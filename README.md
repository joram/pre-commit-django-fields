# Pre-commit Django Fields
this pre-commit plugin is a single hook to validate django classes have expected fields on them.

## Usage
in your `.pre-commit-config.yaml` file add the following:

```yaml
-   repo: https://github.com/joram/pre-commit-django-fields
    rev: v1.0.23
    hooks:
    -   id: pre-commit-django-fields
        language_version: python3
```