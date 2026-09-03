FROM python:3.11-slim

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model during build for instant cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Render injects $PORT
ENV PORT=8001
EXPOSE ${PORT}

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
