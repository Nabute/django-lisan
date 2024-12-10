from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class TranslationSerializer(serializers.Serializer):
    """
    Serializer for each translation entry, containing a
    language code and the translatable fields.
    """
    language_code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        # Dynamically add fields based on `lisan_fields`
        # provided by the main model
        lisan_fields = kwargs.pop('lisan_fields', [])
        super().__init__(*args, **kwargs)

        for field in lisan_fields:
            self.fields[field] = serializers.CharField(
                allow_blank=True, required=False)


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

        # Initialize `translations` with the nested
        # serializer for each language entry
        self.fields['translations'] = serializers.ListSerializer(
            child=TranslationSerializer(
                lisan_fields=getattr(self.Meta.model, 'lisan_fields', [])),
            required=False,
            write_only=True
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
                self.fields['translations'] = serializers.ListSerializer(
                    child=TranslationSerializer(
                        lisan_fields=getattr(
                            self.Meta.model, 'lisan_fields', [])),
                    required=False,
                    write_only=True
                )
        else:
            self.fields.pop('translations', None)

    def to_representation(self, instance):
        """
        Override the default representation of the instance to include
        language-specific fields based on the requested language.
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

        # Add structured `translations` with data for each language
        translations_representation = []
        for lang_code in self.allowed_languages:
            translation_data = {'language_code': lang_code}
            for field in instance.lisan_fields:
                translation_data[field] = instance.get_lisan_field(
                    field, lang_code)
            translations_representation.append(translation_data)

        representation['translations'] = translations_representation
        return representation

    def create(self, validated_data):
        """
        Create a new instance of the model, handling any translations
        provided in the validated data. The translations are processed
        and saved separately after the main instance is created.
        """
        translations = validated_data.pop('translations', [])
        self._validate_translations(translations)
        language_code = getattr(
            self.request, 'language_code', self.default_language
        )

        # Ensure the language code is within allowed languages,
        if language_code not in self.allowed_languages:
            # eventhought it's hard to reach here
            language_code = self.default_language

        # Create the main instance
        instance = super().create(validated_data)
        instance.set_bulk_lisans(translations)

        return instance

    def update(self, instance, validated_data):
        """
        Update an existing instance of the model, handling any translations
        provided in the validated data. The translations are processed and
        saved separately after the main instance is updated.
        """
        translations = validated_data.pop('translations', [])
        self._validate_translations(translations, partial=True)
        language_code = getattr(
            self.request, 'language_code', self.default_language
        )

        # Ensure the language code is within allowed languages
        if language_code not in self.allowed_languages:
            # eventhought it's hard to reach here
            language_code = self.default_language

        # Track translatable fields updated in the main model
        translatable_updates = {
            field: validated_data[field]
            for field in self.Meta.model.lisan_fields
            if field in validated_data
        }

        # Update the main instance with non-translation fields
        instance = super().update(instance, validated_data)

        # Synchronize updated translatable fields with the default
        # language translation
        if translatable_updates:
            instance.set_lisan(language_code, **translatable_updates)

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
        """
        if not translations:
            # Skip translation validation for partial updates
            # if no translation data is provided
            if not partial:
                raise ValidationError("Translations are required.")
            return

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
