import re
from bs4 import BeautifulSoup
import re
import emoji


def nettoyer_avant_bert(text):

    # Convertir en UTF-8
    text = text.encode('utf-8', 'ignore').decode('utf-8')

    # Supprimer les balises HTML
    text = BeautifulSoup(text, "html.parser").get_text()

    # Remplacer les retours à la ligne et tabulations
    text = re.sub(r"[\n\t\r]", " ", text)

    # Supprimer les caractères non pertinents
    # text = re.sub(r"[^\w\s.,!?']", "", text)

    # Gérer les emojis
    text = emoji.demojize(text)  # Remplace 😊 par ":smile:"

    # Limiter les caractères répétitifs
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)  # Réduit "coooool" à "cool"

    # Normaliser les espaces
    text = " ".join(text.split())

    return text
