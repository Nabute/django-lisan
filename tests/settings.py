from django.db import models

SECRET_KEY = 'some-secret-key'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'tests',  # Include the tests module if it contains models
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Lisan Settings
LISAN_DEFAULT_LANGUAGE = 'en'
LISAN_ALLOWED_LANGUAGES = ['en', 'am', 'or', 'tg']
LISAN_PRIMARY_KEY_TYPE = models.UUIDField
LISAN_DEFAULT_TRANSLATION_SERVICE = 'tests.google_translate_service.GoogleTranslateService' # noqa

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'lisan.middleware.LanguageMiddleware',
]
