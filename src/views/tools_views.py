"""Telas das ferramentas de importação e relatório."""

from __future__ import annotations

import webbrowser
from datetime import date
from tkinter import filedialog

import customtkinter as ctk

from src.config.paths import REPORTS_DIR
from src.i18n import tr
from src.presentation import formatar_data, formatar_moeda, interpretar_data_filtro
from src.views.components import DatePickerDialog, PageHeader, StatusBanner
from src.views.theme import COLORS, FONT_FAMILY


class ToolView(ctk.CTkFrame):
    """Base visual para operações pontuais com mensagem de resultado."""

    def __init__(self, master, title, subtitle):
        super().__init__(master, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        PageHeader(self, title, subtitle).grid(
            row=0, column=0, sticky="ew", padx=28, pady=(26, 18)
        )
        self.panel = ctk.CTkFrame(
            self, fg_color=COLORS["surface"], corner_radius=12,
            border_width=1, border_color=COLORS["border"],
        )
        self.panel.grid(row=1, column=0, sticky="new", padx=28)
        self.panel.grid_columnconfigure(0, weight=1)
        self.status = StatusBanner(self)
        self.status.grid(row=2, column=0, sticky="ew", padx=28, pady=16)

    def _label(self, texto, row):
        ctk.CTkLabel(
            self.panel, text=tr(texto), anchor="w", font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).grid(row=row, column=0, sticky="ew", padx=22, pady=(16, 6))


class CSVImportView(ToolView):
    def __init__(self, master):
        super().__init__(master, "Importar CSV", "Integre vendas validadas ao MiniCRM.")
        self._label("Arquivo CSV", 0)
        line = ctk.CTkFrame(self.panel, fg_color="transparent")
        line.grid(row=1, column=0, sticky="ew", padx=22)
        line.grid_columnconfigure(0, weight=1)
        self.path = ctk.CTkEntry(line, height=40, placeholder_text=tr("Selecione um arquivo .csv"))
        self.path.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(line, text=tr("Procurar"), width=100, height=40, command=self.selecionar).grid(
            row=0, column=1, padx=(10, 0)
        )
        ctk.CTkButton(
            self.panel, text=tr("Importar vendas"), height=42, command=self.importar,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=(FONT_FAMILY, 13, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=22, pady=22)
        self.status.mostrar("Selecione o CSV. A importação é transacional e evita duplicações.")

    def selecionar(self):
        caminho = filedialog.askopenfilename(filetypes=[(tr("Arquivos CSV"), "*.csv")])
        if caminho:
            self.path.delete(0, "end")
            self.path.insert(0, caminho)

    def importar(self):
        try:
            # Pandas só é carregado quando a importação é realmente solicitada.
            from src.services.importacao_csv_service import ImportacaoCSVService

            resumo = ImportacaoCSVService().importar(self.path.get().strip())
            texto = tr(
                "Importação concluída: {orders} pedidos, {customers} clientes e {revenue}.",
                orders=resumo.pedidos_criados, customers=resumo.clientes_criados,
                revenue=formatar_moeda(resumo.faturacao_importada),
            )
            if resumo.arquivo_ja_importado:
                texto = "Este arquivo já foi importado anteriormente; nenhum dado foi duplicado."
            self.status.mostrar(texto, "success")
        except Exception as error:
            self.status.mostrar(str(error), "error")


class ReportsView(ToolView):
    def __init__(self, master):
        super().__init__(master, "Relatórios", "Gere um relatório HTML autônomo e filtrado.")
        self._label("Arquivo de saída", 0)
        output = ctk.CTkFrame(self.panel, fg_color="transparent")
        output.grid(row=1, column=0, sticky="ew", padx=22)
        output.grid_columnconfigure(0, weight=1)
        self.path = ctk.CTkEntry(output, height=40)
        self.path.grid(row=0, column=0, sticky="ew")
        default = REPORTS_DIR / f"relatorio_{date.today():%Y%m%d}.html"
        self.path.insert(0, str(default))
        ctk.CTkButton(output, text=tr("Procurar"), width=100, height=40, command=self.selecionar).grid(
            row=0, column=1, padx=(10, 0)
        )
        dates = ctk.CTkFrame(self.panel, fg_color="transparent")
        dates.grid(row=2, column=0, sticky="ew", padx=22, pady=(16, 0))
        dates.grid_columnconfigure((0, 1), weight=1)
        self.inicio = self._date_field(dates, 0, "Data inicial (DD/MM/AAAA)")
        self.fim = self._date_field(dates, 1, "Data final (DD/MM/AAAA)")
        ctk.CTkButton(
            self.panel, text=tr("Gerar e abrir relatório completo"), height=42,
            command=self.gerar,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=(FONT_FAMILY, 13, "bold"),
        ).grid(row=3, column=0, sticky="w", padx=22, pady=22)
        self.status.mostrar("O HTML gerado inclui indicadores, tabelas e gráficos incorporados.")

    def _date_field(self, master, column, label):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 8) if column == 0 else (8, 0))
        ctk.CTkLabel(frame, text=tr(label), anchor="w", text_color=COLORS["muted"]).pack(fill="x")
        line = ctk.CTkFrame(frame, fg_color="transparent")
        line.pack(fill="x", pady=(5, 0))
        line.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(line, height=38, placeholder_text="DD/MM/AAAA")
        entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            # O ícone mantém o filtro compacto quando os dois campos ficam lado a lado.
            line, text="📅", width=44, height=38,
            command=lambda: self._open_calendar(entry),
            fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
            hover_color=COLORS["border"], font=(FONT_FAMILY, 16),
        ).grid(row=0, column=1, padx=(8, 0))
        return entry

    def _open_calendar(self, entry):
        """Abre no mês digitado ou no mês atual quando o campo está vazio ou inválido."""

        try:
            initial_date = interpretar_data_filtro(entry.get())
        except ValueError:
            initial_date = None

        def apply_date(selected_date):
            entry.delete(0, "end")
            if selected_date is not None:
                entry.insert(0, formatar_data(selected_date))

        self.calendar_dialog = DatePickerDialog(self, initial_date, apply_date)

    def selecionar(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[(tr("Relatório HTML"), "*.html")]
        )
        if caminho:
            self.path.delete(0, "end")
            self.path.insert(0, caminho)

    def gerar(self):
        try:
            # Jinja2 só é necessário no momento de gerar o ficheiro HTML.
            from src.services.relatorio_html_service import RelatorioHTMLService

            inicio = interpretar_data_filtro(self.inicio.get())
            fim = interpretar_data_filtro(self.fim.get())
            caminho = RelatorioHTMLService().gerar(
                caminho_saida=self.path.get().strip(), data_inicio=inicio, data_fim=fim,
            )
            webbrowser.open(caminho.as_uri())
            self.status.mostrar(tr("Relatório gerado em {path}", path=caminho), "success")
        except Exception as error:
            self.status.mostrar(str(error), "error")
