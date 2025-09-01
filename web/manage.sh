#!/usr/bin/env bash
set -euo pipefail
python manage.py collectstatic --noinput || true
exec python manage.py "$@"
