from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class LanguageMiddleware(MiddlewareMixin):
    """
    Middleware to extract the 'Accept-Language' header from the request
    and set the language code in the request object.

    If the 'Accept-Language' header is not present, the language code
    defaults to the value of 'LISAN_DEFAULT_LANGUAGE' from settings, or
    'en' if that setting is not defined.
    """

    def process_request(self, request):
        """
        Process the incoming request to set the language code.

        This method extracts the 'Accept-Language' header from the request
        headers and assigns it to `request.language_code`. If the header is
        not present, the language code defaults to the value specified by
        the `LISAN_DEFAULT_LANGUAGE` setting, or 'en' if that setting is
        not configured.

        Args:
            request: The HTTP request object.
        """
        # Fetch the default language from settings, fallback to 'en'
        default_language = getattr(settings, 'LISAN_DEFAULT_LANGUAGE', 'en')
        supported_language = getattr(
            settings, 'LISAN_ALLOWED_LANGUAGES', [default_language])

        # Safe retrieval of user profile language preference
        language_preference = None
        if hasattr(request, 'user') and hasattr(
                request.user, 'profile') and hasattr(
                    request.user.profile, 'language_preference'):
            language_preference = request.user.profile.language_preference

        # Extract the language code in order of precedence
        language_code = (
            request.GET.get('lang') or
            language_preference or
            request.COOKIES.get('language') or
            self.parse_accept_language(
                request.headers.get('Accept-Language')) or
            default_language
        )

        # Validate against supported languages
        if language_code not in supported_language:
            language_code = default_language

        # Set the language code on the request object
        request.language_code = language_code

    def parse_accept_language(self, accept_language_header):
        """
        Parse the 'Accept-Language' header and extract the first language code.
        If the header is malformed or empty, return None.

        Args:
            accept_language_header: The value of the 'Accept-Language' header.

        Returns:
            A string representing the best matched language code, or None
            if not found.
        """
        if not accept_language_header:
            return None

        # Split on commas and take the first part before any semicolon
        languages = accept_language_header.split(',')
        if languages:
            primary_language = languages[0].split(';')[0].strip()
            return primary_language if primary_language else None

        return None
