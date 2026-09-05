from pathlib import Path

from PIL import Image

from src.config.paths import (
    APP_ICON_ICO_PATH,
    APP_ICON_PATH,
    BRAND_LOGO_PATH,
    BRAND_NAME,
    PROJECT_ROOT,
    diretorio_dados,
)


def test_diretorio_dados_no_desenvolvimento():
    assert diretorio_dados(frozen=False, environ={}) == PROJECT_ROOT / "src" / "data"


def test_diretorio_dados_na_aplicacao_empacotada():
    environ = {"LOCALAPPDATA": r"C:\Users\Teste\AppData\Local"}
    assert diretorio_dados(frozen=True, environ=environ) == (
        Path(environ["LOCALAPPDATA"]) / "FDT Sales Manager"
    )


def test_diretorio_dados_aceita_configuracao_explicita():
    assert diretorio_dados(
        frozen=True,
        environ={"FDT_DATA_DIR": r"D:\Dados\FDT"},
    ) == Path(r"D:\Dados\FDT")


def test_ativos_da_marca_estao_disponiveis():
    assert BRAND_NAME == "TSS Invest"
    assert BRAND_LOGO_PATH.is_file()
    assert APP_ICON_PATH.is_file()
    assert APP_ICON_ICO_PATH.is_file()

    with Image.open(APP_ICON_PATH) as icone_png:
        assert icone_png.size == (256, 256)

    with Image.open(APP_ICON_ICO_PATH) as icone_windows:
        assert icone_windows.format == "ICO"
        assert (256, 256) in icone_windows.info["sizes"]
