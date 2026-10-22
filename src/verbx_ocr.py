
import os
import json
import base64
import uuid
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()


def read_pdf_with_verbx(pdf_bytes, hard=False, pages=None):
    api_key = os.getenv("VERBX_API_KEY")

    if not api_key:
        raise ValueError(
            "VERBX_API_KEY is missing. Check your .env file."
        )

    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    endpoint = (
        "/v1/ocr/hard" if hard else "/v1/ocr"
    )

    body = {"pdf": encoded_pdf}

    if pages:
        body["pages"] = pages

    request = urllib.request.Request(
        "https://api.verbxeco.com" + endpoint,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "x-api-key": api_key,
            "X-VerbX-Shell": "saas",
            "Content-Type": "application/json",
            "Idempotency-Key": uuid.uuid4().hex,
        },
    )

    try:
        with urllib.request.urlopen(
            request, timeout=120
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return result

    except urllib.error.HTTPError as error:
        details = error.read().decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(
            f"VerbX OCR failed (HTTP {error.code}): {details}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to VerbX: {error.reason}"
        ) from error
