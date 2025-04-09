# 🧱 wouldchunk

**wouldchunk** is an AI-powered content chunking microservice designed to intelligently process, segment, and prepare company documents, code, and data for downstream LLM applications like RAG, Q&A, and semantic search.

It takes in raw input (like a PDF, `.cob` file, Slack export, or Jira data), classifies it, routes it to the appropriate domain-specific chunker, uses an LLM (like Mistral via Ollama) to chunk the content meaningfully, and returns structured output with rich metadata.

## 🚀 Features

- 🧠 **LLM-Powered Semantic Chunking** — uses Mistral (locally via Ollama) to create meaningful chunks instead of naive slicing
- 📂 **Multi-type Ingestion** — supports PDFs (coming soon: text files, code, Git logs, Slack exports, Jira issues, Jira comments, Confluence, Google Docs...)
- 🔎 **Smart Routing** — auto-detects file type and content category (e.g. `"culture"`, `"code"`, `"git"`) and routes to the correct handler
- 🏗️ **Single vs Multiple Handling** — dynamically chooses the right chunking pipeline based on number of files uploaded
- 🏷️ **Metadata-Rich Output** — includes category, chunk index, timestamps, file source, versioning (more coming soon)
- 📜 **Output Logging** — every ingestion is saved as `.jsonl` for later reprocessing or training

## 🔧 Requirements

- Python 3.10+
- [`ollama`](https://ollama.com) running locally with Mistral (`ollama run mistral`)
- `pdfplumber` for PDF ingestion
- `python-magic` for MIME sniffing

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🧪 Running the server

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

## Docs

Access the API docs: (coming soon)

```bash
http://localhost:8000/docs
```

## 📤 Testing

Testing with curl:

```bash
curl -X POST http://localhost:8000/auto-chunk \
  -F 'files=@/path/to/Your Document.pdf'
```

You’ll get back:
• A list of chunked content
• Metadata per chunk
• The file’s category and type
• The saved path to your .jsonl log file

Chunk Output Example:

```json
{
  "chunk_text": "Trust is earned. We do what we say.",
  "category": "culture",
  "chunk_index": 0,
  "source_file": "Our Company Culture.pdf",
  "version": "v1.0",
  "timestamp": "2025-04-08T22:30:00Z"
}
```

## 🗺️ Roadmap Ideas

- Add support for text files, code, Git logs, Slack exports, Jira issues, Jira comments, Confluence, Google Docs
- Unit tests
- Allow CLI-based batch ingestion
