from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from azure.storage.blob import BlobServiceClient
import os


class Settings(BaseSettings):
    # Variables Azure Storage
    connection_string: str = Field(...,
                                   alias="AZURE_STORAGE_CONNECTION_STRING")
    container_name: str = Field(..., alias="AZURE_STORAGE_CONTAINER_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        extra='allow'
    )


def init_azure_storage():
    """
    Initialise la connexion Azure Storage et retourne le client
    Si la configuration est invalide, lève une exception
    """
    try:
        settings = Settings()

        if not settings.connection_string:
            raise ValueError(
                "Azure Storage connection string is not configured")

        if not settings.container_name:
            raise ValueError("Azure Storage container name is not configured")

        blob_service_client = BlobServiceClient.from_connection_string(
            settings.connection_string
        )
        container_client = blob_service_client.get_container_client(
            settings.container_name
        )

        print(f"Azure Storage initialized successfully")
        return blob_service_client, container_client

    except Exception as e:
        print(f"Failed to initialize Azure Storage: {str(e)}")
        raise


async def download_blob(container_client, blob_name: str, destination_path: str):
    """
    Télécharge un blob depuis Azure Storage
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        with open(destination_path, "wb") as file:
            blob_data = blob_client.download_blob()
            file.write(blob_data.readall())
        return True
    except Exception as e:
        print(f"Error downloading blob {blob_name}: {str(e)}")
        return False


async def upload_blob(container_client, blob_name: str, source_path: str):
    """
    Upload un fichier vers Azure Storage
    """
    try:
        blob_client = container_client.get_blob_client(blob_name)
        with open(source_path, "rb") as file:
            blob_client.upload_blob(file, overwrite=True)
        return True
    except Exception as e:
        print(f"Error uploading blob {blob_name}: {str(e)}")
        return False
