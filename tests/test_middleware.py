from django.test import TestCase, RequestFactory
from django.conf import settings
from unittest.mock import MagicMock, Mock
from lisan.middleware import LanguageMiddleware


class TestLanguageMiddleware(TestCase):
    """
    Test suite for the LanguageMiddleware class, which sets the language
    code on the request object based on various input sources.
    """

    def setUp(self):
        """
        Set up the test environment, including the middleware instance
        and request factory.
        """
        self.factory = RequestFactory()
        self.middleware = LanguageMiddleware(get_response=Mock())

        # Set test settings for language configuration
        settings.LISAN_DEFAULT_LANGUAGE = 'en'
        settings.LISAN_ALLOWED_LANGUAGES = ['en', 'am', 'or', 'tg']

    def test_language_from_get_parameter(self):
        """
        Test that the middleware extracts the language code from the 'lang'
        GET parameter.
        """
        request = self.factory.get('/?lang=am')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'am')

    def test_language_from_user_profile(self):
        """
        Test that the middleware extracts the language code from the user's
        profile preference if available.
        """
        mock_user = MagicMock()
        mock_user.profile.language_preference = 'or'
        request = self.factory.get('/')
        request.user = mock_user

        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'or')

    def test_language_from_cookie(self):
        """
        Test that the middleware extracts the language code from cookies.
        """
        request = self.factory.get('/')
        request.COOKIES['language'] = 'tg'

        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'tg')

    def test_language_from_accept_language_header(self):
        """
        Test that the middleware extracts the language code from the
        'Accept-Language' header.
        """
        request = self.factory.get('/', HTTP_ACCEPT_LANGUAGE='am, en;q=0.8')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'am')

    def test_fallback_to_default_language(self):
        """
        Test that the middleware falls back to the default language when no
        language source is available or valid.
        """
        request = self.factory.get('/')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'en')

    def test_unsupported_language(self):
        """
        Test that the middleware falls back to the default language when an
        unsupported language is specified.
        """
        request = self.factory.get('/?lang=unsupported_language')
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'en')

    def test_parse_accept_language_valid_header(self):
        """
        Test that parse_accept_language correctly extracts the primary language
        from a valid 'Accept-Language' header.
        """
        result = self.middleware.parse_accept_language('am, en;q=0.8')
        self.assertEqual(result, 'am')

    def test_parse_accept_language_empty_header(self):
        """
        Test that parse_accept_language returns None for an empty or missing
        'Accept-Language' header.
        """
        result = self.middleware.parse_accept_language('')
        self.assertIsNone(result)

        result = self.middleware.parse_accept_language(None)
        self.assertIsNone(result)

    def test_parse_accept_language_malformed_header(self):
        """
        Test that parse_accept_language gracefully handles malformed headers.
        """
        result = self.middleware.parse_accept_language(';;;')
        self.assertIsNone(result)

    def test_language_precedence(self):
        """
        Test that the middleware applies the correct precedence when
        multiple language sources are available.
        """
        mock_user = MagicMock()
        mock_user.profile.language_preference = 'or'
        request = self.factory.get('/?lang=am', HTTP_ACCEPT_LANGUAGE='tg')
        request.user = mock_user
        request.COOKIES['language'] = 'tg'

        # GET parameter should take precedence
        self.middleware.process_request(request)
        self.assertEqual(request.language_code, 'am')

    def test_parse_accept_language_no_languages_extracted(self):
        """
        Test that parse_accept_language returns None when the header
        is provided but no valid languages can be extracted.
        """
        # Header with only commas (no valid languages)
        result = self.middleware.parse_accept_language(',,,')
        self.assertIsNone(result)

        # Header with malformed values that result in empty language codes
        result = self.middleware.parse_accept_language(' , ; , ; ')
        self.assertIsNone(result)
