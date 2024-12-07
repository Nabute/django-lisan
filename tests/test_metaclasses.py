from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from lisan.mixins import LisanModelMixin
from lisan.metaclasses import create_lisan_model  # LisanModelMeta
from tests.models import TestModel


class MetaclassesTestCase(TestCase):
    def setUp(self):
        # Update settings for testing
        settings.LISAN_PRIMARY_KEY_TYPE = models.UUIDField
        self.fields = {
            'title': models.CharField(max_length=100, blank=True, default=''),
            'description': models.TextField(blank=True, default='')
        }
        self.instance = TestModel.objects.create(
            title="Hello World",
            description="Sample description"
        )

    # Test the initial creation of a model
    def test_initial_creation(self):
        self.assertEqual(self.instance.title, "Hello World")
        self.assertEqual(self.instance.description, "Sample description")

    # Test setting and retrieving translations
    def test_set_and_get_translation(self):
        self.instance.set_lisan(
            'am', title="ሰላም ለዓለም", description="ምሳሌ መግለጫ")
        self.assertEqual(
            self.instance.get_lisan_field('title', 'am'), "ሰላም ለዓለም")
        self.assertEqual(self.instance.get_lisan_field(
            'description', 'am'), "ምሳሌ መግለጫ")

    # Test fallback behavior when translation is missing
    def test_fallback_language(self):
        # Falls back to default
        self.assertEqual(
            self.instance.get_lisan_field('title', 'am'), "Hello World")

    # Test overwriting a translation
    def test_overwriting_translation(self):
        self.instance.set_lisan('tg', title="ሰላም አለም")
        self.instance.set_lisan('tg', title="ሰላም ዓለም")
        self.assertEqual(self.instance.get_lisan_field(
            'title', 'tg'), "ሰላም ዓለም")

    # Test retrieving translations for invalid language
    def test_invalid_language_code(self):
        with self.assertRaises(ValueError):
            self.instance.set_lisan(None, title="Invalid")

    def test_unsupported_language_code(self):
        with self.assertRaises(ValueError):
            self.instance.set_lisan('abcldkjfd', title="Invalid")

    # Test setting a translation with invalid data
    def test_invalid_data_for_translation(self):
        with self.assertRaises(IntegrityError):
            self.instance.set_lisan('am', title=None)

    def test_create_lisan_model(self):
        lisan_model = create_lisan_model(
            TestModel, self.fields, models.UUIDField)

        # Assert the model has the required fields
        self.assertTrue(hasattr(lisan_model, 'language_code'))
        self.assertTrue(hasattr(lisan_model, 'id'))
        self.assertTrue(hasattr(lisan_model, 'title'))
        self.assertTrue(hasattr(lisan_model, 'description'))

        # Assert the ForeignKey relationship
        self.assertTrue(hasattr(lisan_model, 'testmodel'))

        # Assert the primary key is UUIDField
        self.assertEqual(
            lisan_model._meta.pk.__class__, models.UUIDField)

        # Assert the unique constraint
        constraints = lisan_model._meta.constraints
        self.assertEqual(len(constraints), 1)
        self.assertEqual(
            constraints[0].fields, tuple(['language_code', 'testmodel']))

        # Assert the table name
        self.assertEqual(lisan_model._meta.db_table, 'tests_testmodel_lisan')

    def test_missing_lisan_fields(self):
        with self.assertRaises(AttributeError):
            class InvalidModel(LisanModelMixin, models.Model):
                a = models.CharField(max_length=100)

    def test_invalid_lisan_fields(self):
        with self.assertRaises(ValueError):
            class InvalidModel(LisanModelMixin, models.Model):
                lisan_fields = ['nonexistent_field']

    def test_invalid_primary_key_type(self):
        with self.assertRaises(TypeError):
            create_lisan_model(TestModel, self.fields, primary_key_type=str)

    def test_default_primary_key_type(self):
        lisan_model = create_lisan_model(TestModel, self.fields)
        self.assertEqual(
            lisan_model._meta.pk.__class__, models.BigAutoField)

    def test_duplicate_translation(self):
        lisan_model = create_lisan_model(
            TestModel, self.fields, models.UUIDField)
        lisan_model.objects.create(
            language_code='am',
            title="Sample",
            description="Description",
            testmodel_id=self.instance.id
        )

        with self.assertRaises(ValidationError):
            duplicate_instance = lisan_model(
                language_code='am',
                title="Duplicate",
                description="Duplicate description",
                testmodel_id=self.instance.id
            )
            duplicate_instance.clean()

    def test_missing_model_class(self):
        with self.assertRaises(AttributeError):
            create_lisan_model(None, self.fields)

    def test_empty_fields(self):
        lisan_model = create_lisan_model(TestModel, {}, models.UUIDField)
        self.assertFalse(hasattr(lisan_model, 'title'))
        self.assertFalse(hasattr(lisan_model, 'description'))

    # def test_invalid_foreign_key_setup(self):
    #     with self.assertRaises(ValueError):
    #         class InvalidForeignKeyModel(
    #                 models.Model, metaclass=LisanModelMeta):
    #             lisan_fields = ['title']
    #             title = models.CharField(max_length=100)
    #             lisan_primary_key_type = "invalid_type"
