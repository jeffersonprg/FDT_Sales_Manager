import json

from src.config.preferences import (
    carregar_idioma,
    carregar_tema,
    guardar_idioma,
    guardar_tema,
    normalizar_tema,
)
from src.views.theme import cor_atual


def test_preferencia_de_tema_e_guardada(tmp_path):
    path = tmp_path / "preferences.json"

    guardar_tema("dark", path)

    assert carregar_tema(path) == "dark"
    assert json.loads(path.read_text(encoding="utf-8")) == {"theme": "dark"}


def test_preferencia_invalida_usa_modo_claro(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text('{"theme": "desconhecido"}', encoding="utf-8")

    assert carregar_tema(path) == "light"
    assert carregar_tema(tmp_path / "ausente.json") == "light"
    assert normalizar_tema("DARK") == "dark"


def test_paleta_resolve_cores_para_widgets_ttk():
    assert cor_atual("background", "light") == "#F3F6FA"
    assert cor_atual("background", "dark") == "#0F1318"


def test_idioma_e_guardado_sem_perder_o_tema(tmp_path):
    path = tmp_path / "preferences.json"
    guardar_tema("dark", path)

    guardar_idioma("EN-us", path)

    assert carregar_tema(path) == "dark"
    assert carregar_idioma(path) == "en"
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "theme": "dark",
        "language": "en",
    }


def test_idioma_invalido_usa_portugues(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text('{"language": "desconhecido"}', encoding="utf-8")

    assert carregar_idioma(path) == "pt"
    assert carregar_idioma(tmp_path / "ausente.json") == "pt"


def test_preferencia_aceita_espanhol(tmp_path):
    path = tmp_path / "preferences.json"

    guardar_idioma("es-ES", path)

    assert carregar_idioma(path) == "es"
    assert json.loads(path.read_text(encoding="utf-8")) == {"language": "es"}
