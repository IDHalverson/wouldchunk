import httpx
import json
from datetime import datetime
from app.utils.logging import write_chunk_log

OLLAMA_URL = "http://localhost:11434/api/generate"

CHUNKING_PROMPT = """
You are a document chunking assistant. Given a culture document, segment it into semantically meaningful "chunks" that represent complete thoughts.

Each chunk should:
- Be self-contained
- Represent a single idea, quote, or bullet group
- Be suitable for semantic search

Return your response as a JSON array of objects like:
[
  {{"chunk_text": "Trust is earned. We do what we say."}},
  {{"chunk_text": "Integrity means doing the right thing even when no one is watching."}}
]

Document:
\"\"\"
{content}
\"\"\"
"""

CHUNK_VERSION = "v1.0"

async def get_chunks_from_mistral(content: str, source_file: str = "uploaded.txt") -> list[dict]:
    prompt = CHUNKING_PROMPT.format(content=content.strip())

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    timeout = httpx.Timeout(60.0)  # seconds

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_output = response.json()["response"]

        try:
            print("📤 Raw LLM output:", raw_output)
            parsed = json.loads(raw_output)
            enriched = []

            for i, chunk in enumerate(parsed):
                chunk_text = chunk.get("chunk_text", "").strip()
                if not chunk_text:
                    continue

                enriched.append({
                    "chunk_text": chunk_text,
                    "category": "culture",
                    "chunk_index": i,
                    "source_file": source_file,
                    "version": CHUNK_VERSION,
                    "timestamp": datetime.utcnow().isoformat()
                })

                log_path = write_chunk_log(enriched, source_file, "culture", CHUNK_VERSION)
                print(f"✅ Chunks saved to: {log_path}")

                return {
                    "chunks": enriched,
                    "log_path": log_path
                }

        except Exception:
            return [{
                "chunk_text": content.strip(),
                "category": "culture",
                "chunk_index": 0,
                "source_file": source_file,
                "version": CHUNK_VERSION,
                "timestamp": datetime.utcnow().isoformat(),
                "error": "LLM chunking failed"
            }]