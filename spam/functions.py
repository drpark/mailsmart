import spacy
import pandas as pd
import re
from tqdm import tqdm
from spacy.cli import download
# Charger le modèle spaCy pour l'anglais
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Le modèle 'en_core_web_sm' n'est pas installé. Téléchargement en cours...")
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Traitement spaCy du texte


def nettoyage_spacy(texte):
    """
    Fait le nettoyage d'un texte en enlevant les mots vides, les ponctuations, les noms propres, et en lemmatisant les mots.
    :param texte: Texte à nettoyer
    :return: Texte nettoyé
    """
    doc = nlp(texte)

    cleaned_text = ' '.join([token.lemma_ for token in doc  # Lemmatisation
                            if not token.is_stop  # Pas un stopword
                            and not token.is_punct  # Pas de ponctuation
                            # Pas de mots de longueur 1 (a, I, etc.)
                             and len(token.text) > 1
                             and not token.ent_type_])  # Pas de noms propres

    return cleaned_text


# nettoyer texte avec spacy
def nettoyer_texte(df, col_name):

    tqdm.pandas(desc="Nettoyage des messages")

    # Supprimer les NaN et convertir en chaine
    df = df.dropna(subset=[col_name])
    # df.loc[:, col_name] sinon alerte pandas qui veut etre sur qu'on applique la fonction sur toute la colonne
    df.loc[:, col_name] = df[col_name].astype(str)

    # minuscules
    df.loc[:, col_name] = df[col_name].str.lower()

    # Supprimer chiffres
    df.loc[:, col_name] = df[col_name].apply(lambda x: re.sub(r'\d+', '', x))

    # Supprimer URLs
    df.loc[:, col_name] = df[col_name].apply(
        lambda x: re.sub(r'http\S+', '', x))

    # Supprimer les mentions et hashtags
    df.loc[:, col_name] = df[col_name].apply(
        lambda x: re.sub(r'@\S+|#\S+', '', x))

    # Supprimer les chaînes bizarres ï¿½ï¿
    df.loc[:, col_name] = df[col_name].str.replace("ï¿½ï¿", "", regex=False)

    # Supprimer les retours à la ligne (\n)
    df.loc[:, col_name] = df[col_name].str.replace("\n", "", regex=False)

    # Appliquersur col_name
    df.loc[:, col_name] = df[col_name].progress_apply(nettoyage_spacy)

    return df


# ajouter des features
def add_features(df):
    # Supprimer les NaN dans la colonne 'message'
    df = df.dropna(subset=['message']).reset_index(drop=True)

    # Convertir toutes les valeurs en chaînes
    df['message'] = df['message'].astype(str)

    df['message_length'] = df['message'].apply(len)  # longueur du message
    df['word_count'] = df['message'].apply(lambda x: len(x.split()))
    df['special_char_count'] = df['message'].apply(
        lambda x: sum(1 for char in x if char in '@#$%&*'))

    spam_keywords = [
        # Arnaques financières et offres
        'cash', 'free', 'prize', 'winning', 'congratulations', 'claim', 'bonus', 'money',
        'offer', 'pay', 'investment', 'earnings', 'discount', 'credit card', 'no cost',
        'payday loan', 'save money', 'get rich', 'lottery', 'winner', 'payment', 'guarantee',
        'risk-free', 'bank account', 'deposit', 'withdraw', 'refund', 'fund transfer',
        'deposit now', 'instant win', 'cash prize',

        # Liens douteux / Mots relatifs à l'escroquerie
        'click here', 'visit our website', 'you won’t believe', 'just for you', 'act now',
        'now or never', 'limited time offer', 'call now', 'don\'t miss out', 'urgent',
        'hurry', 'immediate action required', 'attention', 'final notice', 'unsolicited offer',
        'no obligation',

        # Produits illégaux et services douteux
        'viagra', 'cialis', 'prescription drugs', 'weight loss', 'herbal pills', 'pharmacy',
        'enhancement', 'medical treatment', 'fast results', 'fake watches', 'fake merchandise',
        'counterfeit', 'replica', 'online pharmacy', 'bodybuilding', 'diet pills', 'natural remedies',

        # Arnaques à l'investissement et à la crypto-monnaie
        'bitcoin', 'cryptocurrency', 'ethereum', 'altcoin', 'ico', 'investment opportunity',
        'trade now', 'financial freedom', 'secure your future', 'diversify your portfolio',
        'multi-level marketing', 'pyramid scheme', 'ponzi scheme', 'passive income',

        # Phishing (vol d'identité)
        'account verification', 'login', 'reset password', 'suspicious activity', 'please verify',
        'your account is suspended', 'account update', 'login immediately', 'confirm your details',
        'immediate action required', 'verify now', 'suspended account',

        # Phrases courantes de spam
        'make money fast', 'earn money online', 'work from home', 'easy money', 'no strings attached',
        'no hidden fees', 'you’ve been selected', 'don\'t miss out', 'act fast', 'call now for a free trial',
        'free gift', 'unclaimed prize', 'you\'ve been approved', 'immediate response needed',

        # Arnaques sur les dates et les voyages
        'vacation', 'trip', 'free holiday', 'getaway', 'resort', 'free flight', 'discounted hotels',
        'luxury vacation', 'trip of a lifetime', 'vacation package', 'last minute deal', 'travel offer',
        'special offer',

        # Autres mots-clés communs
        'adult', 'porn', 'gambling', 'adult content', 'spam', 'fake', 'unsubscribe', 'malware',
        'virus', 'download', 'trojan', 'phishing', 'risky download'
    ]

    df['keyword_count'] = df['message'].apply(lambda x: sum(
        1 for word in spam_keywords if word in x.lower()))
    df['keyword_ratio'] = df['keyword_count'] / df['word_count']
    df['url_count'] = df['message'].apply(
        lambda x: len(re.findall(r'http[s]?://', x)))

    promo_words = [
        # Offres et promotions
        'offer', 'discount', 'sale', 'deal', 'coupon', 'voucher', 'free', 'save',
        'promo', 'limited time', 'special offer', 'clearance', 'exclusive', 'bargain',
        'bundle', 'flash sale', 'buy one get one', 'free shipping', 'exclusive deal',
        'unbeatable price', 'offer expires', 'today only', 'final sale', 'price drop',
        'price cut', 'special discount', 'best deal', 'end of season sale', 'mega sale',
        'big savings', 'limited time offer', 'save up to', 'super sale', 'hot deal',

        # Produits et services en promotion
        'free trial', 'buy now', 'get started', 'limited stock', 'hot item', 'best seller',
        'new release', 'must-have', 'featured product', 'limited edition', 'exclusive product',
        'top rated', 'limited quantity', 'best value', 'new arrival', 'just for you',
        'special price', 'limited time deal', 'seasonal offer', 'hot pick', 'high demand',

        # Termes associés aux avantages
        'bonus', 'gift', 'reward', 'thank you gift', 'free gift', 'surprise gift',
        'gift card', 'loyalty program', 'rewards', 'exclusive access', 'premium access',
        'early bird', 'VIP', 'gold member', 'bronze member', 'platinum member', 'premium',
        'complimentary', 'members only', 'priority access', 'personalized', 'extra benefits',

        # Appels à l'action
        'buy now', 'shop now', 'get yours', 'order now', 'claim your', 'sign up', 'subscribe now',
        'join now', 'click here', 'act fast', 'get yours today', 'register now', 'grab it now',
        'don’t miss out', 'get started', 'limited offer', 'click to claim', 'add to cart',
        'hurry', 'now or never', 'act quickly', 'exclusive access', 'get your discount',

        # Mots relatifs à l'urgence
        'hurry', 'limited time', 'last chance', 'ending soon', 'only a few left', 'only today',
        'expiring soon', 'ending today', 'time is running out', 'closing soon', 'don’t wait',
        'act fast', 'rush', 'quick', 'now', 'only hours left', 'final hours', 'only minutes left',

        # Réductions et offres spéciales
        'clearance sale', 'blowout sale', 'half price', 'discounted', 'price drop', 'half off',
        'flash sale', 'buy one get one free', 'limited time discount', 'save big', 'final markdown',
        'hot deal', 'massive discount', 'special deal', 'unbeatable price', 'low price',
        'huge savings', 'lowest price', 'cut prices', 'discounts available', 'bulk discount',
        'price slash', 'mega savings', 'one-time offer', 'special savings', 'today’s deal',

        # Livraison et services associés
        'free shipping', 'free delivery', 'fast shipping', 'same day delivery', 'expedited shipping',
        'next day delivery', 'international shipping', 'worldwide shipping', 'free return',
        'satisfaction guaranteed', 'no hidden fees', 'easy returns', 'return policy', 'free return shipping',

        # Mentions de période de promotion
        'Black Friday', 'Cyber Monday', 'Christmas Sale', 'New Year Sale', 'Holiday Discount',
        'Summer Sale', 'Spring Offer', 'Back to School Sale', 'End of Year Sale', 'Seasonal Sale',
        'Big Sale', 'Weekend Special', 'Flash Discount', 'Holiday Shopping', 'Easter Sale',
        'Fall Offer', 'Thanksgiving Deal', 'Boxing Day Sale', 'Valentine’s Day Sale'
    ]
    df['promo_word_count'] = df['message'].apply(
        lambda x: sum(1 for word in promo_words if word in x.lower()))
    df['promo_word_ratio'] = df['promo_word_count'] / df['word_count']
    df['letter_digit_ratio'] = df['message'].apply(lambda x: len([c for c in x if c.isalpha(
    )]) / len([c for c in x if c.isdigit()]) if len([c for c in x if c.isdigit()]) > 0 else 0)
    pronouns = [
        # Pronoms personnels sujets
        'I', 'you', 'he', 'she', 'it', 'we', 'they',  # Singulier et pluriel

        # Pronoms personnels objets
        'me', 'you', 'him', 'her', 'it', 'us', 'them',

        # Pronoms possessifs
        'my', 'your', 'his', 'her', 'its', 'our', 'their',

        # Pronoms réfléchis
        'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'yourselves', 'themselves',

        # Pronoms démonstratifs
        'this', 'that', 'these', 'those',

        # Pronoms indéfinis
        'everyone', 'someone', 'anyone', 'no one', 'nothing', 'everything', 'anything', 'everybody', 'somebody', 'anybody', 'nobody',

        # Pronoms interrogatifs
        'who', 'whom', 'whose', 'which', 'what',

        # Pronoms relatifs
        'who', 'whom', 'whose', 'which', 'that'
    ]
    df['pronoun_count'] = df['message'].apply(
        lambda x: sum(1 for word in pronouns if word in x.lower()))
    df['uppercase_ratio'] = df['message'].apply(
        lambda x: sum(1 for char in x if char.isupper()) / len(x))
    return df


def remove_short_messages(df, col_name='message', min_length=50):
    df_cleaned = df[df[col_name].apply(lambda x: len(x) >= min_length)]
    return df_cleaned
