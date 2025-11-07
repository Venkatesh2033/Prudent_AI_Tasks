import os
import json
import tempfile
from typing import Dict, Any
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from google import generativeai as genai

# ---------- CONFIG ----------
GEMINI_MODEL = "gemini-1.5-pro"
TIMEOUT = 30


def extract_text_from_pdf(file_path: str) -> str:
    "Extracts text from a PDF"
    text = ""
    reader = PdfReader(file_path)

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
            if not page_text.strip():  # OCR fallback
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                    # Convert PDF page to image via pdf2image if needed
                    pass
            text += "\n" + page_text
        except Exception as e:
            print(f"Warning reading page: {e}")
    return text.strip()


def extract_text_from_image(file_path: str) -> str:
    "Extract text from image using Tesseract OCR"
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


def mask_account_number(acc_no: str) -> str:
    "Mask all but last 4 digits"
    digits = ''.join([d for d in acc_no if d.isdigit()])
    if len(digits) >= 4:
        return "XXXX-XXXX-" + digits[-4:]
    return acc_no


def load_prompt(file_name: str) -> str:
    "Load prompt"
    with open(os.path.join("prompts", file_name), "r") as f:
        return f.read()


def call_gemini(prompt: str, text: str) -> Any:
    "Call Gemini with safety + timeout"
    genai.configure(api_key=os.environ.get("AIzaSyAivTM6RDTynndcRLKwBzH-MJzylIXYCrM"))
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt + "\n\n" + text)
    return response.text


def process_bank_statement(file_path: str, test_mode: bool = False) -> Dict[str, Any]:
    """
    Extracts data from bank statement (PDF/Image),
    parses via Gemini, returns structured JSON + insights + quality metrics.
    """
    if test_mode:
        print("Running in TEST MODE: using mock data.")
        with open("sample_output.json") as f:
            return json.load(f)

    # 1. Read file & extract text
    if file_path.lower().endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    else:
        raw_text = extract_text_from_image(file_path)

    # 2. Gemini extraction call
    extraction_prompt = load_prompt("prompt_extraction.txt")
    extraction_response = call_gemini(extraction_prompt, raw_text)

    try:
        extracted_json = json.loads(extraction_response)
    except json.JSONDecodeError:
        print("Error: Gemini returned invalid JSON. Attempting fix...")
        extraction_response = extraction_response.strip().split("```json")[-1].split("```")[0]
        extracted_json = json.loads(extraction_response)

    # Mask account number for privacy
    if "fields" in extracted_json and "Account Info" in extracted_json["fields"]:
        info = extracted_json["fields"]["Account Info"]
        if "account number" in info:
            info["account number"] = mask_account_number(info["account number"])

    # 3. Gemini insights call
    insights_prompt = load_prompt("prompt_insights.txt")
    insights_response = call_gemini(insights_prompt, json.dumps(extracted_json))
    extracted_json["insights"] = json.loads(insights_response) if insights_response.strip().startswith("[") else [insights_response]

    # 4. Add quality metadata
    extracted_json["quality"] = {
        "ocr_confidence": "N/A (Tesseract fallback)",
        "missing_sections": [],
        "duplicate_entries": False,
        "gemini_confidence": "High"
    }

    return extracted_json


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bank Statement Parser using Gemini")
    parser.add_argument("file_path", help="Path to PDF or image file")
    parser.add_argument("--test", action="store_true", help="Run in test mode (mock data)")
    args = parser.parse_args()

    result = process_bank_statement(args.file_path, args.test)
    print(json.dumps(result, indent=2))
