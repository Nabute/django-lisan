# Lisan - ልሳን

**means**: A language

**Lisan** is a Django package that simplifies the process of adding translation support to model fields in Django projects. With `Lisan`, you can easily manage multilingual content within your Django models, API, and admin interface.

## Features

- **Automatic Translation Models:** Automatically generate translation models for your fields.
- **Admin Integration:** Seamlessly manage translations through the Django admin interface.
- **Fallback Mechanism:** Fallback to the default language if a translation is not available.
- **Dynamic Getter Methods:** Automatically generate methods to access translated fields.

## Installation

You can install Lisan via pip:

```bash
pip install lisan
```

## Lisan Settings

### 1. Configuring Lisan

To start using `Lisan` in your project, you need to configure the language settings and middleware in your Django settings file.

#### Step 1.0: Add Lisan Language Settings

```python
LISAN_DEFAULT_LANGUAGE = 'en'  # Default language for translations
LISAN_ALLOWED_LANGUAGES = ['en', 'am', 'or', 'tg']  # Languages supported by Lisan
```

#### Step 1.1: Add Lisan Middleware

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
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from lisan import LisanModelMixin

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

# Add the LisanModelMixin mixin
class Snippet(LisanModelMixin, models.Model):
    lisan_fields = ['title', 'language', 'style']  # Fields to be translated

    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

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
```

### 3. Accessing Translations in Code

You can set and get translations using the provided methods.

#### Setting a Translation

```python
snippet = Snippet.objects.create(title="Code Snippet Example", code="def example_function():\n    return 'Hello, World!'")
snippet.set_lisan('am', title="ኮድ ቅርጸት ምሳሌ")
```

#### Getting a Translation

You can retrieve translations with a fallback mechanism. For example, if a translation in Amharic is not available, it will default to the base language (e.g., English).

```python
amharic_title = snippet.get_lisan_field('title', 'am')
print(amharic_title)  # Output: ኮድ ቅርጸት ምሳሌ

english_title = snippet.get_lisan_field('title', 'en')
print(english_title)  # Output: Code Snippet Example
```

## API Usage

Here is how to use the API to create and retrieve a translated snippet.

### 1. Creating a Snippet with Translations

To create a snippet with translations, send a `POST` request to the appropriate API endpoint with the following payload:

**Request Body**:

```json
{
    "title": "Code Snippet Example",
    "code": "def example_function():\n    return 'Hello, World!'",
    "linenos": true,
    "language": "python",
    "style": "friendly",
    "translations": [
        {
            "language_code": "en",
            "title": "Code Snippet Example",
            "language": "python",
            "style": "friendly"
        },
        {
            "language_code": "am",
            "title": "ኮድ ቅርጸት ምሳሌ",
            "language": "ፒያዝ",
            "style": "ወዳጅ"
        },
        {
            "language_code": "or",
            "title": "Miseensa Koodii Fakkeenya",
            "language": "python",
            "style": "bareedaa"
        },
        {
            "language_code": "tg",
            "title": "ምሳሌ ውሂብ ቅርጸት",
            "language": "python",
            "style": "ናብኣይ"
        }
    ]
}
```

### 2. Retrieving a Snippet with a Specific Translation

To retrieve a snippet in a specific language, send a `GET` request with the appropriate `Accept-Language` header to specify the desired language (e.g., `am` for Amharic, `or` for Oromo).

**Request Example**:

```http
GET /api/snippets/1/
Accept-Language: am
```

The response will return the snippet information in the requested language if available, or it will fallback to the default language:

**Response Example**:

```json
{
    "id": 1,
    "title": "ኮድ ቅርጸት ምሳሌ",
    "code": "def example_function():\n    return 'Hello, World!'",
    "linenos": true,
    "language": "ፒያዝ",
    "style": "ወዳጅ"
}
```

### 3. Serializer for Snippets

Use `LisanSerializerMixin` in your serializer to handle translations.

```python
from rest_framework import serializers
from lisan.serializers import LisanSerializerMixin
from .models import Snippet

class SnippetSerializer(LisanSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ['id', 'title', 'code', 'linenos', 'language', 'style']
```

### 4. Snippet ViewSet

Define your `SnippetViewSet` and make sure to pass the request to the serializer context for handling language-specific responses.

```python
from rest_framework import viewsets
from .models import Snippet
from .serializers import SnippetSerializer

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def get_serializer_context(self):
        """
        Adds custom context to the serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request  # Pass request context for translation handling
        return context
```

### Summary

This `README.md` provides a comprehensive overview of the `lisan` package, including settings, installation, configuration, and usage instructions. It covers how to create and retrieve translations for Django models and includes API examples for managing translated content.

## Contributing

If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on GitHub.

## License

Lisan is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
