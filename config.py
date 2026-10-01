import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / os.getenv("EXPORT_DIR", "exports")
EXPORT_DIR.mkdir(exist_ok=True)


class Settings:
    APP_NAME = os.getenv("APP_NAME", "SmartRH")
    # IA / LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_ENABLED = os.getenv("LLM_ENABLED", "False").lower() == "true"
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    ABSENCE_ALERT_THRESHOLD = int(os.getenv("ABSENCE_ALERT_THRESHOLD", 5))
    LEAVE_RISK_MULTIPLIER = float(os.getenv("LEAVE_RISK_MULTIPLIER", 1.5))
    MATCH_SCORE_THRESHOLD = int(os.getenv("MATCH_SCORE_THRESHOLD", 80))

    EXPORT_DIR = EXPORT_DIR


settings = Settings()