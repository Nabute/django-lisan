# google_translate_service.py
# from googletrans import Translator
from lisan.translation_services import BaseTranslationService


class GoogleTranslateService(BaseTranslationService):
    def __init__(self):
        self.translator = lambda a, b: f"{a} in {b}"

    def translate(self, text, target_language):
        return self.translator(text, target_language)
