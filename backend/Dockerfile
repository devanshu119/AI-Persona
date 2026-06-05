FROM python:3.11-slim

WORKDIR /app

# No extra system packages needed — PyMuPDF uses pre-built wheels,
# weasyprint was removed from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure package __init__.py files exist
RUN touch rag/__init__.py calcom/__init__.py ingest/__init__.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
