from pathlib import Path
from src import read_pdf_with_verbx

def main():
    print("Test started")
    pdf_path = Path(r"C:\Users\nathi\Downloads\Agentic AI Problem Statement.pdf")

    if not pdf_path.exists():
        print("PDF not found:", pdf_path.resolve())
    else:
        print("PDF found. Calling VerbX OCR...")
        result = read_pdf_with_verbx(pdf_path.read_bytes())
        print("OCR SUCCESS")
        print(result.get("text", "No text returned"))

if __name__ == "__main__":
    main()
