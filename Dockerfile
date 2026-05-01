FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/ app/
COPY static/ static/
COPY templates/ templates/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
