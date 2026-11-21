#!/bin/sh
set -e

echo " Veritabanı migrasyonları uygulanıyor..."
python manage.py migrate --noinput

echo " Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput --clear || true

echo " Başlangıç soru havuzu (9 kategori, 180 soru) yükleniyor..."
python manage.py seed_quiz_data || python manage.py loaddata quiz_api/fixtures/initial_questions.json || true

echo " Gunicorn sunucusu başlatılıyor..."
exec gunicorn rapid_quiz_core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
