from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackCreate(BaseModel):
    message_id: int = Field(..., description="ID du message")
    user_id: int = Field(..., description="ID de l'utilisateur")
    text: str = Field(..., description="Texte du message")
    initial_spam_prediction: float = Field(..., ge=0,
                                           le=1, description="Prédiction initiale de spam")
    initial_sentiment_prediction: str = Field(
        ..., description="Prédiction initiale d'émotion")
    real_spam: bool = Field(..., description="Véritable statut de spam")
    real_emotion: str = Field(..., description="Véritable émotion")
