#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
echo "=== DEBUG: checking static folder ==="
find . -name "style.css" -not -path "*/node_modules/*"
echo "=== DEBUG: settings STATIC config ==="
python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','Remise.settings'); django.setup(); from django.conf import settings; print('STATICFILES_DIRS:', getattr(settings, 'STATICFILES_DIRS', 'NOT SET')); print('INSTALLED_APPS:', settings.INSTALLED_APPS); print('STATIC_ROOT:', settings.STATIC_ROOT)"
echo "=== DEBUG: finders ==="
python manage.py findstatic shorp/css/style.css --verbosity 2
python manage.py collectstatic --no-input
python manage.py migrate