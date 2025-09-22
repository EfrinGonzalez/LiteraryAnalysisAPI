from fastapi import APIRouter, UploadFile, File, Form
from app.services.analysis import analyze_text_file
from app.services.scraper import fetch_article_text
from app.services.ocr import ocr_image_bytes, ocr_pdf_bytes

router = APIRouter()

@router.post("/analyze-file/")
async def analyze_file(file: UploadFile = File(...)):
    text = await file.read()
    result = analyze_text_file(text.decode("utf-8"))
    return result

@router.post("/analyze-url/")
async def analyze_url(url: str = Form(...)):
    text = fetch_article_text(url)
    result = analyze_text_file(text)
    return result

@router.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    content = await file.read()
    ext = file.filename.lower().split('.')[-1]
    if ext == "pdf":
        text = ocr_pdf_bytes(content)
    else:
        text = ocr_image_bytes(content)
    result = analyze_text_file(text)
    return result