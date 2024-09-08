from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class LisanSerializerMixin(serializers.ModelSerializer):
    """
    A serializer mixin that handles dynamic language translations
    for models that support multi-language fields. This mixin
    adds support for handling translations in POST, PUT, and PATCH
    requests, as well as customizing the serialization output
    based on the requested language.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer, setting up the request context,
        allowed languages, and default language. Also handles the
        addition or removal of dynamic fields based on the request method.
        """
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request', None)
        self.allowed_languages = getattr(
            settings, 'LISAN_ALLOWED_LANGUAGES', ['en']
        )
        self.default_language = getattr(
            settings, 'LISAN_DEFAULT_LANGUAGE', 'en'
        )
        self._handle_dynamic_fields()

    def _handle_dynamic_fields(self):
        """
        Handle the inclusion or exclusion of the 'translations' field
        in the serializer based on the request method. The field is
        added for POST, PUT, and PATCH requests and removed otherwise.
        """
        if self.request and self.request.method in ['POST', 'PUT', 'PATCH']:
            if 'translations' not in self.fields:
                self.fields['translations'] = serializers.ListField(
                    child=serializers.DictField(),
                    write_only=True,
                    required=False
                )
        else:
            self.fields.pop('translations', None)

    def to_representation(self, instance):
        """
        Override the default representation of the instance to include
        language-specific fields based on the requested language. This
        ensures that the correct language data is included in the response.
        """
        representation = super().to_representation(instance)
        language_code = getattr(
            self.request, 'language_code', self.default_language
        )

        # Ensure the language code is within the allowed languages
        if language_code not in self.allowed_languages:
            language_code = self.default_language

        # Modify the representation to include language-specific fields
        if hasattr(instance, 'lisan_fields'):
            for field in instance.lisan_fields:
                if field in representation:
                    representation[field] = instance.get_lisan_field(
                        field, language_code
                    )

        return representation

    def _process_translations(
            self, instance, translations, default_language_code):
        """
        Process and save the translations for each language provided
        in the translations list. This method updates the instance with
        language-specific data.

        Args:
            instance: The model instance being created or updated.
            translations: A list of translation dictionaries containing
                          language_code and field data.
            default_language_code: The default language code to use if
                                   none is provided in a translation.
        """
        for translation in translations:
            lang_code = translation.pop('language_code', None)
            if lang_code:
                lisan_data = {
                    field: translation.get(field)
                    for field in instance.lisan_fields
                    if translation.get(field) is not None
                }
                if lisan_data:
                    instance.set_lisan(lang_code, **lisan_data)

    def create(self, validated_data):
        """
        Create a new instance of the model, handling any translations
        provided in the validated data. The translations are processed
        and saved separately after the main instance is created.

        Args:
            validated_data: The data that has been validated and is ready
                            for creating a new model instance.

        Returns:
            The newly created model instance.
        """
        translations = validated_data.pop('translations', [])
        self._validate_translations(translations)
        language_code = getattr(
            self.request, 'language_code', self.default_language
        )

        # Ensure the language code is within allowed languages
        if language_code not in self.allowed_languages:
            language_code = self.default_language

        # Create the main instance
        instance = super().create(validated_data)
        lisan_fields = {
            field: validated_data.get(field)
            for field in self.Meta.model.lisan_fields
        }
        instance.set_lisan(language_code, **lisan_fields)

        # Process and save the translations
        self._process_translations(instance, translations, language_code)

        return instance

    def update(self, instance, validated_data):
        """
        Update an existing instance of the model, handling any translations
        provided in the validated data. The translations are processed and
        saved separately after the main instance is updated.

        Args:
            instance: The existing model instance being updated.
            validated_data: The data that has been validated and is ready
                            for updating the model instance.

        Returns:
            The updated model instance.
        """
        translations = validated_data.pop('translations', [])
        self._validate_translations(translations, partial=True)
        language_code = getattr(
            self.request, 'language_code', self.default_language
        )

        # Ensure the language code is within allowed languages
        if language_code not in self.allowed_languages:
            language_code = self.default_language

        # Update the main instance with non-translation fields
        instance = super().update(instance, validated_data)

        # Process and save the translations
        for translation in translations:
            lang_code = translation.get('language_code', language_code)

            # Only include fields that are present in the translation
            lisan_fields = {
                field: translation[field]
                for field in self.Meta.model.lisan_fields
                if field in translation
            }

            if lisan_fields:
                instance.set_lisan(lang_code, **lisan_fields)

        return instance

    def _validate_translations(self, translations, partial=False):
        """
        Validate that the translations contain all required languages and
        fields. This method ensures that each translation includes a
        language_code and that all necessary fields are present for each
        translation.

        Args:
            translations: A list of dictionaries containing translation data.
            partial: A boolean indicating whether the validation is for a
                     partial update (PATCH) or a full update/creation.

        Raises:
            ValidationError: If any required language or field is missing, or
                             if an unsupported language code is provided.
        """
        if not translations:
            raise ValidationError("Translations are required.")

        translation_languages = {
            translation['language_code'] for translation in translations
        }
        missing_languages = set(self.allowed_languages) - translation_languages

        if missing_languages and not partial:
            raise ValidationError(
                "Missing translations for languages: "
                f"{', '.join(missing_languages)}"
            )

        for translation in translations:
            lang_code = translation.get('language_code')
            if lang_code not in self.allowed_languages:
                raise ValidationError(
                    f"Unsupported language code: {lang_code}"
                )

            if not partial:
                missing_fields = set(
                    self.Meta.model.lisan_fields
                ) - translation.keys()
                if missing_fields:
                    raise ValidationError(
                        f"Missing fields for {lang_code}: "
                        f"{', '.join(missing_fields)}"
                    )
