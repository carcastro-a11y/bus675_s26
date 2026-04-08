FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies first (maximizes layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and required data files
COPY app.py .
COPY imagenet_classes.json .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
