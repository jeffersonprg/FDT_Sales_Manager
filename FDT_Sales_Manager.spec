# Configuração do PyInstaller para gerar uma distribuição em pasta.

from PyInstaller.utils.hooks import collect_data_files


datas = collect_data_files("customtkinter")
datas += [("src/templates", "src/templates")]
datas += [("src/assets", "src/assets")]

analysis = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pytest"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="FDT Sales Manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="src/assets/brand/favicon.ico",
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    name="FDT Sales Manager",
)
