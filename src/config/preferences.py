"""Lê e guarda preferências locais da interface."""

from __future__ import annotations

import json
from pathlib import Path

from src.config.paths import DATA_DIR
from src.i18n import normalizar_idioma


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


def carregar_idioma(path: Path | None = None) -> str:
    """Devolve o idioma guardado ou portugues em caso de erro."""

    caminho = path or PREFERENCES_PATH
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return "pt"
    return normalizar_idioma(dados.get("language")) if isinstance(dados, dict) else "pt"


def _guardar_preferencia(chave: str, valor: str, caminho: Path) -> None:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            dados = {}
    except (OSError, json.JSONDecodeError, TypeError):
        dados = {}
    dados[chave] = valor
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(json.dumps(dados, indent=2), encoding="utf-8")
    temporario.replace(caminho)


def guardar_tema(theme: str, path: Path | None = None) -> None:
    """Persiste a escolha sem deixar um ficheiro parcialmente escrito."""

    caminho = path or PREFERENCES_PATH
    _guardar_preferencia("theme", normalizar_tema(theme), caminho)


def guardar_idioma(language: str, path: Path | None = None) -> None:
    """Persiste o idioma sem perder outras preferencias."""

    _guardar_preferencia(
        "language", normalizar_idioma(language), path or PREFERENCES_PATH,
    )
