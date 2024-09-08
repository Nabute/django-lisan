from django.db import models
from django.utils.translation import gettext_lazy as _


def create_lisan_model(model_cls, fields):
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
        unique_together = ('language_code', model_cls._meta.pk.name)
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

    # Add the specified fields to the Lisan model
    for field_name, field in fields.items():
        attrs[field_name] = field

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
        # Gather the fields intended for Lisan support
        lisan_fields = {
            key: value for key, value in attrs.items()
            if isinstance(value, models.Field)
        }

        # Create the new model class
        new_class = super().__new__(cls, name, bases, attrs)

        # If the new class includes LisanModelMixin, generate the Lisan model
        if 'LisanModelMixin' in [base.__name__ for base in bases]:
            lisan_model = create_lisan_model(new_class, lisan_fields)
            setattr(new_class, 'Lisan', lisan_model)

            # Add a ManyToManyField linking the original model to
            # the Lisan model
            new_class.add_to_class(
                'lisans',
                models.ManyToManyField(
                    lisan_model,
                    related_name="+",
                    blank=True,
                )
            )

        return new_class
