# Lisan - ልሳን

**means**: A language in Amharic (Ethiopian Language)

**Lisan** is a Django package that simplifies the process of adding translation support to model fields in Django projects. With `Lisan`, you can easily manage multilingual content within your Django models, API, and admin interface.

## Features

- **Automatic Translation Models:** Automatically generate translation models for your fields.
- **Flexible Primary Key Configuration:** Use either BigInt or UUID as primary keys for translation tables, configurable globally or per model.
- **Admin Integration:** Seamlessly manage translations through the Django admin interface.
- **Fallback Mechanism:** Fallback to the default language if a translation is not available.
- **Dynamic Getter Methods:** Automatically generate methods to access translated fields.
- **Pluggable Translation Services:** Support for external services like Google Translate to automatically translate content.
- **Customizable Admin Display:** Configure how translations are displayed in the Django admin interface.
- **Flexible Field Types:** Add translation support for various field types like `CharField`, `TextField`, and `JSONField`.
- **Synchronization of Translatable Fields:** Ensures consistency by automatically syncing main model updates with default language translations.


## Table of Contents

- [Installation](#installation)
- [Lisan Settings](#lisan-settings)
- [Usage](#usage)
  - [Adding Translation Support to Models](#1-adding-translation-support-to-models)
  - [Managing Translations in Django Admin](#2-managing-translations-in-django-admin)
  - [Accessing Translations in Code](#3-accessing-translations-in-code)
  - [Synchronization of Updates](#4-synchronization-of-updates)
- [API Usage](#api-usage)
  - [Creating a Snippet with Translations](#1-creating-a-snippet-with-translations)
  - [Retrieving a Snippet with a Specific Translation](#2-retrieving-a-snippet-with-a-specific-translation)
  - [Handling User Preferences for Translations](#handling-user-preferences-for-translations)
- [Pluggable Translation Services](#pluggable-translation-services)
  - [Creating Custom Translation Services](#creating-custom-translation-services)
- [Testing Translations](#testing-translations)
- [Contributing](#contributing)
- [License](#license)

## Installation

You can install Lisan via pip:

```bash
pip install lisan
```

## Lisan Settings

### 1. Configuring Lisan

To start using `Lisan` in your project, configure the language settings, middleware, and primary key type (if needed) in your Django settings file.

#### Step 1.0: Add Lisan Language Settings

```python
LISAN_DEFAULT_LANGUAGE = 'en'  # Default language for translations
LISAN_ALLOWED_LANGUAGES = ['en', 'am', 'or', 'tg']  # Languages supported by Lisan
LISAN_FALLBACK_LANGUAGES = ['fr', 'es', 'en']  # Customize fallback languages
LISAN_DEFAULT_TRANSLATION_SERVICE = 'yourapp.google_translate_service.GoogleTranslateService'  # Pluggable translation service
```

#### Step 1.1: Configure Primary Key Type (Optional)

You can configure `Lisan` to use either `BigInt` or `UUID` as the primary key for translation tables. 

To set this globally, use the `LISAN_PRIMARY_KEY_TYPE` setting in `settings.py`:

```python
from django.db import models
LISAN_PRIMARY_KEY_TYPE = models.UUIDField  # Options: models.BigAutoField (default) or models.UUIDField
```

Alternatively, define `lisan_primary_key_type` on specific models to override the global setting.

#### Step 1.2: Add Lisan Middleware

Make sure to include `Lisan`'s middleware in your `MIDDLEWARE` settings for automatic language detection and management:

```python
MIDDLEWARE = [
    ...
    'lisan.middleware.LanguageMiddleware',  # Lisan middleware for handling language preferences
    'django.middleware.common.CommonMiddleware',
    ...
]
```

## Usage

### 1. Adding Translation Support to Models

To add translation support to a model, simply inherit from `LisanModelMixin` and specify which fields should be translatable using the `lisan_fields` attribute.

Example:

```python
from django.db import models
from lisan import LisanModelMixin

class Snippet(LisanModelMixin, models.Model):
    lisan_fields = ['title', 'description']  # Fields to be translated
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    # Optionally specify UUIDField as primary key for translation tables
    lisan_primary_key_type = models.UUIDField

    class Meta:
        ordering = ['created']
```

Once the model is defined, run the following commands to create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Managing Translations in Django Admin

To enable translation management in the Django admin, use `LisanAdminMixin` in your admin class.

Example:

```python
from django.contrib import admin
from lisan import LisanAdminMixin
from .models import Snippet

@admin.register(Snippet)
class SnippetAdmin(LisanAdminMixin, admin.ModelAdmin):
    list_filter = ('created',)
    ordering = ('-created',)
    lisan_display_format = "{field_name} ({language_code})"  # Customizable admin display format
```

### 3. Accessing Translations in Code

You can set and get translations using the provided methods.

#### Setting a Translation

```python
snippet = Snippet.objects.create(title="Code Snippet Example", description="Example Description")
snippet.set_lisan('am', title="ኮድ ቅርጸት ምሳሌ", description="እንቁ ምሳሌ")
```

#### Getting a Translation with Fallback and Auto-Translate

You can retrieve translations with a fallback mechanism or even auto-translate content using an external service.

```python
amharic_title = snippet.get_lisan_field('title', 'am', auto_translate=True)
print(amharic_title)  # Output: ኮድ ቅርጸት ምሳሌ (if available) or the auto-translated version

english_title = snippet.get_lisan_field('title', 'en')
print(english_title)  # Output: Code Snippet Example
```

---

### 4. Synchronization of Updates

When updating translatable fields directly in the main model, Lisan ensures synchronization with the default language translation automatically.

#### Example

**Request**:

```http
PATCH /api/snippets/1/
Accept-Language: en
Content-Type: application/json

{
    "title": "Updated Snippet Title"
}
```

**Behavior**:

- Updates the `title` field in the main model.
- Synchronizes the updated value with the `en` translation.

**Response**:

```json
{
    "id": 1,
    "title": "Updated Snippet Title",
    "translations": [
        {
            "language_code": "en",
            "title": "Updated Snippet Title",
            "description": "Existing description"
        },
        {
            "language_code": "am",
            "title": "ኮድ ቅርጸት ምሳሌ",
            "description": "እንቁ ምሳሌ"
        }
    ]
}
```

---

## API Usage

Here is how to use the API to create and retrieve a translated snippet.

### 1. Creating a Snippet with Translations

To create a snippet with translations, send a `POST` request to the appropriate API endpoint with the following payload:

**Request Body**:

```json
{
    "title": "Code Snippet Example",
    "description": "Example Description",
    "translations": [
        {
            "language_code": "am",
            "title": "ኮድ ቅርጸት ምሳሌ",
            "description": "እንቁ ምሳሌ"
        }
    ]
}
```

### 2. Retrieving a Snippet with Translations Using Nested Translation Serializer

To retrieve translations for a snippet, use the `TranslationSerializer` to structure the translations in a nested format.

**Request Example**:

```http
GET /api/snippets/1/
Accept-Language: am
```

The response will include all translations for the snippet in a structured format:

**Response Example**:

```json
{
    "id": 1,
    "title": "Code Snippet Example",
    "description": "Example Description",
    "translations": [
        {
            "language_code": "am",
            "title": "ኮድ ቅርጸት ምሳሌ",
            "description": "እንቁ ምሳሌ"
        },
        {
            "language_code": "en",
            "title": "Code Snippet Example",
            "description": "Example Description"
        }
    ]
}
```

### Handling User Preferences for Translations

You can dynamically handle user preferences for translations based on the `Accept-Language` header or custom user settings.

```python
class SnippetSerializer(LisanSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ['id', 'title', 'description']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        language_code = request.headers.get('Accept-Language', 'en')
        representation['title'] = instance.get_lisan_field('title', language_code)
        return representation
```

## Pluggable Translation Services

The `Lisan` package supports pluggable translation services, allowing you to integrate with third-party APIs like Google Translate for automatic translations. You can configure this via the `LISAN_DEFAULT_TRANSLATION_SERVICE` setting.

### Creating Custom Translation Services

You can create custom translation services by implementing the `BaseTranslationService` class.

Example using Google Translate:

```python
# google_translate_service.py
from googletrans import Translator
from lisan.translation_services import BaseTranslationService

class GoogleTranslateService(BaseTranslationService):
    def __init

__(self):
        self.translator = Translator()

    def translate(self, text, target_language):
        return self.translator.translate(text, dest=target_language).text
```

### Setting up the Service

To configure your application to use this service, simply set it in the `LISAN_DEFAULT_TRANSLATION_SERVICE` setting in `settings.py`:

```python
LISAN_DEFAULT_TRANSLATION_SERVICE = 'yourapp.google_translate_service.GoogleTranslateService'
```

## Testing Translations

To ensure that your translations are handled correctly, here’s an example of how you can write tests for translated fields:

```python
from django.test import TestCase
from .models import Snippet

class SnippetTestCase(TestCase):
    def setUp(self):
        self.snippet = Snippet.objects.create(title="Hello World", description="Description Example")

    def test_translation_set(self):
        self.snippet.set_lisan('fr', title="Bonjour le monde", description="Exemple de description")
        self.assertEqual(self.snippet.get_lisan_field('title', 'fr'), "Bonjour le monde")

    def test_fallback(self):
        # Test that it falls back to English if no French translation is available
        self.assertEqual(self.snippet.get_lisan_field('title', 'fr'), "Hello World")
```

This testing structure ensures that your translations work as expected, using both direct translations and fallback mechanisms when translations are unavailable.

## Contributing

If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on GitHub. Contributions are always welcome.

## License

Lisan is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.