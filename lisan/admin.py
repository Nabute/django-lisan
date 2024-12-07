from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


class LisanAdminMixin(admin.ModelAdmin):
    """
    A Django admin mixin to add multilingual support for models.

    This mixin dynamically generates getter methods for fields defined in the
    model's `lisan_fields` attribute, allowing easy access and display of
    localized content within the Django admin interface.
    """

    lisan_display_format = "{field_name} ({language_code})"

    def __init__(self, *args, **kwargs):
        """
        Initialize the LisanAdminMixin.

        If the model has `lisan_fields` defined, it generates getter methods
        for each field to display localized content in the admin interface.
        """
        super().__init__(*args, **kwargs)
        if hasattr(self.model, 'lisan_fields'):
            self._generate_lisan_getters()

    def _generate_lisan_getters(self):
        """
        Dynamically generate getter methods for each field in `lisan_fields`.

        These methods retrieve the content in the default language (English)
        and add them to the `list_display` in the admin interface.
        """
        for field_name in self.model.lisan_fields:
            method_name = f'get_lisan_{field_name}'
            setattr(self, method_name, self._create_lisan_getter(field_name))

            short_description = self.lisan_display_format.format(
                field_name=field_name.capitalize(), language_code='EN'
            )
            getattr(self, method_name).short_description = short_description

            if 'list_display' in self.__dict__:
                self.list_display += (method_name,)
            else:
                self.list_display = (method_name,)

    def _create_lisan_getter(self, field_name):
        """
        Create a getter method for the specified lisan field.

        Args:
            field_name (str): The name of the field to create the getter for.

        Returns:
            function: A function that retrieves the localized content of the
                      specified field in English.
        """
        def getter(obj):
            return obj.get_lisan_field(field_name, 'en')
        return getter

    def get_lisan_inline(self):
        """
        Return the inline class for managing translations in the admin.

        This method creates and returns a `TabularInline` class for managing
        related translation models in the Django admin interface.

        Returns:
            LisanInline: The inline class for managing translations.
        """
        lisan_field = None
        for field in self.model._meta.get_fields():
            if field.is_relation and field.one_to_many and field.related_model:
                # Verify it's a Lisan model
                if hasattr(field.related_model, 'language_code'):
                    lisan_field = field
                    break

        if not lisan_field:
            raise ImproperlyConfigured(
                f"{self.model.__name__} does not have a related Lisan model."
            )

        lisan_model = lisan_field.related_model

        class LisanInline(admin.TabularInline):
            model = lisan_model
            extra = 1

        return LisanInline

    def get_inlines(self, request, obj=None):
        """
        Get the list of inlines to display in the admin interface.

        If the model has `lisan_fields`, it returns a list containing the
        inline class for managing translations.

        Args:
            request (HttpRequest): The request object.
            obj (Model): The model instance (optional).

        Returns:
            list: A list of inline classes to be displayed in the admin.
        """
        if getattr(self.model, 'lisan_fields', None):
            return [self.get_lisan_inline()]
        return []
