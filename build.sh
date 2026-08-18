#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
echo "=== DEBUG: checking for duplicate management commands ==="
find . -iname "*collectstatic*"
echo "=== DEBUG: finders ==="
python manage.py findstatic shorp/css/style.css --verbosity 2
echo "=== DEBUG: collectstatic verbose ==="
python manage.py collectstatic --no-input --verbosity 3
python manage.py migrate