"""Paleta partilhada pelos modos claro e escuro da interface."""

from __future__ import annotations

import customtkinter as ctk


# O CustomTkinter escolhe automaticamente o primeiro ou o segundo valor de
# cada tuplo quando o modo de aparência muda.
COLORS = {
    "navy": ("#102A43", "#151A21"),
    "navy_hover": ("#1D3F5E", "#252D38"),
    "blue": ("#2563EB", "#4F7CFF"),
    "blue_hover": ("#1D4ED8", "#3F6EE8"),
    "background": ("#F3F6FA", "#0F1318"),
    "surface": ("#FFFFFF", "#181D24"),
    "surface_alt": ("#EAF0F6", "#232A34"),
    "input": ("#F8FAFC", "#11161D"),
    "text": ("#102A43", "#F3F6FA"),
    "muted": ("#627D98", "#A7B2C2"),
    "border": ("#D9E2EC", "#303946"),
    "selection": ("#DBEAFE", "#284577"),
    "table_alt": ("#F8FAFC", "#141920"),
    "success": ("#16856B", "#34D399"),
    "success_bg": ("#E6FFFA", "#12352F"),
    "warning": ("#B7791F", "#FBBF24"),
    "danger": ("#C53030", "#F87171"),
    "danger_hover": ("#9B2C2C", "#DC5B5B"),
    "danger_bg": ("#FFF5F5", "#3B1E24"),
    "sidebar_muted": ("#829AB1", "#8F9AAA"),
    "header_muted": ("#BCCCDC", "#B5C0CF"),
}

FONT_FAMILY = "Segoe UI"


def cor_atual(nome: str, modo: str | None = None) -> str:
    """Resolve uma cor da paleta para widgets ttk, que não aceitam tuplos."""

    cor = COLORS[nome]
    if isinstance(cor, str):
        return cor
    modo_ativo = modo or ctk.get_appearance_mode()
    return cor[1] if modo_ativo.casefold() == "dark" else cor[0]
