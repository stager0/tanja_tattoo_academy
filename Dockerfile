FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y dos2unix curl && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /app/entrypoint.sh

RUN dos2unix /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]