import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.verbxeco.com"

# Supported Indian & major languages
SUPPORTED_LANGUAGES = {
    "hi": "Hindi (हिंदी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "ur": "Urdu (اردو)",
    "en": "English",
}


def translate_text(
    text: str,
    target_lang: str = "hi",
    source_lang: str = "auto",
    timeout: int = 30,
) -> dict:
    """
    Translates text using the VerbX translation API.
    
    Args:
        text (str): Text to translate.
        target_lang (str): Target ISO-639 language code (e.g. 'hi', 'ta', 'te').
        source_lang (str): Source language code or 'auto' for auto-detection.
        timeout (int): Request timeout in seconds.
        
    Returns:
        dict: API response containing 'text', 'confidence', etc.
    """
    api_key = os.getenv("VERBX_API_KEY")
    if not api_key:
        raise ValueError("VERBX_API_KEY is missing. Check your .env file.")

    text = text.strip()
    if not text:
        return {"text": "", "confidence": 1.0}

    url = f"{BASE_URL}/v1/translate"
    headers = {
        "x-api-key": api_key,
        "X-VerbX-Shell": "saas",
        "Content-Type": "application/json",
        "Idempotency-Key": str(uuid.uuid4()),
        "User-Agent": "IndianDocumentAgent/1.0",
    }

    # If text is very long (>2000 chars), split by paragraphs/chunks to ensure high quality
    if len(text) > 2500:
        return _translate_in_chunks(text, target_lang, source_lang, headers, timeout)

    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not connect to VerbX Translate: {e}") from e

    # Fallback if auto-detection produces upstream error: retry with 'en' source
    if response.status_code == 503 and source_lang == "auto":
        payload["source_lang"] = "en"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException:
            pass

    if response.status_code != 200:
        try:
            err_data = response.json()
            err_msg = err_data.get("message") or err_data.get("error", response.text)
        except Exception:
            err_msg = response.text
        raise RuntimeError(f"VerbX Translation failed (HTTP {response.status_code}): {err_msg}")

    return response.json()


def _translate_in_chunks(
    text: str,
    target_lang: str,
    source_lang: str,
    headers: dict,
    timeout: int,
    chunk_size: int = 1500,
) -> dict:
    """Splits large text into paragraphs/chunks, translates each, and joins them."""
    paragraphs = text.split("\n")
    translated_parts = []
    total_conf = 0.0
    count = 0

    current_chunk = []
    current_len = 0

    chunks = []
    for p in paragraphs:
        if current_len + len(p) + 1 > chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += len(p) + 1

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    url = f"{BASE_URL}/v1/translate"

    for chunk in chunks:
        if not chunk.strip():
            translated_parts.append("")
            continue

        payload = {
            "text": chunk,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        res = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if res.status_code == 503 and source_lang == "auto":
            payload["source_lang"] = "en"
            res = requests.post(url, json=payload, headers=headers, timeout=timeout)

        if res.status_code == 200:
            data = res.json()
            translated_parts.append(data.get("text", chunk))
            if "confidence" in data:
                total_conf += data["confidence"]
                count += 1
        else:
            translated_parts.append(chunk)

    return {
        "text": "\n".join(translated_parts),
        "confidence": round(total_conf / count, 4) if count > 0 else 1.0,
        "chunks_count": len(chunks),
    }
