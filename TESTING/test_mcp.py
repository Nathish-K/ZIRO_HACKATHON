
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("VERBX_API_KEY")
if not api_key:
    raise SystemExit("API key not found in .env")

headers = {
    "x-api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {
            "name": "IndianDocumentAgent",
            "version": "1.0.0",
        },
    },
}

try:
    response = requests.post(
        "https://api.verbxeco.com/mcp",
        headers=headers,
        json=payload,
        timeout=30,
    )
    print("HTTP status:", response.status_code)
    print("MCP session ID:", response.headers.get("Mcp-Session-Id", "(not provided)"))
    print("Response:", response.text or "(empty response body)")
except requests.RequestException as error:
    print("Connection error:", error)
