from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "8000"))