from src.i18n import ENGLISH, SPANISH, get_language, normalizar_idioma, set_language, tr
from src.presentation import montar_dashboard


def test_traducao_da_interface_e_do_dashboard():
    try:
        set_language("en")
        assert get_language() == "en"
        assert tr("Configurações") == "Settings"
        assert tr("Pedido #{id}", id=12) == "Order #12"
        assert montar_dashboard({})["cards"][0][0] == "Active customers"
    finally:
        set_language("pt")


def test_portugues_e_o_idioma_padrao_e_fallback():
    try:
        set_language("pt")
        assert tr("Configurações") == "Configurações"
        assert normalizar_idioma("EN_us") == "en"
        assert normalizar_idioma("es-ES") == "es"
        assert normalizar_idioma("fr") == "pt"
    finally:
        set_language("pt")


def test_traducao_para_espanhol_tem_o_mesmo_catalogo():
    try:
        assert set(ENGLISH) == set(SPANISH)
        set_language("es-ES")
        assert get_language() == "es"
        assert tr("Configurações") == "Configuración"
        assert tr("Pedido #{id}", id=12) == "Pedido #12"
        assert montar_dashboard({})["cards"][0][0] == "Clientes activos"
        assert tr("Espanhol") == "Español"
    finally:
        set_language("pt")
