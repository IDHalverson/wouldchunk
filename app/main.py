from fastapi import FastAPI, UploadFile, File
from app.utils.detect import detect_type_and_category
from app.utils.extract import extract_zip_to_temp
from app.router import classify_text
import importlib

from pathlib import Path

def ensure_outputs_dir():
    Path("outputs").mkdir(parents=True, exist_ok=True)

app = FastAPI()

import pdfplumber

async def read_file_content(file: UploadFile) -> str:
    if file.filename.lower().endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return text
    else:
        return (await file.read()).decode("utf-8", errors="ignore")

@app.post("/auto-chunk")
async def auto_chunk(files: list[UploadFile] = File(...)):
    results = []
    actual_files = []

    for file in files:
        if file.filename.endswith(".zip"):
            temp_dir, extracted_paths = extract_zip_to_temp(file)
            for path in extracted_paths:
                with open(path, "r") as f:
                    actual_files.append((path.name, f.read()))
        else:
            content = await read_file_content(file)
            actual_files.append((file.filename, content))

    is_multiple = len(actual_files) > 1

    for filename, content in actual_files:
        detection = await detect_type_and_category(
            UploadFile(filename=filename, file=None), content
        )

        data_type = detection["data_type"]

        # Only classify if text-document
        if data_type == "text-document":
            category = await classify_text(content)
        else:
            category = "generic"

        path_type = "multiple" if is_multiple else "single"
        safe_cat = category.replace("-", "_")
        module_path = f"app.ingestion-types.{data_type}.{path_type}.categories.{safe_cat}.{path_type}_{safe_cat}_document"

        try:
            module = importlib.import_module(module_path)
            chunks = await module.get_chunks_from_mistral(
                content if not is_multiple else [c for _, c in actual_files]
            )
            results.append({
                "filename": filename,
                "type": data_type,
                "category": category,
                "chunks": chunks
            })
        except ModuleNotFoundError:
            results.append({
                "filename": filename,
                "type": data_type,
                "category": category,
                "error": f"No handler for {data_type}/{category} ({path_type})"
            })

    return results