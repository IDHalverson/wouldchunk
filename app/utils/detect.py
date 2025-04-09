from pathlib import Path
from fastapi import UploadFile
import magic
from app.router_constants import EXT_TO_TYPE

async def detect_type_and_category(file: UploadFile, content: str = None) -> dict:
    ext = Path(file.filename).suffix.lower()
    data_type = EXT_TO_TYPE.get(ext)

    if not content:
        content = (await file.read()).decode("utf-8")
        # Reset file position after reading
        await file.seek(0)

    # Fallback MIME detection using python-magic
    if not data_type:
        # Get raw bytes for MIME detection
        file_bytes = await file.read()
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_bytes)
        
        # Reset file position after reading
        await file.seek(0)
        
        # Categorize based on MIME type
        if mime_type.startswith('text/'):
            if any(code_indicator in mime_type for code_indicator in ['x-python', 'x-script', 'x-c', 'x-java']):
                data_type = "code"
            else:
                data_type = "text-document"
        elif mime_type.startswith(('application/x-executable', 'application/x-sharedlib')):
            data_type = "binary"
        else:
            data_type = "text-document"

    return {
        "data_type": data_type,
        "content": content,
        "mime_type": mime_type if 'mime_type' in locals() else None
    }