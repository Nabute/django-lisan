Here's the updated README with a more detailed example, incorporating how you've used `Lisan` in your project:

---

# Django Lisan

**Django Lisan** is a Django package that simplifies the process of adding translation support to model fields in Django projects. With `Lisan`, you can easily manage multilingual content within your Django models and admin interface.

## Features

- **Automatic Translation Models:** Automatically generate translation models for your fields.
- **Admin Integration:** Seamlessly manage translations through the Django admin interface.
- **Fallback Mechanism:** Fallback to the default language if a translation is not available.
- **Dynamic Getter Methods:** Automatically generate methods to access translated fields.

## Installation

You can install Django Lisan via pip:

```bash
pip install django-lisan
```

## Usage

### 1. Adding Translation Support to Models

To add translation support to a model, simply inherit from `LisanModelMixin` and specify which fields should be translatable using the `lisan_fields` attribute.

Example:

```python
from django.db import models
from lisan import LisanModelMixin
from django.utils.translation import gettext_lazy as _

class BranchOffice(LisanModelMixin, models.Model):
    lisan_fields = ['name', 'address']

    name = models.CharField(max_length=256, verbose_name=_("name"))
    address = models.CharField(max_length=256, verbose_name=_("address"))

    class Meta:
        verbose_name = _("branch office")
        verbose_name_plural = _("branch offices")
        ordering = ("-created_at",)
        db_table = "branch_offices"

    def __str__(self):
        return self.name
```

### 2. Managing Translations in Django Admin

To enable translations management in the Django admin, use `LisanAdminMixin` in your admin class.

Example:

```python
from django.contrib import admin
from lisan import LisanAdminMixin
from .models import BranchOffice

@admin.register(BranchOffice)
class BranchOfficeAdmin(LisanAdminMixin, admin.ModelAdmin):
    list_filter = ('created_at',)
    ordering = ('-created_at',)
```

### 3. Accessing Translations in Code

You can set and get translations (lisans) using the provided methods.

#### Setting a Translation

Example:

```python
office = BranchOffice.objects.create(name="Main Office", address="123 Main St")
office.set_lisan('am', name="ቆልፌ ቀራኒዮ ክፍለ ከተማ", address="123 ዋና መንገድ")
```

#### Getting a Translation

Example:

```python
amharic_name = office.get_lisan_field('name', 'am')
print(amharic_name)  # Output: ቆልፌ ቀራኒዮ ክፍለ ከተማ

english_name = office.get_lisan_field('name', 'en')
print(english_name)  # Output: Main Office
```

### 4. Handling Languages and Fallbacks

Lisan provides a fallback mechanism for when a translation is not available in the requested language:

Example:

```python
default_name = office.get_lisan_field('name', 'fr', fallback_to_default=True)
print(default_name)  # Fallbacks to the default language (English) if French is not available.
```

### 5. Using Lisan in Views and Serializers

You can integrate `Lisan` with Django REST framework by using `LisanSerializerMixin` in your serializers. Here’s how you can implement it:

#### Serializers Example:

```python
from rest_framework import serializers
from lisan import LisanSerializerMixin
from .models import BranchOffice

class BranchOfficeResponseSerializer(LisanSerializerMixin, serializers.ModelSerializer):
    object_state = DataLookupSerializer()
    created_by = UserSerializer()

    class Meta:
        model = BranchOffice
        fields = ['id', 'name', 'address', 'object_state', 'created_by', 'created_at', 'updated_at']

class BranchOfficeSerializer(LisanSerializerMixin):
    class Meta:
        model = BranchOffice
        fields = ['id', 'name', 'address', 'object_state']

    def to_representation(self, instance):
        return BranchOfficeResponseSerializer(instance, context=self.context).to_representation(instance)

    def create(self, validated_data):
        auth_user = self.context['request'].user

        if not validated_data.get('object_state'):
            validated_data["object_state"] = DataLookup.objects.get(
                type=ObjectStateType.TYPE.value,
                is_default=True
            )

        validated_data["created_by"] = auth_user
        return super().create(validated_data)
```

#### ViewSet Example:

```python
from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BranchOfficeSerializer, BranchOfficeResponseSerializer
from .models import BranchOffice

@extend_schema(responses=BranchOfficeResponseSerializer)
class BranchOfficeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, BranchOfficeAccessPolicy]
    serializer_class = BranchOfficeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        return self.permission_classes[1].scope_queryset(self.request, BranchOffice.objects.all())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
```

### Summary

This `README.md` provides a comprehensive overview of the `django-lisan` package, including installation, configuration, and usage instructions. It’s designed to be user-friendly and informative, helping users get started with the package quickly.

## Contributing

If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on GitHub.

## License

Django Lisan is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

This updated README includes practical examples of how `Lisan` can be integrated into a Django project, from models to admin and serializers. The added sections should provide users with a clear and detailed guide on using `Lisan` effectively in their projects.