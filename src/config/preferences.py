"""Lê e guarda preferências locais da interface."""

from __future__ import annotations

import json
from pathlib import Path

from src.config.paths import DATA_DIR


PREFERENCES_PATH = DATA_DIR / "preferences.json"
VALID_THEMES = {"light", "dark"}


def normalizar_tema(value: object) -> str:
    tema = str(value).casefold()
    return tema if tema in VALID_THEMES else "light"


def carregar_tema(path: Path | None = None) -> str:
    """Devolve a preferência guardada ou o modo claro em caso de erro."""

    caminho = path or PREFERENCES_PATH
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return "light"
    return normalizar_tema(dados.get("theme")) if isinstance(dados, dict) else "light"


def guardar_tema(theme: str, path: Path | None = None) -> None:
    """Persiste a escolha sem deixar um ficheiro parcialmente escrito."""

    caminho = path or PREFERENCES_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(
        json.dumps({"theme": normalizar_tema(theme)}, indent=2),
        encoding="utf-8",
    )
    temporario.replace(caminho)
