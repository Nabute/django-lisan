## [v0.1.6] - 2024-12-07

This release delivers significant improvements across the `Lisan` package, focusing on enhanced functionality, better error handling, and comprehensive test coverage. It introduces refined translation handling in `LisanModelMixin`, dynamic serializer validation, and robust admin inline management for multilingual data.

---

### **Added**

- **Admin Inline Support for Lisan Models**:
  - Dynamically identifies related `Lisan` models and adds inlines in the admin interface.
  - Enables seamless management of translations directly from the Django admin.

- **Dynamic Field Management in Serializers**:
  - `TranslationSerializer` and `LisanSerializerMixin` now dynamically handle `translations` fields based on request methods (`POST`, `PATCH`, etc.).
  - Early validation of translation fields halts processing on invalid data.

- **Synchronization of Translatable Fields in Updates**:
  - Translatable fields updated directly in the main model are now synchronized with their corresponding default language translations during `PATCH` and `PUT` operations, ensuring consistency in API responses.

- **Comprehensive Error Handling**:
  - Added explicit exceptions for:
    - Invalid field names (`FieldDoesNotExist`).
    - Unsupported language codes (`ValueError`).
    - Integrity issues (`IntegrityError`).
    - General exceptions in translation methods like `set_lisan`.

- **Improved Test Suite**:
  - Added 100% test coverage for `LisanModelMixin`, middleware, serializers, and admin functionalities.
  - Tests now validate behaviors such as:
    - Creation and update of translations.
    - Handling of duplicate and bulk translations.
    - Dynamic field inclusion in serializers.
    - Middleware fallback and validation.

---

### **Improved**

- **`set_lisan` Method**:
  - Replaces existing translations for the same language, avoiding duplicates.
  - Handles custom primary key configurations dynamically.
  - Improved field validation to ensure all `lisan_fields` exist in the `Lisan` model.

- **Bulk Translation Handling**:
  - `set_bulk_lisans` now supports a mix of updates and new translations for multiple languages in a single operation.

- **Middleware Enhancements**:
  - Refined `LanguageMiddleware` for better validation and fallback logic:
    - Prioritizes query parameters (`?lang=xx`), user profile preferences, cookies, and headers.
    - Ensures unsupported languages default to `LISAN_DEFAULT_LANGUAGE`.

- **Documentation**:
  - Enhanced docstrings for all key methods and classes.
  - Improved error messages for better debugging.

---

### **Fixed**

- **Admin Relationship Detection**:
  - Fixed issues with detecting reverse relationships between `Lisan` models and parent models in admin inlines.

- **Translation Field Validation**:
  - Prevented silent failures when invalid fields are passed to `set_lisan`.

- **Middleware Parsing**:
  - Addressed edge cases in `Accept-Language` header parsing, ensuring valid language selection.

---

### **Configuration Changes**

- No new settings were added in this release. Existing settings such as `LISAN_DEFAULT_LANGUAGE` and `LISAN_ALLOWED_LANGUAGES` continue to be integral for managing translations.

---

### **Example Usage**

- **Set a Translation**:
  ```python
  instance.set_lisan('am', title="አዲስ ሰላም", description="አስገራሚ መግለጫ")
  ```

- **Retrieve a Field with Fallback**:
  ```python
  title = instance.get_lisan_field('title', 'fr', fallback_languages=['en', 'am'])
  ```

- **Bulk Translation Update**:
  ```python
  translations = {
      'en': {'title': "New Title", 'description': "New Description"},
      'fr': {'title': "Nouveau Titre", 'description': "Nouvelle Description"}
  }
  instance.set_bulk_lisans(translations)
  ```

---

### **Future Plans**

- Add support for more advanced translation workflows, such as language auto-detection.
- Introduce caching mechanisms for translation retrieval.
- Expand support for admin inline customization and validation.

---

## [v0.1.5] - 2024-11-11

This release introduces two major enhancements to `Lisan`'s translation model functionality, improving flexibility in primary key configurations and structuring translation data for API responses.

### Added
- **Flexible Primary Key Configuration for Translation Tables**:
  - Added support to configure primary key type for translation (Lisan) tables, allowing the use of either `BigInt` or `UUID` as primary keys.
  - Configurable globally via `settings.py` (`LISAN_PRIMARY_KEY_TYPE`) or per model by setting the `lisan_primary_key_type` attribute.
  - Ensures flexibility for projects that require UUIDs or BigInts based on specific requirements or database configurations.

- **Nested Translation Serializer for Structured API Responses**:
  - Introduced a `TranslationSerializer` to handle multilingual data in API responses, providing a structured, nested format.
  - Integrated `TranslationSerializer` within `LisanSerializerMixin`, enabling organized representation of translations in API responses.
  - Allows each translation entry to include fields such as `language_code` and all specified translatable fields, making it easier to work with multilingual data in client applications.

### Improved
- **Dynamic Primary Key Assignment for Lisan Models**:
  - Enhanced the `LisanModelMeta` metaclass to detect and apply the specified primary key type dynamically, either at the model level or globally.
  - Ensured that the primary key type for Many-to-Many join tables remains `AutoField` even when the `Lisan` model uses `UUIDField` as its primary key, simplifying compatibility with Django’s default join tables.

### Configuration Changes
- **New Settings**:
  - `LISAN_PRIMARY_KEY_TYPE`: Allows configuration of the primary key type for translation tables globally. Options include `BigAutoField` (default) and `UUIDField`.

### Migration Notes
- A new migration is required if you change the primary key type for existing translation tables. After updating, use the following commands:

  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Example Usage

- **Primary Key Configuration**: Define primary key type globally in `settings.py` or per model:
  ```python
  # In settings.py
  LISAN_PRIMARY_KEY_TYPE = models.UUIDField

  # Per model configuration
  class MyModel(LisanModelMixin, models.Model):
      lisan_primary_key_type = models.UUIDField
  ```

- **Translation Serializer**: Access structured translation data in API responses with `TranslationSerializer`:
  ```json
  {
      "id": 1,
      "title": "Sample Title",
      "description": "Sample Description",
      "translations": [
          {
              "language_code": "am",
              "title": "ምሳሌ ርእስ",
              "description": "ምሳሌ መግለጫ"
          },
          {
              "language_code": "en",
              "title": "Sample Title",
              "description": "Sample Description"
          }
      ]
  }
  ```

---

## [v0.1.4] - 2024-10-07

This release introduces improvements in the translation validation process for partial updates, ensuring that translations are properly validated unless explicitly omitted in partial updates.

### Improved
- **Translation Validation for Partial Updates**:
  - Added logic to skip translation validation if no translation data is provided and the update is marked as a partial update. This ensures that translation validation does not unnecessarily block partial updates.
  - If the update is **not** partial, a `ValidationError` will be raised if translations are missing, ensuring consistency for full updates.

---

## [v0.1.3] - 2024-09-28

This release addresses a critical issue in the `Lisan` model where all fields from the main model were being included in the migration, even though only the fields defined in `lisan_fields` were expected to be migrated.

### Fixed
- **Resolved Migration Issue for Lisan Model**:
  - Fixed an issue where the `Lisan` model migrations included all fields from the main model instead of only those listed in the `lisan_fields` attribute.
  - The `LisanModelMeta` metaclass now correctly filters out fields that are not translatable based on the `lisan_fields` list, ensuring that only the intended fields are migrated.
  - Added validation to ensure that any model using `LisanModelMixin` must define `lisan_fields`. If `lisan_fields` is missing, an `AttributeError` is raised during model initialization.

### Improved
- **Automatic Field Filtering in Lisan Model**:
  - The dynamic `Lisan` model generation now strictly adheres to the `lisan_fields` specification, dynamically creating translation models with only the specified translatable fields.

### Migration Notes
- A new migration is required to fix the schema of previously generated migrations for the `Lisan` model. After upgrading, run the following commands:
  
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

---

## [v0.1.2] - 2024-09-23

This release focuses on refining the multilingual handling capabilities by introducing additional flexibility in language detection and ensuring compatibility with supported languages.

### Added
- **Enhanced Language Detection in Middleware**:
  - **Improved `LanguageMiddleware`**: The `LanguageMiddleware` now includes more robust language detection mechanisms:
    - It checks for the `lang` query parameter, user profile language preference, cookies, and the `Accept-Language` header in a prioritized manner.
    - Added support for configurable fallback languages via the `LISAN_DEFAULT_LANGUAGE` setting.
    - Introduced validation to ensure the selected language is within the list of supported languages, using the new `LISAN_ALLOWED_LANGUAGES` setting.
    - Refined the `Accept-Language` header parsing to handle complex header values and gracefully fallback when necessary.
  
  - **Support for Configurable Allowed Languages**: A new setting, `LISAN_ALLOWED_LANGUAGES`, has been added to specify the languages supported by the application. If a language from the request is not in this list, the middleware falls back to the default language.
  
### Configuration Changes
- **New Settings**:
  - `LISAN_ALLOWED_LANGUAGES`: A list of language codes that the application supports. The `LanguageMiddleware` ensures that only these languages are applied to the request. Defaults to `[LISAN_DEFAULT_LANGUAGE]`.

### Fixed
- Improved robustness in the `LanguageMiddleware` by ensuring safe access to user profile attributes and handling of missing or malformed `Accept-Language` headers.
- Prevented invalid language codes from being set on requests by validating against the new `LISAN_ALLOWED_LANGUAGES` setting.

### Migration Notes
No database migrations are required for this release. However, to take advantage of the new language validation features, developers should define `LISAN_ALLOWED_LANGUAGES` in `settings.py`.

---


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