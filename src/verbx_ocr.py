import os
import base64
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.verbxeco.com"


def read_pdf_with_verbx(pdf_bytes, hard=False, pages=None):
    api_key = os.getenv("VERBX_API_KEY")

    if not api_key:
        raise ValueError("VERBX_API_KEY is missing. Check your .env file.")

    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    endpoint = "/v1/ocr/hard" if hard else "/v1/ocr"
    url = f"{BASE_URL}{endpoint}"

    body = {"pdf": encoded_pdf}
    if pages:
        body["pages"] = pages

    headers = {
        "x-api-key": api_key,
        "X-VerbX-Shell": "saas",
        "Content-Type": "application/json",
        "User-Agent": "IndianDocumentAgent/1.0",
        "Idempotency-Key": uuid.uuid4().hex,
    }

    try:
        response = requests.post(url, json=body, headers=headers, timeout=120)

        if response.status_code == 200:
            return response.json()

        try:
            details = response.json()
            err_msg = details.get("message") or details.get("error", response.text)
        except Exception:
            err_msg = response.text

        if response.status_code == 503:
            raise RuntimeError(
                f"VerbX OCR Service Maintenance (HTTP 503): {err_msg}. Please retry in a few moments."
            )
        else:
            raise RuntimeError(f"VerbX OCR failed (HTTP {response.status_code}): {err_msg}")

    except requests.exceptions.RequestException as error:
        err_str = str(error)
        if "10053" in err_str or "Connection aborted" in err_str:
            raise RuntimeError(
                "Connection aborted by host/server: The connection was dropped during upload. "
                "This typically occurs if the file is extremely large or the server is undergoing maintenance."
            ) from error
        raise RuntimeError(f"Could not connect to VerbX: {error}") from error
