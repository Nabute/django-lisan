import unittest
from django.conf import settings
from unittest.mock import MagicMock, patch

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.admin',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )

import django
django.setup()

from lisan.admin import LisanAdminMixin


class LisanAdminMixinTest(unittest.TestCase):
    """
    Unit tests for the LisanAdminMixin class.

    These tests ensure that the mixin's methods behave as expected in isolation,
    without requiring a fully running Django project.
    """

    def setUp(self):
        """
        Set up the test case with mocked model and admin_site.

        We use MagicMock to mock a model and the admin site. This allows us to 
        isolate the behavior of the LisanAdminMixin without needing real models 
        or a real Django admin site.
        """
        # Mock a model that would be used in the admin
        self.model = MagicMock()
        
        # Mock the admin site, since we're testing an admin mixin
        self.admin_site = MagicMock()
        
        # Instantiate the LisanAdminMixin with the mocked model and admin site
        self.admin = LisanAdminMixin(model=self.model, admin_site=self.admin_site)

    def test_lisan_getters_are_generated(self):
        """
        Test that getter methods are dynamically generated for lisan fields.

        The LisanAdminMixin should dynamically create methods for fields listed 
        in `lisan_fields` of the model. These methods are added to the mixin 
        (e.g., get_lisan_<field_name>), and they should also be added to the 
        `list_display` in the admin.
        """
        # Simulate the model having two multilingual fields: 'name' and 'description'
        self.model.lisan_fields = ['name', 'description']
        
        # Call the private method to generate getter methods
        self.admin._generate_lisan_getters()

        # Check that a method `get_lisan_name` has been dynamically created
        self.assertTrue(hasattr(self.admin, 'get_lisan_name'))
        
        # Ensure the dynamically created getter method is added to the list_display
        self.assertIn('get_lisan_name', self.admin.list_display)

    def test_create_lisan_getter(self):
        """
        Test that the `_create_lisan_getter` method generates the correct getter function.

        This method creates a getter function for a specific lisan field (in this case, 'name').
        The generated function should retrieve the localized content of the field for the 'en' 
        language from the model instance.
        """
        # Mock a model instance
        mock_instance = MagicMock()
        
        # Mock the method get_lisan_field to return "Localized Name" when called
        mock_instance.get_lisan_field.return_value = "Localized Name"
        
        # Create the getter function for the 'name' field
        getter = self.admin._create_lisan_getter('name')
        
        # Call the generated getter function and check the returned value
        result = getter(mock_instance)
        
        # The getter function should return the mocked "Localized Name"
        self.assertEqual(result, "Localized Name")
        
        # Ensure the model's get_lisan_field method was called with the correct arguments
        mock_instance.get_lisan_field.assert_called_once_with('name', 'en')

    def test_generate_getters_no_lisan_fields(self):
        """
        Test that `_generate_lisan_getters` does nothing if the model has no lisan_fields.
        """
        # Simulate a model without lisan_fields
        self.model.lisan_fields = []

        # Call the method and check that no getters are added
        self.admin._generate_lisan_getters()
        self.assertNotIn('get_lisan_name', self.admin.__dict__)
        self.assertNotIn('get_lisan_description', self.admin.__dict__)

    def test_get_lisan_inline(self):
        """
        Test that the `get_lisan_inline` method returns a valid TabularInline class.

        This method should dynamically create a TabularInline class that manages translations
        related to the main model.
        """
        # Mock the related model field (lisans) and the related_model attribute
        lisan_model = MagicMock()
        self.model._meta.get_field.return_value.related_model = lisan_model

        # Call the method
        LisanInline = self.admin.get_lisan_inline()

        # Assert that the returned class is a subclass of admin.TabularInline
        self.assertTrue(issubclass(LisanInline, django.contrib.admin.TabularInline))
        self.assertEqual(LisanInline.model, lisan_model)

    def test_get_inlines_with_lisan_fields(self):
        """
        Test that `get_inlines` returns the inline class if the model has lisan_fields.
        """
        # Mock lisan_fields to simulate the model having translatable fields
        self.model.lisan_fields = ['name']

        # Call the method
        inlines = self.admin.get_inlines(request=None)

        # The inline list should contain the translation inline
        self.assertEqual(len(inlines), 1)
        self.assertTrue(issubclass(inlines[0], django.contrib.admin.TabularInline))

    def test_get_inlines_without_lisan_fields(self):
        """
        Test that `get_inlines` returns the default inline even if the model has no lisan_fields.
        """
        self.model.lisan_fields = None

        # Check the state of the model and inline generation
        print(f"Model lisan_fields: {self.model.lisan_fields}")
        inlines = self.admin.get_inlines(request=None)
        print(f"Inlines returned: {inlines}")

        # Assert expected behavior
        self.assertEqual(len(inlines), 0)



if __name__ == "__main__":
    # This runs the tests when the file is executed directly
    unittest.main()
