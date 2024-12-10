from django.conf import settings
from django.db import models, IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from lisan.metaclasses import LisanModelMeta
from lisan.utils import get_translation_service


class LisanModelMixin(models.Model, metaclass=LisanModelMeta):
    """
    A Django model mixin that provides multilingual support for models.

    This mixin allows models to have translations in different languages by
    linking to a corresponding Lisan model. It provides methods to get and
    set translations for different fields based on the language code.
    """

    _current_language = 'en'

    class Meta:
        abstract = True

    def get_lisan(self, language_code=None):
        """
        Retrieve the Lisan (translation) instance for the specified language.

        Args:
            language_code (str): The language code to retrieve the translation
                                 for. Defaults to the current language.

        Returns:
            Model or None: The Lisan model instance for the specified language,
                           or None if not found.
        """
        language_code = language_code or self._current_language
        try:
            filter_kwargs = {
                    "language_code": language_code,
                    f"{self._meta.model_name}": self
                }
            return self.Lisan.objects.filter(**filter_kwargs).first()
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            # Log or handle unexpected exceptions if needed
            raise e

    def set_lisan(self, language_code, **lisan_fields):
        """
        Set or update the Lisan (translation) fields for a specified language.

        Args:
            language_code (str): The language code for the translation.
            lisan_fields (dict): Key-value pairs of field names and their
                                 corresponding values.

        Returns:
            Model: The updated or created Lisan model instance.

        Raises:
            ValueError: If no language code is provided.
            FieldDoesNotExist: If a specified field does not exist in the
                               translation model.
            IntegrityError: If a database integrity issue occurs.
        """
        self._validate_language_code(language_code)

        try:
            with transaction.atomic():
                filter_kwargs = {
                    "language_code": language_code,
                    f"{self._meta.model_name}": self
                }
                lisan = self.Lisan.objects.filter(**filter_kwargs).first()

                if not lisan:
                    # Check if all lisan_fields exist in the model
                    for field_name in lisan_fields.keys():
                        if not hasattr(self.Lisan, field_name):
                            raise FieldDoesNotExist(
                                f"Field '{field_name}' does not exist in the "
                                "translation model."
                            )

                    primary_key_field = getattr(self.Lisan._meta, 'pk', None)
                    if primary_key_field and primary_key_field.name != 'id':
                        primary_key_value = lisan_fields.pop(
                            primary_key_field.name, None)
                    else:
                        primary_key_value = None

                    # Explicitly set the foreign key to self (the instance)
                    # TODO: this is not capturing the UUID for the id
                    lisan = self.Lisan(
                        **lisan_fields,
                        language_code=language_code,
                        **{self._meta.model_name: self}
                    )

                    if primary_key_value is not None:
                        setattr(
                            lisan,
                            primary_key_field.name,
                            primary_key_value
                        )

                    lisan.save()
                else:
                    for field, value in lisan_fields.items():
                        if hasattr(lisan, field):
                            setattr(lisan, field, value)
                        else:
                            raise FieldDoesNotExist(
                                f"Field '{field}' does not exist in the "
                                "translation model."
                            )
                    lisan.save()
                return lisan
        except IntegrityError:
            raise IntegrityError(
                "Failed to set translation due to database integrity issues."
            )
        except FieldDoesNotExist as e:
            raise e
        except Exception as e:
            raise e

    def set_bulk_lisans(self, translations):
        """
        Set or update translations for multiple languages in bulk.

        Args:
            translations (dict): A dictionary where each key is a language
                                code (str) and the corresponding value is a
                                dictionary of fields (dict) to be set or
                                updated for that language.

                                Example:
                                {
                                    'en': {
                                        'field1': 'value1',
                                        'field2': 'value2'
                                    },
                                    'fr': {
                                        'field1': 'valeur1',
                                        'field2': 'valeur2'
                                    }
                                }

        Behavior:
            This method updates the Lisan (translation) model for each
            specified language in bulk. For each language code in the
            `translations` dictionary, the corresponding fields
            and their values are passed to the `set_lisan` method for
            that language.

        Transaction:
            The operation is wrapped in a database transaction to ensure
            that either all translations are successfully updated or none
            of them are (atomic operation).

        Raises:
            Exception: Any exceptions encountered during the transaction
            will cause the entire operation to roll back, ensuring data
            consistency.
        """
        with transaction.atomic():
            for translation in translations:
                language_code = translation.pop("language_code")
                self.set_lisan(language_code, **translation)

    def get_lisan_field(
            self, field_name,
            language_code=None,
            fallback_languages=None,
            auto_translate=False):
        """
        Retrieve a specific field's value from the Lisan (translation) model.

        Args:
            field_name (str): The name of the field to retrieve.
            language_code (str, optional): The language code to retrieve the
                                           field for. Defaults to the current
                                           language if not provided.
            fallback_languages (list, optional): A list of fallback language
                                                 codes to try if the field is
                                                 not found in the specified
                                                 language. Defaults to a list
                                                 of fallback languages set in
                                                 the configuration or ['en'].
            auto_translate (bool, optional): Whether to automatically translate
                                             the field value if it is not found
                                             in the specified language.
                                             Defaults to False.

        Returns:
            Any: The value of the specified field from the Lisan translation
                 model. If the field is not found in any of the provided
                 languages, it returns the default field value from the main
                 model. If `auto_translate` is True, it attempts to translate
                 the value to the requested language if not found.

        Raises:
            AttributeError: If the field does not exist in either the model or
                            its translations.
        """
        language_code = language_code or self._current_language
        fallback_languages = fallback_languages or getattr(
            settings, 'LISAN_FALLBACK_LANGUAGES', ['en']
        )
        # Try to get the field from available translations
        for lang in [language_code] + fallback_languages:
            lisan = self.get_lisan(lang)
            if lisan and hasattr(lisan, field_name):
                return getattr(lisan, field_name)

        # If auto-translation is enabled, use the translation service
        if auto_translate:
            original_text = getattr(self, field_name)
            translation_service = get_translation_service()
            return translation_service.translate(
                original_text, target_language=language_code)

        # Fallback to default field
        return getattr(self, field_name)

    def set_current_language(self, language_code):
        """
        Set the current language for the model instance.

        Args:
            language_code (str): The language code to set as the current
                                 language.

        Raises:
            ValueError: If no language code is provided.
        """
        self._validate_language_code(language_code)
        self._current_language = language_code

    def is_field_translatable(self, field_name):
        """
        Determine if the given field is translatable for this instance.

        Args:
            field_name (str): The name of the field to check for
            translatability.

        Returns:
            bool: True if the field is translatable (i.e., exists in
            `lisan_fields`), False otherwise.

        Behavior:
            This method checks if the specified field is considered
            translatable by verifying its presence in the `lisan_fields`
            attribute. The `lisan_fields` attribute is expected to
            contain a list or set of field names that are marked for
            translation.

        Example:
            >>> instance.is_field_translatable('title')
            True

            >>> instance.is_field_translatable('non_translatable_field')
            False
        """
        return field_name in self.lisan_fields

    def _validate_language_code(self, language_code):
        """
        Validate that the provided language code is valid and supported.

        :param language_code: The language code to validate.
        :raises ValueError: If the language code is not
                            provided or unsupported.
        """
        if not language_code:
            raise ValueError("Language code must be provided")

        # Retrieve default and allowed languages from settings with
        # fallback values
        default_language = getattr(settings, 'LISAN_DEFAULT_LANGUAGE', 'en')
        supported_languages = getattr(
            settings, 'LISAN_ALLOWED_LANGUAGES', [default_language])

        if language_code not in supported_languages:
            raise ValueError(f"Unsupported language code: {language_code}. Supported languages are: {supported_languages}") # noqa
