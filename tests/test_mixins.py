from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from tests.models import TestModel
from unittest.mock import patch


class TestLisanModelMixin(TestCase):
    """
    Test suite for the LisanModelMixin class, which provides multilingual
    support for Django models.
    """

    def setUp(self):
        """
        Set up the test environment. Create a test model instance and
        translations for testing.
        """
        self.instance = TestModel.objects.create(
            title="Hello World",
            description="Sample description"
        )
        self.instance.set_lisan('am', title="ሰላም ለዓለም", description="ምሳሌ መግለጫ")
        self.instance.set_lisan('tg', title="ሰላም ዓለም")

    def test_get_lisan_existing_language(self):
        """
        Test retrieving a translation (Lisan) for an existing language.
        """
        lisan = self.instance.get_lisan('am')
        self.assertIsNotNone(lisan)
        self.assertEqual(lisan.title, "ሰላም ለዓለም")
        self.assertEqual(lisan.description, "ምሳሌ መግለጫ")

    def test_get_lisan_nonexistent_language(self):
        """
        Test retrieving a translation (Lisan) for a non-existent language.
        """
        lisan = self.instance.get_lisan('fr')
        self.assertIsNone(lisan)

    def test_set_lisan_new_language(self):
        """
        Test setting a translation for a new language.
        """
        lisan = self.instance.set_lisan(
            'or', title="Nagaa Addunyaa", description="Miseensa fakkeessaa")
        self.assertEqual(lisan.title, "Nagaa Addunyaa")
        self.assertEqual(lisan.description, "Miseensa fakkeessaa")

    def test_set_lisan_update_existing(self):
        """
        Test updating an existing translation for a language.
        """
        self.instance.set_lisan('am', title="አዲስ ሰላም")
        lisan = self.instance.get_lisan('am')
        self.assertEqual(lisan.title, "አዲስ ሰላም")
        self.assertEqual(lisan.description, "ምሳሌ መግለጫ")  # Unchanged field

    def test_set_lisan_invalid_field(self):
        """
        Test setting a translation with a field that does not exist.
        """
        with self.assertRaises(FieldDoesNotExist):
            self.instance.set_lisan('am', non_existent_field="Invalid")

    def test_set_lisan_invalid_language_code(self):
        """
        Test setting a translation with an unsupported language code.
        """
        with self.assertRaises(ValueError):
            self.instance.set_lisan('xx', title="Unsupported Language")

    def test_set_bulk_lisans(self):
        """
        Test setting translations in bulk for multiple languages.
        """
        translations = [
            {
                "language_code": "or",
                "title": "Nagaa Addunyaa",
                "description": "Fakkeenya"
            },
            {
                "language_code": "am",
                "title": "አስደሳች ጉዞ",
                "description": "በማይታወቁ መሬቶች ላይ አስገራሚ ጉዞ."
            }
        ]
        self.instance.set_bulk_lisans(translations)

        am_translation = self.instance.get_lisan('am')
        or_translation = self.instance.get_lisan('or')

        self.assertEqual(am_translation.title, "አስደሳች ጉዞ")
        self.assertEqual(or_translation.title, "Nagaa Addunyaa")
        self.assertEqual(or_translation.description, "Fakkeenya")

    def test_get_lisan_field_existing_language(self):
        """
        Test retrieving a field's value for an existing translation.
        """
        title = self.instance.get_lisan_field('title', 'am')
        self.assertEqual(title, "ሰላም ለዓለም")

    def test_get_lisan_field_with_fallback(self):
        """
        Test retrieving a field's value with fallback languages.
        """
        title = self.instance.get_lisan_field(
            'title', 'fr', fallback_languages=['tg'])
        self.assertEqual(title, "ሰላም ዓለም")

    def test_get_lisan_field_auto_translate(self):
        """
        Test retrieving a field's value with auto-translation enabled.
        """
        with patch('lisan.utils.get_translation_service') as mock_service:
            mock_service.return_value = "Bonjour le monde"  # noqa
            title = self.instance.get_lisan_field(
                'title', 'fr', auto_translate=True)
            self.assertEqual(title, f"{self.instance.title} in fr")

    def test_set_current_language(self):
        """
        Test setting the current language for the model instance.
        """
        self.instance.set_current_language('am')
        self.assertEqual(self.instance._current_language, 'am')

    def test_set_invalid_current_language(self):
        """
        Test setting an unsupported current language.
        """
        with self.assertRaises(ValueError):
            self.instance.set_current_language('xx')

    def test_is_field_translatable(self):
        """
        Test checking if a field is translatable.
        """
        self.assertTrue(self.instance.is_field_translatable('title'))
        self.assertFalse(
            self.instance.is_field_translatable('non_translatable_field'))

    def test_validate_language_code(self):
        """
        Test validating a supported language code.
        """
        # Should not raise an exception
        self.instance._validate_language_code('am')

    def test_validate_invalid_language_code(self):
        """
        Test validating an unsupported language code.
        """
        with self.assertRaises(ValueError):
            self.instance._validate_language_code('xx')

    def test_get_lisan_object_does_not_exist(self):
        """
        Test that get_lisan returns None if the Lisan object does not exist.
        """
        with patch.object(
                self.instance.Lisan.objects,
                'filter',
                side_effect=ObjectDoesNotExist):
            lisan = self.instance.get_lisan('am')
            self.assertIsNone(lisan)

    def test_get_lisan_general_exception(self):
        """
        Test that get_lisan raises a general exception if one occurs.
        """
        with patch.object(
                self.instance.Lisan.objects,
                'filter',
                side_effect=Exception("Unexpected error")):
            with self.assertRaises(Exception) as context:
                self.instance.get_lisan('am')
            self.assertEqual(str(context.exception), "Unexpected error")

    def test_set_lisan_field_does_not_exist(self):
        """
        Test that set_lisan raises FieldDoesNotExist if an invalid
        field is provided.
        """
        with self.assertRaises(FieldDoesNotExist) as context:
            self.instance.set_lisan('am', non_existent_field="Invalid")
        self.assertEqual(
            str(context.exception),
            "Field 'non_existent_field' does not exist in the translation model."  # noqa
        )

    def test_set_lisan_primary_key_field(self):
        """
        Test that set_lisan handles a primary key field that is not named 'id'.
        """
        # Create a Lisan translation with a custom primary key
        lisan = self.instance.set_lisan(
            'am', title="ሰላም", description="ምሳሌ"
        )
        self.assertEqual(lisan.language_code, "am")
        self.assertEqual(lisan.title, "ሰላም")
        self.assertEqual(lisan.description, "ምሳሌ")
        self.assertEqual(lisan.testmodel_id, self.instance.id)

    def test_set_lisan_primary_key_value(self):
        """
        Test that set_lisan sets the primary key value when provided.
        """
        lisan = self.instance.set_lisan(
            'am', title="ሰላም", description="ምሳሌ"
        )
        self.assertEqual(lisan.language_code, "am")
        self.assertEqual(lisan.testmodel_id, self.instance.id)

    def test_set_lisan_replaces_existing_translation(self):
        """
        Test that set_lisan replaces the existing translation for a language
        instead of creating a duplicate.
        """
        # Update the 'am' translation
        self.instance.set_lisan('am', title="Updated Title")

        # Retrieve the updated translation
        lisan = self.instance.get_lisan('am')

        # Verify the translation was updated
        self.assertEqual(lisan.title, "Updated Title")
        self.assertEqual(lisan.description, "ምሳሌ መግለጫ")  # Unchanged field

        # Verify that no duplicate translations exist
        am_translations_count = self.instance.Lisan.objects.filter(
            language_code='am').count()
        self.assertEqual(am_translations_count, 1)

    def test_set_lisan_creates_new_translation(self):
        """
        Test that set_lisan creates a new translation if one does not exist
        for the specified language.
        """
        # Add a new translation for 'or' (Oromo)
        lisan = self.instance.set_lisan(
            'or', title="Nagaa Addunyaa", description="Fakkeenya")

        # Verify the translation was created
        self.assertEqual(lisan.language_code, "or")
        self.assertEqual(lisan.title, "Nagaa Addunyaa")
        self.assertEqual(lisan.description, "Fakkeenya")

    def test_set_bulk_lisans_updates_and_creates_translations(self):
        """
        Test that set_bulk_lisans updates existing translations and creates
        new translations as needed.
        """
        translations = [
            {
                "language_code": "or",
                "title": "Nagaa Addunyaa",
                "description": "Fakkeenya"
            },
            {
                "language_code": "am",
                "title": "አስደሳች ጉዞ",
                "description": "ምሳሌ መግለጫ"
            }
        ]
        self.instance.set_bulk_lisans(translations)

        # Verify the 'am' translation was updated
        am_translation = self.instance.get_lisan('am')
        self.assertEqual(am_translation.title, "አስደሳች ጉዞ")
        # Unchanged field
        self.assertEqual(am_translation.description, "ምሳሌ መግለጫ")

        # Verify the 'or' translation was created
        or_translation = self.instance.get_lisan('or')
        self.assertEqual(or_translation.title, "Nagaa Addunyaa")
        self.assertEqual(or_translation.description, "Fakkeenya")

        # Verify that no duplicates exist
        am_translations_count = self.instance.Lisan.objects.filter(
            language_code='am').count()
        or_translations_count = self.instance.Lisan.objects.filter(
            language_code='or').count()
        self.assertEqual(am_translations_count, 1)
        self.assertEqual(or_translations_count, 1)
