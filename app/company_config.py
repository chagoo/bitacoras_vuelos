from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from .config import DATA_DIR


CONFIG_PATH = DATA_DIR / "company.json"


@dataclass
class CompanyConfig:
    name: str = "MANTENIMIENTO AEREO DE MONTERREY, S.A. DE C.V."
    address: str = ""
    phone: str = ""
    email: str = ""
    rfc: str = ""
    afac_no: str = "508"
    logo_path: str = ""  # Absolute or relative path to an image file


def load_company_config() -> CompanyConfig:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return CompanyConfig(**data)
    except Exception:
        pass
    return CompanyConfig()


def save_company_config(cfg: CompanyConfig) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Error guardando configuración: {exc}")
