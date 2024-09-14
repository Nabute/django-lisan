## [v0.1.1] - 2024-09-14

This version brings enhanced flexibility, making the `lisan` package highly adaptable for multilingual projects by enabling external services for automated translations while maintaining a customizable architecture.

### Added
- **Pluggable Translation Service**: Introduced a base `BaseTranslationService` class, allowing easy integration of third-party or custom translation services.
  - Added an example implementation with `GoogleTranslateService` using Google’s translation API.
  - Enabled dynamic loading of translation services via Django settings (`LISAN_DEFAULT_TRANSLATION_SERVICE`).
  
- **Auto-Translation Support**: 
  - Added an `auto_translate` option to `get_lisan_field` in `LisanModelMixin`, enabling automatic translation fallback when specific language translations are missing.
  - Added auto-translation support in serializers and admin displays for models with translatable fields.

- **Bulk Translation Operations**: Added `set_bulk_lisans` method to support creating or updating translations for multiple languages in bulk.

- **Flexible Field Types**: Enhanced support for additional field types, such as `TextField`, `JSONField`, and more, in translatable models.

- **Customizable Admin Display**: 
  - Introduced `lisan_display_format` for customizing how translated fields appear in the Django admin interface.
  
- **Middleware Improvement**: Enhanced `LanguageMiddleware` to support multiple language detection sources, including query parameters (`?lang=xx`), cookies, and user profile settings.

### Fixed
- Improved fallback language handling for missing translations, with a new configuration (`LISAN_FALLBACK_LANGUAGES`) allowing developers to define custom fallback hierarchies.

### Configuration Changes
- **New Settings**: 
  - `LISAN_DEFAULT_TRANSLATION_SERVICE`: Configure the default translation service dynamically.
  - `LISAN_FALLBACK_LANGUAGES`: Customize fallback languages in case a specific translation is missing.

---

### Migration Notes
No database migrations are required for this release, but additional configuration in `settings.py` may be necessary to leverage new features like auto-translation and pluggable services.

---

### Future Plans
- Introduce caching for external translation service results to minimize API calls.
- Add support for other translation services such as DeepL and Microsoft Translator.
- Improve manual translation management in the Django admin interface.