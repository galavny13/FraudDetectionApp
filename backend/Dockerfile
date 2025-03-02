# backend/Dockerfile
FROM python:3.10-slim

# Install Tesseract + dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy & install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code (In dev, we might just rely on volume mount, but let's do it anyway)
COPY app /app/app

EXPOSE 8000

# We'll rely on docker-compose command override to run uvicorn with multiple workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
