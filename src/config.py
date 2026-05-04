import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

MODEL_NAME = "gpt-5.4-mini"

TOP_K_CHUNKS = 5
CHUNK_PAGES = 3
CHUNK_OVERLAP = 1