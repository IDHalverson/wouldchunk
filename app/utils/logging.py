import json
from pathlib import Path
from datetime import datetime

def write_chunk_log(chunks: list[dict], filename: str, category: str, version: str = "v1.0"):
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    safe_name = Path(filename).stem.replace(" ", "_").lower()
    out_path = Path("outputs") / f"{safe_name}.{category}.{version}.{ts}.jsonl"

    with open(out_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            json.dump(chunk, f)
            f.write("\n")

    return str(out_path)