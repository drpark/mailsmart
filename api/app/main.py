from azure.storage.blob import BlobServiceClient
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from app.language_service import LanguageService
from app.sentiment_preprocess import SentimentPreprocessor
from app.spam_preprocess import SpamPreprocessor
from app.sentiment_model import SentimentModel
from app.spam_model import SpamModel
from app.models.feedback import Message
from app.models.schemas import FeedbackCreate
from app.config.database import get_db, engine, Base
from sqlalchemy.orm import Session, sessionmaker
import pandas as pd
from app.config.sentry import init_sentry, capture_exception, capture_message
from app.config.azure import init_azure_storage
from fastapi import FastAPI, HTTPException, Depends, status
import os
import signal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


init_sentry()


class ServicesContainer:
    language_service: LanguageService | None = None
    sentiment_preprocessor: SentimentPreprocessor | None = None
    spam_preprocessor: SpamPreprocessor | None = None
    sentiment_model: SentimentModel | None = None
    spam_model: SpamModel | None = None

    def initialize(self):
        self.language_service = LanguageService()
        self.sentiment_preprocessor = SentimentPreprocessor()
        self.spam_preprocessor = SpamPreprocessor()
        self.sentiment_model = SentimentModel()
        self.spam_model = SpamModel()


class TextInput(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    text: str
    detected_language: str
    translated_text: Optional[str]
    emotion: str
    emotion_scores: Dict[str, float]
    spam_score: float
    is_spam: bool


app = FastAPI(
    title="Mailsmart API",
    description="API pour detecter emotions et spam",
    version="1.0.12"
)

services = ServicesContainer()


@app.on_event("startup")
async def startup_event():
    # S'assure que les modèles sont téléchargés avant tout
    models_ready = await download_models()
    if not models_ready:
        raise Exception("Échec du téléchargement des modèles")

    # Initialisation des services seulement après le téléchargement des modèles
    init_services()


def init_services():
    """Initialise tous les services qui dépendent des modèles"""

    # Initialisation des services
    services.initialize()


@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: TextInput):
    """Analyse un texte pour détecter les émotions et le spam"""
    try:
        # 1. Détection de langue et traductions
        detected_lang, translated_text = services.language_service.process_text(
            input_data.text)
        capture_message("Language processed", context={"lang": detected_lang})

        # 2. Prétraitement pour les émotions (BERT)
        text_for_emotion = services.sentiment_preprocessor.clean_text_for_bert(
            translated_text)
        capture_message("Text preprocessed for emotions")

        # 3. Prétraitement pour le spam
        df = pd.DataFrame(
            services.spam_preprocessor.get_other_features(translated_text))
        df['message'] = services.spam_preprocessor.clean_text(translated_text)
        capture_message("Text preprocessed for spam")

        # 4. Analyse des émotions
        emotion, emotion_scores = services.sentiment_model.analyze_emotions(
            text_for_emotion)
        capture_message("Emotions analyzed", context={"emotion": emotion})

        # 5. Analyse du spam

        spam_score, is_spam = services.spam_model.analyze_spam(df)
        capture_message("Spam analyzed", context={"is_spam": is_spam})

        return PredictionResponse(
            text=input_data.text,
            detected_language=detected_lang,
            translated_text=translated_text if detected_lang != 'en' else None,
            emotion=emotion,
            emotion_scores=emotion_scores,
            spam_score=spam_score,
            is_spam=is_spam
        )

    except Exception as e:
        capture_exception(e, context={"input_text": input_data.text[:200]})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def create_or_update_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Crée ou met à jour un feedback utilisateur
    """
    try:
        # Vérifier que l'émotion est valide
        valid_emotions = ['anger', 'fear', 'joy',
                          'neutral', 'sadness', 'surprise']
        if feedback.real_emotion not in valid_emotions:
            raise HTTPException(
                status_code=400,
                detail=f"Emotion invalide. Valeurs possibles: {', '.join(valid_emotions)}"
            )

        # Vérifier si le message existe déjà
        existing_message = db.query(Message).filter(
            Message.id == feedback.message_id).first()

        if existing_message:
            # Mise à jour du message existant
            existing_message.user_id = feedback.user_id
            existing_message.text = feedback.text
            existing_message.initial_spam_prediction = feedback.initial_spam_prediction
            existing_message.initial_sentiment_prediction = feedback.initial_sentiment_prediction
            existing_message.real_spam = feedback.real_spam
            existing_message.real_emotion = feedback.real_emotion
            action = "updated"
        else:
            # Création d'un nouveau message
            new_message = Message(
                id=feedback.message_id,
                user_id=feedback.user_id,
                text=feedback.text,
                initial_spam_prediction=feedback.initial_spam_prediction,
                initial_sentiment_prediction=feedback.initial_sentiment_prediction,
                real_spam=feedback.real_spam,
                real_emotion=feedback.real_emotion
            )
            db.add(new_message)
            action = "created"

        db.commit()

        capture_message(
            f"Feedback {action}",
            level="info",
            context={
                "message_id": feedback.message_id,
                "user_id": feedback.user_id,
                "action": action
            }
        )

        return {
            "status": "success",
            "message": f"Feedback {action} successfully",
            "action": action
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        capture_exception(e)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement du feedback: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def download_models():
    try:
        # Supprimer le répertoire models s'il existe
        import shutil
        if os.path.exists('models'):
            print("Suppression du répertoire models existant...")
            shutil.rmtree('models')
            print("✓ Répertoire models supprimé")

        _, container_client = init_azure_storage()
        downloaded_files = []

        # Lister tous les blobs dans le container
        blobs = container_client.list_blobs()

        for blob in blobs:
            try:
                # Vérifier si c'est un "dossier" (se termine par /)
                if blob.name.endswith('/') or '.' not in blob.name.split('/')[-1]:
                    # C'est un dossier, on le crée simplement
                    os.makedirs(blob.name, exist_ok=True)
                    print(f"✓ Dossier créé: {blob.name}")
                    continue

                # C'est un fichier, on le télécharge
                local_path = blob.name
                print(f"Téléchargement de {blob.name} vers {local_path}")

                # Créer le dossier parent si nécessaire
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Télécharger le fichier par morceaux
                blob_client = container_client.get_blob_client(blob.name)
                with open(local_path, "wb") as f:
                    stream = blob_client.download_blob()
                    CHUNK_SIZE = 1024 * 1024  # 1MB par chunk
                    for chunk in stream.chunks():
                        f.write(chunk)

                downloaded_files.append(local_path)
                print(f"✓ Fichier téléchargé: {local_path}")

            except Exception as e:
                error_msg = f"Erreur lors du téléchargement de {blob.name}: {str(e)}"
                print(error_msg)
                capture_message(error_msg, level="error")
                continue

        if downloaded_files:
            success_msg = f"\nTéléchargement terminé. {len(downloaded_files)} fichiers téléchargés."
            print(success_msg)
            capture_message(success_msg)
            return True
        else:
            raise Exception("Aucun fichier n'a été téléchargé")

    except Exception as e:
        error_message = f"Erreur lors du téléchargement des modèles: {str(e)}"
        print(error_message)
        capture_message(error_message, level="error")
        return False
