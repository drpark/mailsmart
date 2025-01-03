import spacy
import pandas as pd
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import emoji

# Charger le modèle spaCy pour l'anglais
nlp = spacy.load("en_core_web_sm")
def nettoyage_spacy(texte):
        """
        Fonction de nettoyage d'un texte individuel avec spaCy :
        - Supprimer les entités nommées
        - Lemmatisation des mots
        - Suppression des stopwords
        - Suppression de la ponctuation
        - Suppression des mots de taille 1 (par ex. "a", "I")
        """
        # Traitement spaCy du texte
        doc = nlp(texte)
        
        # Filtrer les tokens : 
        # - garder les mots lemmatisés (représentation de base du mot)
        # - ignorer les stopwords, la ponctuation, les entités nommées et les petits mots
        cleaned_text = ' '.join([token.lemma_ for token in doc 
                                if not token.is_stop  # Pas un stopword
                                and not token.is_punct  # Pas de ponctuation
                                and len(token.text) > 1  # Pas de mots de longueur 1
                                and not token.ent_type_])  # Pas d'entités nommées
        
        return cleaned_text

def nettoyer_texte(df, col_name):

    
    tqdm.pandas(desc="Nettoyage et tokenisation des messages")
    
    # Étape 1 : Supprimer les NaN par des chaînes vides
    df[col_name] = df[col_name].dropna()

    # Étape 2 : Convertir le texte en minuscules
    df[col_name] = df[col_name].str.lower()

    # Étape 4 : Supprimer les chiffres
    df[col_name] = df[col_name].apply(lambda x: re.sub(r'\d+', '', x))

    # Étape 5 : Supprimer les URLs
    df[col_name] = df[col_name].apply(lambda x: re.sub(r'http\S+', '', x))

    # Étape 6 : Supprimer les mentions et hashtags
    df[col_name] = df[col_name].apply(lambda x: re.sub(r'@\S+|#\S+', '', x))

    
      # Appliquer le nettoyage à la colonne spécifiée
    df[col_name] = df[col_name].progress_apply(nettoyage_spacy)
    
    return df   


