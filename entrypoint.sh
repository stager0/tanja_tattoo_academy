#!/bin/sh

# Check if the NGROK_AUTHTOKEN environment variable is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
  echo "Error: The NGROK_AUTHTOKEN environment variable is not set."
  exit 1
fi

# Add the authtoken to the ngrok configuration
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Starting ngrok...
echo "Starting ngrok..."
ngrok http 8000 --log=stdout > /dev/null &

# Wait for ngrok to start up
sleep 5

# Fetch the public URL from the ngrok API
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | sed 's/"public_url":"//')
HOST=$(echo $NGROK_URL | sed 's|https://||')

# Check if the URL was fetched successfully
if [ -z "$NGROK_URL" ]; then
  echo "Failed to get URL from ngrok. Check the logs."
  exit 1
fi

# Print the obtained ngrok URL and Host
echo "Ngrok started:"
echo "URL_BASE=${NGROK_URL}"
echo "HOST=${HOST}"

# If an .env file exists, update it with the new ngrok URL
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
    echo ".env file has been updated."
fi

# Applying database migrations...
echo "Applying migrations..."
python manage.py migrate

# Setting the Telegram webhook...
echo "Setting Telegram webhook..."
python manage.py shell -c "from web.telegram_bot import set_telegram_webhook; set_telegram_webhook()"
# ------------------------------------

# Starting the main process...
echo "Starting the main process..."

# Load initial data from a fixture
python manage.py loaddata fixture_tariffs.json

# Execute the Django development server
exec python manage.py runserver 0.0.0.0:8000
