# 📄 Persona-Driven Document Intelligence
This project is a CPU-efficient system designed for extracting and ranking the most relevant sections/subsections from a set of documents based on a given persona and their specific job-to-be-done. Built for Adobe’s Hackathon challenge, it operates entirely offline (no internet access at runtime) and respects resource limits (sub-1GB models, <60s runtime).

## 🚀 Features

🔍 Contextual Relevance Scoring based on persona profiles.

📊 Ranking Engine for document sections.

💡 Custom persona.json input support.

⚡ Optimized for speed and memory (runs within 60s on CPU).

🐳 Dockerized for easy setup & reproducibility.

## 🧠 Architecture
```
project-root/
│
├── app/                    # Main application logic
│   ├── input/              # Input documents go here
│   ├── output/             # Outputs final ranked sections
│   ├── models/             # Local HuggingFace models
│   ├── main.py             # Entry point script
│   ├── parser.py           # Document parsing logic
│   ├── ranker.py           # Ranking algorithm logic
│   └── persona.json        # Persona input file
│
├── output/                 # Final exported results (outside container)
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔄 Pipeline Overview

Here’s a step-by-step breakdown of the document intelligence pipeline:

### 1. Input Collection
Accepts PDF or plain text files from the app/input folder.

Persona description (role + JTBD) is loaded from app/persona.json.

### 2. Parsing
PDFs are converted to text using pdfminer.

Large documents are split into manageable, semantically meaningful chunks (e.g., paragraph blocks).

### 3. Summarization
Each chunk is passed through a local summarization model (e.g., flan-t5-base or similar) to reduce size while preserving core meaning.

This improves scoring accuracy and speed.

### 4. Embedding + Scoring
Summarized chunks are converted into vector embeddings using a sentence transformer model.

The persona query is also embedded.

Cosine similarity is computed between the persona query and each chunk to get a relevance score.

### 5. Ranking
Chunks are sorted in descending order of similarity scores.

Top-k relevant chunks are selected (configurable).

## 🐋 Run with Docker

### 1. Build the Docker image:
```
docker build -t persona-pdf-ranker .
```
### 2.Run the container:
```
docker run --rm -v $(pwd)/app/input:/app/input \
                  -v $(pwd)/app/output:/app/output \
                  -v $(pwd)/app/models:/app/models \
                  -v $(pwd)/output:/output \
                  persona-pdf-ranker
```

## 🧾 Inputs
**persona.json:** Defines persona traits and job-to-be-done.

.txt or .pdf documents in the /app/input folder.

## 📤 Output

Ranked sections (JSON/CSV/text) written to /output.
