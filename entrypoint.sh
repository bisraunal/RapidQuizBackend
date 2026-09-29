#!/bin/sh
set -e

echo " Veritabanı migrasyonları uygulanıyor..."
python manage.py migrate --noinput

echo " Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput --clear || true

echo " Başlangıç soru havuzu (fixtures) yükleniyor..."
python manage.py loaddata quiz_api/fixtures/initial_questions.json || true

echo " Gunicorn sunucusu başlatılıyor..."
exec gunicorn rapid_quiz_core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
