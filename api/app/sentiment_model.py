from app.config.sentry import capture_exception, capture_message
from fastapi import HTTPException
import numpy as np
from transformers import RobertaTokenizer
import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Supprime les avertissements TF
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Désactive les opérations oneDNN
tf.get_logger().setLevel('ERROR')  # Supprime les avertissements TF additionnels


class SentimentModel:
    def __init__(self):
        self.tokenizer = None
        self.emotion_model = None
        self.emotions = ['anger', 'fear', 'joy',
                         'neutral', 'sadness', 'surprise']
        self.load_models()

    def load_models(self):
        try:
            self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            self.emotion_model = tf.saved_model.load('models/emotions')
            # capture_message("Modèle d'émotions chargé avec succès", level="info")
        except Exception as e:
            capture_exception(e)
            raise HTTPException(
                status_code=500, detail="Erreur lors du chargement des modèles")

    def analyze_emotions(self, text: str):
        try:
            # Tokenisation pour RoBERTa
            encodings = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="tf"
            )
            inputs = {
                'input_ids': encodings['input_ids'],
                'attention_mask': encodings['attention_mask'],
                'token_type_ids': encodings.get('token_type_ids', tf.zeros_like(encodings['input_ids']))
            }

            # Prédiction des émotions
            predictions = self.emotion_model(inputs, training=False)
            probs = tf.nn.softmax(predictions['logits'], axis=1)[0].numpy()

            emotion_scores = {emotion: float(
                prob) for emotion, prob in zip(self.emotions, probs)}
            predicted_emotion = self.emotions[np.argmax(probs)]

            return predicted_emotion, emotion_scores

        except Exception as e:
            capture_exception(e, context={"text_length": len(text)})
            raise HTTPException(
                status_code=500, detail="Erreur lors de l'analyse des émotions")
