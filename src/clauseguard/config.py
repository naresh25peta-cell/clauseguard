"""
config.py — loads all settings from the .env file.

Why: we keep secrets (API keys, paths) out of code.
     Every other module imports from here instead of reading .env directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")   # None = use default OpenAI; set to xAI URL for Grok
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
DB_PATH         = os.getenv("DB_PATH", "data/db/clauseguard.db")
CN_PDF_FOLDER   = os.getenv("CN_PDF_FOLDER", "data/pdfs/cn")
MSA_PDF_FOLDER  = os.getenv("MSA_PDF_FOLDER", "data/pdfs/msa")
