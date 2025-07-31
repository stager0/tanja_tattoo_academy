FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y wget unzip curl && rm -rf /var/lib/apt/lists/*

RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip -O ngrok.zip && \
    unzip ngrok.zip && \
    rm ngrok.zip && \
    mv ngrok /usr/local/bin/

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh", "python manage.py makemigration", "python manage.py migrate"]

CMD ["python", "manage.py", "runserver"]