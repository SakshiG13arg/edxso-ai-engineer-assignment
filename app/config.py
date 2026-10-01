from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

with open(ROOT / "config" / "settings.yaml", "r", encoding="utf-8") as f:
    SETTINGS = yaml.safe_load(f)

OUTPUT_DIR = ROOT / SETTINGS["runtime"]["output_dir"]
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "fallback").lower()
