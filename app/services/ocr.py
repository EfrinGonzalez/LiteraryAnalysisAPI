import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF

def ocr_image_bytes(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang='eng+spa')

def ocr_pdf_bytes(pdf_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            text += pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)), lang='eng+spa')
    return text