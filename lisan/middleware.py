from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


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
        language_code = request.headers.get(
            'Accept-Language',
            getattr(settings, 'LISAN_DEFAULT_LANGUAGE', 'en')
        )
        request.language_code = language_code
