# app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class DatabaseSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='allow'  # Permet les variables supplémentaires dans le .env
    )

    @property
    def DATABASE_URL(self) -> str:
        # Utilisation de PyMySQL comme connecteur
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


try:
    # Initialisation des paramètres de la base de données
    settings = DatabaseSettings()

    # Création du moteur de base de données
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20
    )

    # Création du SessionLocal
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

except Exception as e:
    print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")
    raise

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction pour obtenir une session de base de données


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
