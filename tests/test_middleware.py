from django.test import TestCase, RequestFactory
from lisan.middleware import LanguageMiddleware
from django.conf import settings


class LanguageMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LanguageMiddleware()

    def test_language_set_from_header(self):
        request = self.factory.get('/test/', HTTP_ACCEPT_LANGUAGE='es')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'es')

    def test_language_fallback(self):
        settings.LISAN_DEFAULT_LANGUAGE = 'fr'
        request = self.factory.get('/test/')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'fr')

    def test_language_default_fallback(self):
        del settings.LISAN_DEFAULT_LANGUAGE
        request = self.factory.get('/test/')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'en')
