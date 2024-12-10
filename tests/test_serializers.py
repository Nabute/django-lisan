from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from tests.models import TestModel
from lisan.serializers import TranslationSerializer, LisanSerializerMixin


class TestTranslationSerializer(TestCase):
    """
    Test suite for the TranslationSerializer class.
    """

    def test_dynamic_fields(self):
        """
        Test that TranslationSerializer dynamically adds fields based on
        `lisan_fields`.
        """
        serializer = TranslationSerializer(
            lisan_fields=['title', 'description'])
        self.assertIn('title', serializer.fields)
        self.assertIn('description', serializer.fields)
        self.assertIn('language_code', serializer.fields)

    def test_serialize_translation(self):
        """
        Test serialization of translation data.
        """
        data = {'language_code': 'am', 'title': 'ሰላም', 'description': 'ምሳሌ'}
        serializer = TranslationSerializer(
            lisan_fields=['title', 'description'], data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)

    def test_deserialize_translation(self):
        """
        Test deserialization of translation data.
        """
        serializer = TranslationSerializer(
            lisan_fields=['title', 'description'])
        instance = serializer.to_representation({
            'language_code': 'am', 'title': 'ሰላም', 'description': 'ምሳሌ'
        })
        self.assertEqual(instance['language_code'], 'am')
        self.assertEqual(instance['title'], 'ሰላም')
        self.assertEqual(instance['description'], 'ምሳሌ')


class TestLisanSerializerMixin(TestCase):
    """
    Test suite for the LisanSerializerMixin class.
    """

    def setUp(self):
        """
        Set up the test environment with a mock request and model instance.
        """
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.request.language_code = 'en'
        self.model_instance = TestModel.objects.create(
            title="Hello World",
            description="Sample description"
        )
        self.model_instance.set_lisan('am', title="ሰላም", description="ምሳሌ")

        class TestModelSerializer(LisanSerializerMixin):
            class Meta:
                model = TestModel
                fields = ['id', 'title', 'description', 'author']

        self.serializer_class = TestModelSerializer

    def test_representation(self):
        """
        Test the representation of the model with language-specific fields
        and structured translations.
        """
        serializer = self.serializer_class(
            self.model_instance, context={'request': self.request})
        representation = serializer.data

        # Check language-specific fields
        self.assertEqual(representation['title'], "Hello World")
        self.assertEqual(representation['description'], "Sample description")

        # Check structured translations
        self.assertIn('translations', representation)
        translations = representation['translations']
        self.assertEqual(len(translations), 4)  # en, am, or, tg
        self.assertEqual(translations[1]['language_code'], 'am')
        self.assertEqual(translations[1]['title'], "ሰላም")
        self.assertEqual(translations[1]['description'], "ምሳሌ")

    def test_create_with_translations(self):
        """
        Test creating a model instance with translations.
        """
        self.request.method = 'POST'
        data = {
            'title': "New Title",
            'description': "New Description",
            'translations': [
                {
                    "language_code": "en",
                    "title": "The Great Adventure",
                    "description": "An exciting journey through uncharted lands."  # noqa
                },
                {
                    "language_code": "am",
                    "title": "አስደሳች ጉዞ",
                    "description": "በማይታወቁ መሬቶች ላይ አስገራሚ ጉዞ."
                },
                {
                    "language_code": "or",
                    "title": "Adeemsa Guddaa",
                    "description": "Daandii jajjaboo fi tasgabboof balaa keessa darbuu."  # noqa
                },
                {
                    "language_code": "tg",
                    "title": "Сафари Бузург",
                    "description": "Сафари ҳаяҷоновар тавассути сарзаминҳои номаълум."  # noqa
                }
            ]
        }
        serializer = self.serializer_class(
            data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()
        self.assertEqual(instance.title, "New Title")
        self.assertEqual(instance.get_lisan_field('title', 'am'), "አስደሳች ጉዞ")
        self.assertEqual(instance.get_lisan_field(
            'description', 'am'), "በማይታወቁ መሬቶች ላይ አስገራሚ ጉዞ.")

    def test_update_with_translations(self):
        """
        Test updating a model instance with translations.
        """
        self.request.method = 'PATCH'
        data = {
            'title': "Updated Title",
            'translations': [
                {'language_code': 'am', 'title': "አዲስ ሰላም"}
            ]
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()
        self.assertEqual(instance.title, "Updated Title")
        self.assertEqual(instance.get_lisan_field('title', 'am'), "አዲስ ሰላም")

    def test_validation_missing_translations(self):
        """
        Test validation error for missing translations.
        """
        self.request.method = 'POST'
        data = {'title': "New Title"}
        serializer = self.serializer_class(
            data=data, context={'request': self.request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_validation_unsupported_language(self):
        """
        Test validation error for unsupported language code.
        """
        self.request.method = 'POST'
        data = {
            'title': "New Title",
            'translations': [
                {'language_code': 'unsupported', 'title': "Test"}
            ]
        }
        serializer = self.serializer_class(
            data=data, context={'request': self.request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_dynamic_fields_removal(self):
        """
        Test that the `translations` field is removed for non-write methods.
        """
        self.request.method = 'GET'
        serializer = self.serializer_class(context={'request': self.request})
        self.assertNotIn('translations', serializer.fields)

    def test_dynamic_fields_addition(self):
        """
        Test that the `translations` field is added for write methods.
        """
        for method in ['POST', 'PUT', 'PATCH']:
            self.request.method = method
            serializer = self.serializer_class(
                context={'request': self.request})
            self.assertIn('translations', serializer.fields)

    def test_representation_unsupported_language(self):
        """
        Test that the representation falls back to the default language
        when the requested language is not supported.
        """
        self.request.language_code = 'unsupported'
        serializer = self.serializer_class(
            self.model_instance, context={'request': self.request})
        representation = serializer.data

        # Check that it falls back to the default language
        self.assertEqual(representation['title'], "Hello World")
        self.assertEqual(representation['description'], "Sample description")

    def test_validate_translations_partial(self):
        """
        Test validation with partial translations in partial update mode.
        """
        serializer = self.serializer_class(context={'request': self.request})
        translations = [{'language_code': 'en', 'title': "Partial Title"}]
        # No exceptions should be raised for partial updates
        serializer._validate_translations(translations, partial=True)

    def test_validate_translations_missing_languages(self):
        """
        Test validation failure for missing translations in non-partial mode.
        """
        serializer = self.serializer_class(context={'request': self.request})
        translations = [{'language_code': 'en', 'title': "Partial Title"}]
        with self.assertRaises(ValidationError) as context:
            serializer._validate_translations(translations)
        self.assertIn(
            "Missing translations for languages:", str(context.exception))

    def test_create_with_missing_fields(self):
        """
        Test that `create` raises a validation error for missing
        required fields.
        """
        self.request.method = 'POST'
        # Missing `title`
        data = {'translations': [{'language_code': 'am'}]}
        serializer = self.serializer_class(
            data=data, context={'request': self.request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def test_update_with_unsupported_language(self):
        """
        Test that `update` raises a validation error when an unsupported
        language is used in translations.
        """
        self.request.method = 'PATCH'
        data = {
            'translations': [
                {'language_code': 'unsupported', 'title': "Invalid"}]
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
            serializer.save()

        self.assertIn("Unsupported language code", str(context.exception))

    def test_update_with_partial_translations(self):
        """
        Test that `update` allows partial translations with optional fields
        in a PATCH request.
        """
        self.request.method = 'PATCH'
        # Only language_code provided
        data = {
            'translations': [{'language_code': 'am'}]
        }
        serializer = self.serializer_class(
            self.model_instance, data=data, partial=True,
            context={'request': self.request})

        # Validate and save without raising exceptions
        self.assertTrue(serializer.is_valid(raise_exception=True))

        instance = serializer.save()

        # Ensure the instance is updated correctly
        # Unchanged
        self.assertEqual(instance.get_lisan_field('title', 'am'), "ሰላም")
        # Unchanged
        self.assertEqual(instance.get_lisan_field('description', 'am'), "ምሳሌ")

    def test_handle_dynamic_fields_add_translations(self):
        """
        Test that `_handle_dynamic_fields` dynamically adds the `translations`
        field for write methods when not already present.
        """
        self.request.method = 'POST'
        serializer = self.serializer_class(context={'request': self.request})

        # Remove translations field to simulate the condition
        serializer.fields.pop('translations', None)

        # Call _handle_dynamic_fields to add it back
        serializer._handle_dynamic_fields()

        self.assertIn('translations', serializer.fields)

    def test_create_with_unsupported_language(self):
        """
        Test that `create` defaults to the `default_language` if the
        provided language code is not supported.
        """
        self.request.method = 'POST'
        self.request.language_code = 'dkajflskdjfl'
        data = {
            'title': "Unsupported Language Test",
            'translations': [
                {
                    "language_code": "en",
                    "title": "The Great Adventure",
                    "description": "An exciting journey through uncharted lands."  # noqa
                },
                {
                    "language_code": "fr",
                    "title": "አስደሳች ጉዞ",
                    "description": "በማይታወቁ መሬቶች ላይ አስገራሚ ጉዞ."
                },
                {
                    "language_code": "or",
                    "title": "Adeemsa Guddaa",
                    "description": "Daandii jajjaboo fi tasgabboof balaa keessa darbuu."  # noqa
                },
                {
                    "language_code": "tg",
                    "title": "Сафари Бузург",
                    "description": "Сафари ҳаяҷоновар тавассути сарзаминҳои номаълум."  # noqa
                }
            ]
        }
        serializer = self.serializer_class(
            data=data, context={'request': self.request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # Ensure it defaults to the default language ('en')
            self.assertEqual(
                instance.get_lisan_field('title', 'or'),
                "Unsupported Language Test")
            self.request.language_code = None

    def test_validate_translations_empty_partial(self):
        """
        Test that `_validate_translations` skips validation for
        empty translations in partial updates.
        """
        serializer = self.serializer_class(context={'request': self.request})
        # Should not raise any exception
        serializer._validate_translations([], partial=True)

    def test_validate_translations_empty_non_partial(self):
        """
        Test that `_validate_translations` raises a ValidationError for empty
        translations in non-partial updates.
        """
        serializer = self.serializer_class(context={'request': self.request})
        with self.assertRaises(ValidationError) as context:
            serializer._validate_translations([], partial=False)
        self.assertIn("Translations are required.", str(context.exception))

    def test_validate_translations_missing_fields(self):
        """
        Test that `_validate_translations` raises a ValidationError when
        required fields are missing in translations during non-partial updates.
        """
        serializer = self.serializer_class(context={'request': self.request})
        translations = [{'language_code': 'en'}]  # Missing required fields
        with self.assertRaises(ValidationError) as context:
            serializer._validate_translations(translations, partial=False)
        self.assertIn(
            "Missing translations for languages",
            str(context.exception.detail[0]))

    def test_update_sync_translatable_fields(self):
        """
        Test that updating translatable fields in the main model synchronizes
        changes to the default language translation.
        """
        self.request.method = 'PATCH'
        data = {
            'title': "Updated Title",
            'description': "Updated Description"
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()

        # Check that the main model fields are updated
        self.assertEqual(instance.title, "Updated Title")
        self.assertEqual(instance.description, "Updated Description")

        # Check that the default language translation is synchronized
        lisan = instance.get_lisan('en')
        self.assertEqual(lisan.title, "Updated Title")
        self.assertEqual(lisan.description, "Updated Description")

    def test_update_sync_translatable_fields_with_language(self):
        """
        Test that updating translatable fields synchronizes changes to the
        specified language translation when the language code is set.
        """
        self.request.method = 'PATCH'
        self.request.language_code = 'am'
        data = {
            'title': "አዲስ ርእስ",
            'description': "አዲስ መግለጫ"
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()

        # Check that the main model fields are updated
        self.assertEqual(instance.title, "አዲስ ርእስ")
        self.assertEqual(instance.description, "አዲስ መግለጫ")

        # Check that the 'am' translation is updated
        lisan = instance.get_lisan('am')
        self.assertEqual(lisan.title, "አዲስ ርእስ")
        self.assertEqual(lisan.description, "አዲስ መግለጫ")

    def test_partial_update_without_translatable_fields(self):
        """
        Test that updating non-translatable fields does not affect
        translations.
        """
        self.request.method = 'PATCH'
        data = {'author': "New Author"}
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()

        # Check that the main model field is updated
        self.assertEqual(instance.author, "New Author")

        # Check that translations remain unchanged
        lisan = instance.get_lisan('am')
        self.assertEqual(lisan.title, "ሰላም")
        self.assertEqual(lisan.description, "ምሳሌ")

    def test_update_translatable_and_non_translatable_fields(self):
        """
        Test that updating both translatable and non-translatable fields
        synchronizes translatable fields while updating the main model.
        """
        self.request.method = 'PATCH'
        data = {
            'title': "Updated Title",
            'author': "New Author"
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()

        # Check that both main model fields are updated
        self.assertEqual(instance.title, "Updated Title")
        self.assertEqual(instance.author, "New Author")

        # Check that the default language translation is synchronized
        lisan = instance.get_lisan('en')
        self.assertEqual(lisan.title, "Updated Title")
        self.assertEqual(lisan.description, "")

    def test_update_with_unsupported_language_to_sync(self):
        """
        Test that updating with an unsupported language defaults to the
        default language for synchronization.
        """
        self.request.method = 'PATCH'
        self.request.language_code = 'unsupported'
        data = {
            'title': "Unsupported Language Title"
        }
        serializer = self.serializer_class(
            self.model_instance, data=data,
            partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()

        # Check that the default language is used for synchronization
        lisan = instance.get_lisan('en')
        self.assertEqual(lisan.title, "Unsupported Language Title")
