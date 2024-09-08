from django.test import TestCase
from lisan.mixins import LisanModelMixin
from django.db import models


class DummyModel(LisanModelMixin, models.Model):
    lisan_fields = ['title', 'description']
    title = models.CharField(max_length=255)
    description = models.TextField()


class LisanModelMixinTestCase(TestCase):
    def setUp(self):
        self.instance = DummyModel.objects.create(
            title="Test Title", description="Test Description")

    def test_set_lisan(self):
        self.instance.set_lisan(
            'es', title="Título de prueba",
            description="Descripción de prueba")
        lisan_instance = self.instance.get_lisan('es')
        self.assertIsNotNone(lisan_instance)
        self.assertEqual(lisan_instance.title, "Título de prueba")

    def test_get_lisan_field(self):
        self.instance.set_lisan('fr', title="Titre de test")
        title = self.instance.get_lisan_field('title', 'fr')
        self.assertEqual(title, "Titre de test")

    def test_fallback_to_default_language(self):
        self.instance.set_lisan('es', title="Título de prueba")
        title = self.instance.get_lisan_field('title', 'es')
        self.assertEqual(title, "Título de prueba")

    def test_no_translation_available(self):
        title = self.instance.get_lisan_field('title', 'de')
        self.assertEqual(title, "Test Title")

    def test_set_current_language(self):
        self.instance.set_current_language('fr')
        self.assertEqual(self.instance._current_language, 'fr')
