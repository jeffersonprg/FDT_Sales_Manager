import ctypes
import sys

import customtkinter as ctk

from src.config.preferences import carregar_idioma, carregar_tema
from src.database.database import create_tables
from src.i18n import set_language
from src.views.main_window import MainWindow


def configurar_identidade_windows() -> None:
    """Define a identidade usada pelo Windows na barra de tarefas."""

    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "TSSInvest.FDTSalesManager"
        )


def main() -> None:
    configurar_identidade_windows()
    ctk.set_appearance_mode(carregar_tema())
    set_language(carregar_idioma())
    ctk.set_default_color_theme("blue")
    create_tables()
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
