import os
import platform
import tempfile
from PIL import Image
import pytesseract
from email import message_from_binary_file
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Set Tesseract path from .env (for Windows)
if platform.system() == "Windows":
    tess_path = os.getenv("TESSERACT_CMD")
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
        

def extract_text_from_eml_with_ocr(file) -> str:
    
    msg = message_from_binary_file(file)
    extracted_text = []

    for part in msg.walk():
        content_type = part.get_content_type()

        if content_type == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                extracted_text.append(payload.decode(errors="ignore"))

        elif "image" in content_type:
            image_data = part.get_payload(decode=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(image_data)
                tmp_img.flush()
                try:
                    text = pytesseract.image_to_string(Image.open(tmp_img.name))
                    extracted_text.append(text)
                except Exception as e:
                    print(f"OCR failed: {e}")

    return "\n".join(extracted_text)
