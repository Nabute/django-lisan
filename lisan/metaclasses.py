from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def create_lisan_model(
        model_cls, fields, primary_key_type=models.BigAutoField):
    """
    Dynamically create a Lisan model for the given model class.

    This function generates a new model class that supports multilingual
    fields. The generated model will have a `language_code` field and
    a ForeignKey relationship to the original model.

    Args:
        model_cls (Model): The original Django model class.
        fields (dict): A dictionary of fields to be included in the Lisan
                       model.

    Returns:
        Model: The dynamically created Lisan model class.
    """
    # Define metadata for the dynamically created Lisan model
    class Meta:
        app_label = model_cls._meta.app_label
        constraints = [
            models.UniqueConstraint(
                fields=['language_code', model_cls._meta.model_name],
                name=f'unique_language_{model_cls._meta.verbose_name}'
            )
        ]
        db_table = f"{model_cls._meta.db_table}_lisan"
        verbose_name = f"{model_cls._meta.verbose_name} lisan"
        verbose_name_plural = f"{model_cls._meta.verbose_name_plural} lisans"

    # Build the attributes for the Lisan model
    attrs = {
        'Meta': Meta,
        '__module__': model_cls.__module__,
        'language_code': models.CharField(
            max_length=10,
            verbose_name=_("language code")
        ),
    }

    if not issubclass(primary_key_type, models.Field):
        raise TypeError(
            "Invalid primary_key_type provided. Must be a subclass of models.Field.") # noqa

    if primary_key_type is models.UUIDField:
        import uuid
        # Configure UUIDField with auto-generation
        attrs['id'] = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False,
            verbose_name=_("id")
        )
    else:
        # Default primary key field setup
        attrs['id'] = primary_key_type(primary_key=True)

    # Add the specified fields to the Lisan model
    for field_name, field in fields.items():
        attrs[field_name] = field

    def clean(self):
        if self.__class__.objects.filter(
            language_code=self.language_code,
            **{f"{model_cls._meta.model_name}_id": getattr(
                self, f"{model_cls._meta.model_name}_id")}
        ).exists():
            raise ValidationError("Duplicate translation for this language.")

    attrs['clean'] = clean

    # Create a ForeignKey field linking the Lisan model to the original model
    attrs[model_cls._meta.model_name] = models.ForeignKey(
        model_cls,
        related_name=f"{model_cls._meta.model_name}_lisans",
        on_delete=models.CASCADE
    )

    # Dynamically create the Lisan model class
    lisan_model = type(
        f'{model_cls.__name__}LisanModel',
        (models.Model,),
        attrs
    )

    return lisan_model


class LisanModelMeta(models.base.ModelBase):
    """
    A metaclass that adds multilingual support to Django models.

    This metaclass automatically generates a corresponding Lisan model
    for any model that uses the `LisanModelMixin`. It identifies the fields
    marked for multilingual support and creates a related model that stores
    the translated content.
    """

    def __new__(cls, name, bases, attrs):
        """
        Create a new model class and add Lisan model support.

        This method is responsible for creating the new model class and
        automatically generating a related Lisan model if the new class
        includes the `LisanModelMixin` in its base classes.

        Args:
            name (str): The name of the new model class.
            bases (tuple): The base classes of the new model.
            attrs (dict): The attributes of the new model class.

        Returns:
            Model: The newly created model class with multilingual support.
        """
        if 'LisanModelMixin' in [base.__name__ for base in bases]:
            lisan_fields = attrs.get('lisan_fields')

            # If `lisan_fields` is not defined, raise an exception
            if lisan_fields is None:
                raise AttributeError(
                    f"{name} must define 'lisan_fields' when using LisanModelMixin."  # noqa
                )

            if not all(field in attrs for field in lisan_fields):
                raise ValueError(
                    f"Invalid 'lisan_fields' in {name}. Ensure all fields are defined.")  # noqa

            # Filter translatable fields by checking if they are
            # defined in lisan_fields
            translatable_fields = {
                key: value for key, value in attrs.items()
                if isinstance(value, models.Field) and key in lisan_fields
            }

            # Determine primary key type, checking model-specific
            # setting first, then global
            primary_key_type = attrs.get(
                'lisan_primary_key_type',  # Model-specific setting
                getattr(
                    settings,
                    'LISAN_PRIMARY_KEY_TYPE',
                    models.BigAutoField
                )
            )

            # Create the new model class
            new_class = super().__new__(cls, name, bases, attrs)

            # Generate the Lisan model
            lisan_model = create_lisan_model(
                new_class, translatable_fields, primary_key_type)
            setattr(new_class, 'Lisan', lisan_model)

        else:
            # Create the new model class if not using the mixin
            new_class = super().__new__(cls, name, bases, attrs)

        return new_class
