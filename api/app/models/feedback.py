from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, Float, DateTime, Integer, BigInteger
from sqlalchemy.sql import func
from app.config.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    text = Column(String(2000), nullable=False)
    initial_spam_prediction = Column(Float, nullable=False)
    initial_sentiment_prediction = Column(String(20), nullable=False)
    # Nullable car mise à jour par feedback
    real_spam = Column(Boolean, nullable=True)
    # Nullable car mise à jour par feedback
    real_emotion = Column(String(20), nullable=True)
