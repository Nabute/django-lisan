from importlib import import_module
from django.conf import settings


def get_translation_service():
    """
    Dynamically import and instantiate the translation service class defined 
    in the settings.

    This function assumes that the `LISAN_DEFAULT_TRANSLATION_SERVICE` setting
    is a fully qualified Python path string in the format 'module.ClassName'.

    The module and class name are extracted from this setting, and the class
    is imported dynamically. The class is then instantiated and returned.

    Returns:
        object: An instance of the translation service class as defined in
                the settings.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the class is not found within the module.
    """
    # Split the module path and class name from the settings
    module_path, class_name = settings.LISAN_DEFAULT_TRANSLATION_SERVICE.rsplit('.', 1)  # noqa: E501

    # Import the module dynamically
    module = import_module(module_path)

    # Retrieve the class from the imported module
    service_class = getattr(module, class_name)

    # Instantiate and return the translation service class
    return service_class()
