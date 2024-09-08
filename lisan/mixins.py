from django.db import models, IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from .metaclasses import LisanModelMeta


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
            return self.lisans.filter(language_code=language_code).first()
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
        if not language_code:
            raise ValueError("Language code must be provided")

        try:
            with transaction.atomic():
                lisan = self.lisans.filter(
                    language_code=language_code
                ).first()

                if not lisan:
                    # Check if all lisan_fields exist in the model
                    for field_name in lisan_fields.keys():
                        if not hasattr(self.Lisan, field_name):
                            raise FieldDoesNotExist(
                                f"Field '{field_name}' does not exist in the "
                                "translation model."
                            )

                    # Explicitly set the foreign key to self (the instance)
                    lisan = self.Lisan(
                        **lisan_fields,
                        language_code=language_code,
                        **{self._meta.model_name: self}
                    )
                    lisan.save()
                    self.lisans.add(lisan)
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

    def get_lisan_field(
        self, field_name, language_code=None, fallback_to_default=True
    ):
        """
        Retrieve a specific field's value from the Lisan (translation) model.

        Args:
            field_name (str): The name of the field to retrieve.
            language_code (str): The language code to retrieve the field for.
                                 Defaults to the current language.
            fallback_to_default (bool): Whether to fallback to the default
                                        language ('en') if the field is not
                                        found in the specified language.
                                        Defaults to True.

        Returns:
            Any: The value of the specified field.

        Raises:
            AttributeError: If the field does not exist in either the model or
                            its translations.
        """
        language_code = language_code or self._current_language
        try:
            lisan = self.get_lisan(language_code)
            if lisan and hasattr(lisan, field_name):
                return getattr(lisan, field_name)
            elif fallback_to_default:
                default_lisan = self.get_lisan('en')
                if default_lisan and hasattr(default_lisan, field_name):
                    return getattr(default_lisan, field_name)
            return getattr(self, field_name)
        except AttributeError:
            raise AttributeError(
                f"Field '{field_name}' does not exist in either the model or "
                "its translations."
            )
        except Exception as e:
            raise e

    def set_current_language(self, language_code):
        """
        Set the current language for the model instance.

        Args:
            language_code (str): The language code to set as the current
                                 language.

        Raises:
            ValueError: If no language code is provided.
        """
        if not language_code:
            raise ValueError("Language code must be provided")
        self._current_language = language_code
