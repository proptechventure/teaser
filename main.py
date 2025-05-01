from fastapi import FastAPI, UploadFile, File
from teaser_generator import generate_teaser
import shutil
import uuid

app = FastAPI()

@app.post("/upload")
async def upload_files(pptx: UploadFile = File(...), excel: UploadFile = File(...), logo: UploadFile = File(...)):
    id = str(uuid.uuid4())
    pptx_path = f"temp/{id}_presentation.{pptx.filename.split('.')[-1]}"
    excel_path = f"temp/{id}_data.xlsx"
    logo_path = f"static/logos/{id}_logo.png"

    for path, file in [(pptx_path, pptx), (excel_path, excel), (logo_path, logo)]:
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    teaser_pdf = generate_teaser(pptx_path, excel_path, logo_path)
    return {"status": "ok", "teaser_pdf": teaser_pdf}
