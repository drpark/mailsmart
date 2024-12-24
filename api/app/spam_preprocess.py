import spacy
import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class SpamPreprocessor:
    def __init__(self):
        """Initialise le préprocesseur avec le modèle spaCy"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Modèle spaCy chargé avec succès")
        except Exception as e:
            logger.error(
                f"Erreur lors du chargement du modèle spaCy: {str(e)}")
            raise

    def nettoyage_spacy(self, texte: str) -> str:
        """
        Nettoie un texte avec spaCy :
        - Supprime les entités nommées
        - Lemmatise les mots
        - Supprime les stopwords et la ponctuation
        """
        doc = self.nlp(texte)
        cleaned_text = ' '.join([
            token.lemma_ for token in doc
            if not token.is_stop
            and not token.is_punct
            and len(token.text) > 1
            and not token.ent_type_
        ])
        return cleaned_text

    def clean_text(self, text: str) -> str:
        """
        Applique toutes les étapes de prétraitement à un texte
        """
        if not isinstance(text, str):
            return ""

        # Convertir en minuscules
        text = text.lower()

        # Supprimer les chiffres
        text = re.sub(r'\d+', '', text)

        # Supprimer les URLs
        text = re.sub(r'http\S+', '', text)

        # Supprimer les mentions et hashtags
        text = re.sub(r'@\S+|#\S+', '', text)

        # Appliquer le nettoyage spaCy
        return self.nettoyage_spacy(text)

    def get_other_features(self, text: str):
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

        word_count = len(text.split())
        keyword_count = sum(
            1 for word in spam_keywords if word in text.lower())
        keyword_ratio = keyword_count / word_count if word_count > 0 else 0

        promo_word_count = sum(
            1 for word in spam_keywords if word in text.lower())
        promo_word_ratio = keyword_count / word_count if word_count > 0 else 0

        uppercase_ratio = sum(1 for char in text if char.isupper()) / len(text)

        # Retourner toutes les features dans un dictionnaire
        features = {
            'keyword_count': [keyword_count],
            'keyword_ratio': [keyword_ratio],
            'promo_word_count': [promo_word_count],
            'promo_word_ratio': [promo_word_ratio],
            'uppercase_ratio': [uppercase_ratio],

        }

        return features
