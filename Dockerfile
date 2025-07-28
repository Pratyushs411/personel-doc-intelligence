# Use a lightweight Python image
FROM python:3.11-slim

# Disable .pyc files and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy only necessary files
COPY app/ ./app/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory to app/ inside container
WORKDIR /app/app

# Download all-MiniLM-L6-v2 (embedding model)
RUN python3 -c "from sentence_transformers import SentenceTransformer; \
                SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder='/app/models/all-MiniLM-L6-v2')"

# Download the model and tokenizer to /app/models
RUN python3 -c "\
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
AutoTokenizer.from_pretrained('google/flan-t5-base'); \
AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')"
# Command to run your script
CMD ["python", "main.py"]
