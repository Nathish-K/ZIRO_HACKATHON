
from pathlib import Path

# pyrefly: ignore[missing-import]
from test_verbx_ocr import read_pdf_with_verbx

pdf_path = Path("indian_document_agent_test.pdf")

if not pdf_path.exists():
    print("Place the test PDF in your project folder.")
else:
    try:
        result = read_pdf_with_verbx(
            pdf_path.read_bytes()
        )

        print("OCR SUCCESS")
        print("Extracted text:")
        print(result.get("text", ""))

        print("\nPage results:")
        for page in result.get("pages", []):
            print(f"\nPage {page.get('page')}:")
            print(page.get("text", ""))

    except Exception as error:
        print("OCR TEST FAILED:", error)
