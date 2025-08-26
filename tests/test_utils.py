from importlib import import_module
from unittest.mock import patch

from django.test import TestCase

from lisan.utils import get_translation_service
from tests.google_translate_service import GoogleTranslateService


class TestGetTranslationService(TestCase):
    """Verify that the translation service is instantiated only once."""

    def setUp(self):
        get_translation_service.cache_clear()

    def tearDown(self):
        get_translation_service.cache_clear()

    def test_service_created_only_once(self):
        """Subsequent calls should reuse the same service instance."""
        with patch(
            'lisan.utils.import_module', wraps=import_module
        ) as mock_import, patch.object(
            GoogleTranslateService,
            '__init__',
            wraps=GoogleTranslateService.__init__,
            autospec=True,
        ) as mock_init:
            service1 = get_translation_service()
            service2 = get_translation_service()

            self.assertIs(service1, service2)
            self.assertEqual(mock_import.call_count, 1)
            self.assertEqual(mock_init.call_count, 1)
