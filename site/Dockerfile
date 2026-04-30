FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev gcc netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT ["gunicorn", "-k", "eventlet", "-w", "1", "--access-logfile", "-", "--error-logfile", "-", "-b", "0.0.0.0:5000", "run:app"]
