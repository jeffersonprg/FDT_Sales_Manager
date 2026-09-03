import customtkinter as ctk

from src.config.preferences import carregar_tema
from src.database.database import create_tables
from src.views.main_window import MainWindow


def main() -> None:
    ctk.set_appearance_mode(carregar_tema())
    ctk.set_default_color_theme("blue")
    create_tables()
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
