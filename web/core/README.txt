
# core (corrigido, sem duplicação de estáticos)

Este app está namespaced corretamente: **todos os assets** do `core` ficam em:
`core/static/core/...` e os templates já apontam para `{% static 'core/...'%}`.

## Evite duplicação no collectstatic
No seu `settings.py` do projeto *web*, **NÃO** inclua `core/static` em `STATICFILES_DIRS`.
Os estáticos de apps são encontrados automaticamente pelo `AppDirectoriesFinder`.

Exemplo seguro:
```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [ BASE_DIR / "static" ]  # apenas se existir uma pasta global web/static
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
```

Depois:
```bash
python manage.py collectstatic --noinput
python manage.py findstatic core/css/site.css -v 3  # deve listar UMA origem
```
