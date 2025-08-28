import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX: str = os.getenv("GOOGLE_SEARCH_CX", "")
