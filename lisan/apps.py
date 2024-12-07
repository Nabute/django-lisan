from django.apps import AppConfig, apps
from django.db import models
from lisan.metaclasses import create_lisan_model


class LisanConfig(AppConfig):
    """
    The Django AppConfig for the Lisan package.

    This configuration class is responsible for setting up the Lisan models
    and establishing the necessary relationships for multilingual support
    when the application is ready.
    """
    name = 'lisan'

    def ready(self):
        """
        Called when the Django application is ready.

        This method iterates over all registered models in the Django project
        and checks if they use the `LisanModelMixin`. If a model has
        `lisan_fields` defined, a corresponding Lisan model is created and
        associated with the original model via a ManyToManyField relationship.
        """
        for model in apps.get_models():
            if hasattr(model, 'lisan_fields'):
                # Extract the fields intended for multilingual support
                lisan_fields = {
                    field: model._meta.get_field(field)
                    for field in model.lisan_fields
                }

                # Create the corresponding Lisan model dynamically
                lisan_model = create_lisan_model(model, lisan_fields)

                # Set the Lisan model as an attribute of the original model
                setattr(model, 'Lisan', lisan_model)

                # Add a ManyToManyField to associate the model with its Lisan
                model.add_to_class(
                    'lisans',
                    models.ManyToManyField(
                        lisan_model,
                        related_name=f"{model._meta.model_name}_lisans",
                        db_table=f"{model._meta.db_table}_to_lisan"
                    )
                )
