"""Resolve recursos empacotados e ficheiros que precisam de escrita."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Mapping


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def caminho_recurso(*partes: str) -> Path:
    """Localiza ficheiros incluídos pelo PyInstaller ou presentes no projeto."""

    base = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return base.joinpath(*partes)


def diretorio_dados(
    frozen: bool | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Escolhe uma pasta gravável sem alterar o layout usado no desenvolvimento."""

    ambiente = os.environ if environ is None else environ
    override = ambiente.get("FDT_DATA_DIR")
    if override:
        return Path(override).expanduser()

    empacotado = getattr(sys, "frozen", False) if frozen is None else frozen
    if not empacotado:
        return PROJECT_ROOT / "src" / "data"

    local_app_data = ambiente.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    return base / "FDT Sales Manager"


DATA_DIR = diretorio_dados()
DATABASE_PATH = DATA_DIR / "fdt_sales_manager.db"
REPORTS_DIR = DATA_DIR / "reports"
TEMPLATES_DIR = caminho_recurso("src", "templates")
ASSETS_DIR = caminho_recurso("src", "assets")
BRAND_ASSETS_DIR = ASSETS_DIR / "brand"
BRAND_NAME = "TSS Invest"
BRAND_TAGLINE = "O futuro financeiro, nuestra estrategia"
BRAND_LOGO_PATH = BRAND_ASSETS_DIR / "tssinvest_logo.png"
APP_ICON_PATH = BRAND_ASSETS_DIR / "app_icon.png"
APP_ICON_ICO_PATH = BRAND_ASSETS_DIR / "favicon.ico"
