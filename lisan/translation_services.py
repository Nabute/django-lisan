class BaseTranslationService:
    """
    A base class for translation services.

    This class defines the interface that all translation service subclasses
    must implement. Specifically, any subclass must provide its own
    implementation of the `translate` method, which will handle translating 
    text to the target language.
    """

    def translate(self, text, target_language):
        """
        Translate the given text to the target language.

        Args:
            text (str): The text to be translated.
            target_language (str): The language code of the target language
                                   for the translation.

        Returns:
            str: The translated text in the target language.

        Raises:
            NotImplementedError: If this method is not overridden by a
            subclass.
        """
        raise NotImplementedError(
            "This method must be overridden by subclasses."
        )
