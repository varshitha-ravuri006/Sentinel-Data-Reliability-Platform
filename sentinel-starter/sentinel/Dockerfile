FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./static ./static

EXPOSE 8000

# Cloud hosts (Render) give us the port in $PORT; locally it falls back to 8000.
# No --reload here: hot-reload for development is set in docker-compose.yml.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
