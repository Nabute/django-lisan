from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib import admin
from lisan.admin import LisanAdminMixin
from tests.models import TestModel, SomeModel
from django.core.exceptions import ImproperlyConfigured


class TestLisanAdminMixin(TestCase):
    """
    Test suite for the LisanAdminMixin class, which provides multilingual
    support in the Django admin interface for models using LisanModelMixin.
    """

    def setUp(self):
        """
        Set up the test environment. Create a test model instance and an
        admin instance for the tests.
        """
        self.factory = RequestFactory()
        self.site = AdminSite()

        # Create a test admin instance for the TestModel
        class TestModelAdmin(LisanAdminMixin, admin.ModelAdmin):
            model = TestModel

        self.admin = TestModelAdmin(model=TestModel, admin_site=self.site)
        self.instance = TestModel.objects.create(
            title="Hello World",
            description="Sample description"
        )

    def test_admin_initialization(self):
        """
        Test that the admin mixin dynamically generates getter methods
        for all fields defined in the model's `lisan_fields` and adds
        them to the `list_display`.
        """
        self.assertIn('get_lisan_title', self.admin.list_display)
        self.assertIn('get_lisan_description', self.admin.list_display)

    def test_generated_getter_methods(self):
        """
        Test that getter methods for multilingual fields are dynamically
        added to the admin and correctly return the localized content.
        """
        # Check that the getter methods exist
        self.assertTrue(hasattr(self.admin, 'get_lisan_title'))
        self.assertTrue(hasattr(self.admin, 'get_lisan_description'))

        # Check the behavior of the getter methods
        getter_title = getattr(self.admin, 'get_lisan_title')
        self.assertEqual(getter_title(self.instance), "Hello World")

        getter_description = getattr(self.admin, 'get_lisan_description')
        self.assertEqual(
            getter_description(self.instance), "Sample description")

    def test_display_format(self):
        """
        Test that the dynamically generated getter methods have the correct
        short_description format for display in the admin interface.
        """
        getter_title = getattr(self.admin, 'get_lisan_title')
        self.assertEqual(
            getter_title.short_description, "Title (EN)")

        getter_description = getattr(self.admin, 'get_lisan_description')
        self.assertEqual(
            getter_description.short_description, "Description (EN)")

    def test_get_lisan_inline(self):
        """
        Test the creation of the inline class for managing translations
        in the admin interface.
        """
        inline_class = self.admin.get_lisan_inline()
        self.assertTrue(issubclass(inline_class, admin.TabularInline))
        self.assertEqual(inline_class.model, TestModel.Lisan)

    def test_get_lisan_inline_no_lisan_model(self):
        """
        Test that get_lisan_inline raises ImproperlyConfigured if no
        related Lisan model exists.
        """
        class NoLisanModel:
            _meta = SomeModel._meta  # Simulate a model with no lisan_fields

        class NoLisanAdmin(LisanAdminMixin, admin.ModelAdmin):
            model = NoLisanModel

        _admin = NoLisanAdmin(model=NoLisanModel, admin_site=None)

        with self.assertRaises(ImproperlyConfigured) as context:
            _admin.get_lisan_inline()
        self.assertIn(
            "NoLisanModel does not have a related Lisan model.",
            str(context.exception)
        )

    def test_get_inlines(self):
        """
        Test that the admin correctly includes the inline class for managing
        translations when `lisan_fields` is defined in the model.
        """
        # Verify that the inline class is returned for models with lisan_fields
        inlines = self.admin.get_inlines(None)
        self.assertEqual(len(inlines), 1)
        self.assertTrue(issubclass(inlines[0], admin.TabularInline))

        # Verify that no inlines are returned for models without lisan_fields
        class NoLisanModel(models.Model):
            pass

        class NoLisanModelAdmin(LisanAdminMixin, admin.ModelAdmin):
            model = NoLisanModel

        no_lisan_admin = NoLisanModelAdmin(
            model=NoLisanModel, admin_site=self.site)
        self.assertEqual(no_lisan_admin.get_inlines(None), [])

    def test_model_without_lisan_fields(self):
        """
        Test that the admin mixin does not add any getters or modify
        `list_display` for models that do not define `lisan_fields`.
        """
        class NoLisanModel(models.Model):
            name = models.CharField(max_length=100)

        class NoLisanModelAdmin(LisanAdminMixin, admin.ModelAdmin):
            model = NoLisanModel

        admin_instance = NoLisanModelAdmin(
            model=NoLisanModel, admin_site=self.site)

        # Ensure no getters are added
        self.assertFalse(hasattr(admin_instance, 'get_lisan_name'))

    def test_empty_lisan_fields(self):
        """
        Test the behavior of the admin mixin when the model's `lisan_fields`
        is an empty list.
        """
        class EmptyLisanModel(models.Model):
            lisan_fields = []

        class EmptyLisanModelAdmin(LisanAdminMixin, admin.ModelAdmin):
            model = EmptyLisanModel

        admin_instance = EmptyLisanModelAdmin(
            model=EmptyLisanModel, admin_site=self.site)

        # Ensure no lisan getter methods are added to list_display
        lisan_getters = [field for field in admin_instance.list_display if field.startswith('get_lisan_')] # noqa
        self.assertEqual(lisan_getters, [])
