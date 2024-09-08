from django.test import TestCase
from lisan.serializers import LisanSerializerMixin
from rest_framework import serializers
from django.db import models
from rest_framework.exceptions import ValidationError
from lisan.mixins import LisanModelMixin


class DummyModel(LisanModelMixin):
    lisan_fields = ['title', 'description']
    title = models.CharField(max_length=255)
    description = models.TextField()


class DummyModelSerializer(LisanSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DummyModel
        fields = '__all__'


class LisanSerializerMixinTestCase(TestCase):
    def setUp(self):
        self.instance = DummyModel.objects.create(
            title="Test Title", description="Test Description")
        self.serializer = DummyModelSerializer(instance=self.instance)

    def test_to_representation(self):
        data = self.serializer.to_representation(self.instance)
        self.assertIn('title', data)
        self.assertEqual(data['title'], "Test Title")

    def test_create_with_translations(self):
        data = {
            'title': 'New Title',
            'description': 'New Description',
            'translations': [{'language_code': 'es', 'title': 'Nuevo Título'}]
        }
        serializer = DummyModelSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.get_lisan_field(
            'title', 'es'), 'Nuevo Título')

    def test_update_with_translations(self):
        data = {
            'title': 'Updated Title',
            'translations': [
                {'language_code': 'fr', 'title': 'Titre Mis à Jour'}]
        }
        serializer = DummyModelSerializer(instance=self.instance, data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.title, 'Updated Title')
        self.assertEqual(instance.get_lisan_field(
            'title', 'fr'), 'Titre Mis à Jour')

    def test_missing_translation_fields(self):
        data = {
            'title': 'Another Title',
            'translations': [{'language_code': 'de'}]
        }
        serializer = DummyModelSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
