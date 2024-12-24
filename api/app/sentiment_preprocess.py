from bs4 import BeautifulSoup
import re
import emoji
from fastapi import HTTPException
from app.config.sentry import capture_exception, capture_message


class SentimentPreprocessor:
    def clean_text_for_bert(self, text: str) -> str:
        """
        Fonction de nettoyage pour préparer le texte pour BERT
        Args:
            text: Texte à nettoyer
        Returns:
            str: Texte nettoyé
        """
        try:
            if not isinstance(text, str):
                text = str(text)

            # Convertir en UTF-8
            text = text.encode('utf-8', 'ignore').decode('utf-8')

            # Supprimer les balises HTML
            text = BeautifulSoup(text, "html.parser").get_text()

            # Remplacer les retours à la ligne et tabulations
            text = re.sub(r"[\n\t\r]", " ", text)

            # Supprimer les caractères non pertinents
            text = re.sub(r"[^\w\s.,!?']", "", text)

            # Gérer les emojis
            text = emoji.demojize(text)

            # Limiter les caractères répétitifs
            text = re.sub(r"(.)\1{2,}", r"\1\1", text)

            # Normaliser les espaces
            text = " ".join(text.split())

            capture_message(
                "Text cleaned for BERT",
                level="info",
                context={"original_length": len(
                    text), "cleaned_length": len(text)}
            )

            return text

        except Exception as e:
            capture_exception(
                e,
                context={
                    "text_length": len(text) if isinstance(text, str) else "not_string",
                    "preprocessing_step": "clean_text_for_bert"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Erreur lors du nettoyage du texte pour BERT"
            )
