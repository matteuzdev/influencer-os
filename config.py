"""
Configurações e constantes do Influencer IA Pipeline.
"""
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    temp_dir = Path(tempfile.gettempdir())
    INPUT_DIR = temp_dir / "inputs"
    OUTPUT_DIR = temp_dir / "outputs"
    CHROME_PROFILE_DIR = temp_dir / ".chrome-influencer-profile"
else:
    INPUT_DIR = BASE_DIR / "inputs"
    OUTPUT_DIR = BASE_DIR / "outputs"
    CHROME_PROFILE_DIR = Path.home() / ".chrome-influencer-profile"

try:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Recupera chave da API do Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# URL do Google ImageFX / Flow
IMAGE_FX_URL = "https://labs.google/fx/tools/image-fx"
