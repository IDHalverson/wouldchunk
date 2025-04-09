from fastapi import UploadFile
import zipfile
import tempfile
from pathlib import Path

def extract_zip_to_temp(file: UploadFile):
    temp_dir = tempfile.TemporaryDirectory()
    zip_path = Path(temp_dir.name) / file.filename

    with open(zip_path, "wb") as f:
        f.write(file.file.read())

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir.name)

    extracted_files = list(Path(temp_dir.name).rglob("*.*"))
    return temp_dir, extracted_files  # Must keep temp_dir alive