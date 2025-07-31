#!/bin/sh

if [ -z "$NGROK_AUTHTOKEN" ]; then
  echo "Ошибка: Переменная окружения NGROK_AUTHTOKEN не установлена."
  exit 1
fi

ngrok config add-authtoken $NGROK_AUTHTOKEN

echo "Запускаем ngrok..."
ngrok http 8000 --log=stdout > /dev/null &

sleep 5

NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | sed 's/"public_url":"//')
HOST=$(echo $NGROK_URL | sed 's|https://||')

if [ -z "$NGROK_URL" ]; then
  echo "Не удалось получить URL от ngrok. Проверьте логи."
  exit 1
fi

echo "Ngrok запущен:"
echo "URL_BASE=${NGROK_URL}"
echo "HOST=${HOST}"

if [ -f ".env" ]; then
    if grep -q "URL_BASE=" .env; then
        sed -i "s|URL_BASE=.*|URL_BASE=${NGROK_URL}|" .env
    else
        echo "\nURL_BASE=${NGROK_URL}" >> .env
    fi
    if grep -q "HOST=" .env; then
        sed -i "s|HOST=.*|HOST=${HOST}|" .env
    else
        echo "\nHOST=${HOST}" >> .env
    fi
    echo ".env файл обновлен."
fi

echo "Применяем миграции..."
python manage.py migrate

echo "Устанавливаем Telegram webhook..."
python manage.py shell -c "from web.views.telegram_bot import set_telegram_webhook; set_telegram_webhook()"
# ------------------------------------

echo "Запускаем основной процесс..."
exec "$@"