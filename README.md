# Literary Analysis API

FastAPI backend to analyze documents, URLs, and images with support for:
- File analysis (PDF, DOCX, TXT)
- Web article processing
- OCR for images and scanned PDFs
- Sentiment analysis
- PDF report generation

## Setup

```bash
pip install -r requirements.txt
```

Make sure Tesseract is installed:
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`
- Windows: Download from https://github.com/tesseract-ocr/tesseract

## Run

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to explore the API.

You’ll see all available endpoints:
- /analyze-file/ → Upload a text or PDF file
- /analyze-url/ → Analyze an article from the web
- /analyze-image/ → Upload scanned PDF or image for OCR + analysis