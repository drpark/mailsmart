import joblib
from fastapi import HTTPException
from app.config.sentry import capture_exception, capture_message
import numpy as np


class SpamModel:
    def __init__(self):
        """Initialise le modèle de détection de spam"""
        self.spam_model = None
        self.load_model()

    def load_model(self):
        """Charge le modèle de spam"""
        try:
            # contient le pipeline
            self.spam_model = joblib.load('models/spam.joblib')
            # capture_message("Modèle de spam chargé avec succès", level="info")
        except Exception as e:
            capture_exception(e)
            raise HTTPException(
                status_code=500, detail="Erreur lors du chargement du modèle de spam")

    def analyze_spam(self, df) -> tuple[float, bool]:
        """
        Analyse si un texte est un spam
        Args:
            df: Dataframe avec le text nettoyé, lemmatisé + les features
        Returns:
            tuple: (score de spam, booléen indiquant si c'est un spam)
        """
        try:

            # Prédiction
            spam_prob = self.spam_model.predict_proba(df)[0][1]
            # je ne souhaite pas que les mails sur la médiane soient considérés comme spam
            is_spam = spam_prob > 0.75

            return float(spam_prob), bool(is_spam)

        except Exception as e:
            capture_exception(
                e, context={"text_length": len(df['message'])})
            raise HTTPException(
                status_code=500, detail="Erreur lors de l'analyse du spam")
