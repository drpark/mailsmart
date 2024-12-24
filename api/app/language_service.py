from deep_translator import GoogleTranslator
from langdetect import detect
from fastapi import HTTPException
from app.config.sentry import capture_exception, capture_message


class LanguageService:
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            detected_lang = detect(text)
            capture_message("Language detected", level="info",
                            context={"lang": detected_lang})
            return detected_lang
        except:
            capture_message(
                "Language detection failed, defaulting to English", level="warning")
            return 'en'

    @staticmethod
    def translate_to_english(text: str, source_lang: str) -> str:
        if source_lang == 'en':
            return text

        try:
            translator = GoogleTranslator(source=source_lang, target='en')
            translated_text = translator.translate(text)
            capture_message("Translations successful"+" : " +
                            translated_text, level="info")
            return translated_text
        except Exception as e:
            capture_exception(e, context={"source_lang": source_lang})
            raise HTTPException(
                status_code=500, detail="Erreur lors de la traduction")

    def process_text(self, text: str) -> tuple[str, str]:
        detected_lang = self.detect_language(text)
        translated_text = self.translate_to_english(
            text, detected_lang) if detected_lang != 'en' else text
        return detected_lang, translated_text
