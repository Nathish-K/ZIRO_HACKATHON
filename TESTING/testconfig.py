
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Read the API key without displaying it
api_key = os.getenv("VERBX_API_KEY")

if api_key:
    print("SUCCESS: VerbX API key loaded.")
else:
    print("ERROR: API key not found. Check your .env file.")
