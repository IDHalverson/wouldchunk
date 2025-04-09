import httpx
import random
import re
from .router_constants import DOCUMENT_CATEGORIES

OLLAMA_URL = "http://localhost:11434/api/generate"

ROUTING_PROMPT = """
You are a document classification assistant. You will be given a short text sample.

Classify the sample into one of the following categories:
- culture

Respond ONLY with the category name. Do not include quotes, extra words, or explanations.

Text sample:
\"\"\"
{sample}
\"\"\"
"""

async def classify_text(content: str, num_samples: int = 3, sample_size: int = 400) -> str:
    # Split content into sentences or logical chunks
    sentences = re.split(r"\n\s*\n|\.\s", content)
    samples = random.sample(sentences, min(num_samples, len(sentences)))

    responses = []

    timeout = httpx.Timeout(60.0)  # seconds

    async with httpx.AsyncClient(timeout=timeout) as client:
        for sample in samples:
            prompt = ROUTING_PROMPT.format(sample=sample.strip())
            payload = {
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }

            response = await client.post(OLLAMA_URL, json=payload)
            category = response.json()["response"].strip().lower()
            print(f"🔍 Classified as: {category}")
            if category in DOCUMENT_CATEGORIES:
                responses.append(category)
            else:
                responses.append("unknown")

    # Majority vote
    if responses:
        return max(set(responses), key=responses.count)
    return "unknown"