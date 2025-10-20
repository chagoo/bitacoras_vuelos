from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "Bitácoras de Vuelos"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "bitacoras.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"
