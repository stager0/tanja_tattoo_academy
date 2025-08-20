#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Loading vital fixture data..."
python manage.py loaddata fixture_tariffs.json

echo "Setting Telegram webhook..."
python manage.py shell -c "from web.telegram_bot import set_telegram_webhook; set_telegram_webhook()"

echo "Starting Gunicorn server..."
exec gunicorn tattoo_academy.wsgi:application --bind 0.0.0.0:8000