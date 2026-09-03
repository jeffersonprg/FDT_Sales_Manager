"""Gera o relatório PDF da auditoria de segurança.

Uso:
    python docs/security-audit/gerar_relatorio_pdf.py

Dependência: reportlab. O script lê achados.json no mesmo diretório.
"""

from __future__ import annotations

import json
from html import escape as xml_escape
from pathlib import Path

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Circle, Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "achados.json"
OUTPUT_PATH = ROOT / "relatorio-auditoria-seguranca.pdf"

CRITICAL = HexColor("#B91C1C")
HIGH = HexColor("#EA580C")
MEDIUM = HexColor("#D97706")
LOW = HexColor("#2563EB")
STRONG = HexColor("#059669")
INFO = HexColor("#64748B")
NAVY = HexColor("#0F172A")
SLATE = HexColor("#334155")
MUTED = HexColor("#64748B")
LINE = HexColor("#E2E8F0")
SURFACE = HexColor("#F8FAFC")
WHITE = colors.white


def register_fonts() -> tuple[str, str, str]:
    """Usa Segoe UI no Windows e fontes PDF padrão como fallback."""

    windows_fonts = Path("C:/Windows/Fonts")
    regular = windows_fonts / "segoeui.ttf"
    semibold = windows_fonts / "seguisb.ttf"
    bold = windows_fonts / "segoeuib.ttf"
    if regular.is_file() and semibold.is_file() and bold.is_file():
        pdfmetrics.registerFont(TTFont("AuditRegular", regular))
        pdfmetrics.registerFont(TTFont("AuditSemi", semibold))
        pdfmetrics.registerFont(TTFont("AuditBold", bold))
        return "AuditRegular", "AuditSemi", "AuditBold"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Bold"


FONT, FONT_SEMI, FONT_BOLD = register_fonts()


class AuditDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=24 * mm,
            bottomMargin=19 * mm,
            title="Relatório de Auditoria de Segurança - FDT Sales Manager",
            author="Auditoria automatizada assistida por Codex",
            subject="Auditoria das cinco categorias de segurança solicitadas",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )
        self.addPageTemplates(PageTemplate(id="audit", frames=[frame], onPage=draw_header_footer))


def draw_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(20 * mm, height - 17 * mm, width - 20 * mm, height - 17 * mm)
    canvas.setFont(FONT_SEMI, 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, height - 13 * mm, "Relatório de Auditoria de Segurança - FDT Sales Manager")
    canvas.drawRightString(width - 20 * mm, 11 * mm, f"Página {doc.page}")
    canvas.line(20 * mm, 15 * mm, width - 20 * mm, 15 * mm)
    canvas.restoreState()


styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "AuditTitle",
    parent=styles["Title"],
    fontName=FONT_BOLD,
    fontSize=25,
    leading=30,
    textColor=WHITE,
    alignment=TA_LEFT,
    spaceAfter=8,
)
SUBTITLE = ParagraphStyle(
    "AuditSubtitle",
    parent=styles["Normal"],
    fontName=FONT,
    fontSize=11,
    leading=16,
    textColor=HexColor("#DBEAFE"),
)
H1 = ParagraphStyle(
    "AuditH1",
    parent=styles["Heading1"],
    fontName=FONT_BOLD,
    fontSize=18,
    leading=22,
    textColor=NAVY,
    spaceBefore=5,
    spaceAfter=10,
)
H2 = ParagraphStyle(
    "AuditH2",
    parent=styles["Heading2"],
    fontName=FONT_BOLD,
    fontSize=13,
    leading=17,
    textColor=SLATE,
    spaceBefore=9,
    spaceAfter=6,
)
BODY = ParagraphStyle(
    "AuditBody",
    parent=styles["BodyText"],
    fontName=FONT,
    fontSize=9.3,
    leading=13.2,
    textColor=SLATE,
    spaceAfter=6,
)
SMALL = ParagraphStyle(
    "AuditSmall",
    parent=BODY,
    fontSize=7.7,
    leading=10.4,
    textColor=MUTED,
)
TABLE_TEXT = ParagraphStyle(
    "AuditTable",
    parent=BODY,
    fontSize=7.4,
    leading=9.7,
    spaceAfter=0,
)
TABLE_HEAD = ParagraphStyle(
    "AuditTableHead",
    parent=TABLE_TEXT,
    fontName=FONT_BOLD,
    textColor=WHITE,
)
CODE = ParagraphStyle(
    "AuditCode",
    parent=styles["Code"],
    fontName="Courier",
    fontSize=6.7,
    leading=9.2,
    textColor=NAVY,
    backColor=HexColor("#F1F5F9"),
    borderColor=LINE,
    borderWidth=0.5,
    borderPadding=7,
    spaceBefore=3,
    spaceAfter=8,
)
CALLOUT = ParagraphStyle(
    "AuditCallout",
    parent=BODY,
    fontName=FONT_SEMI,
    textColor=HexColor("#065F46"),
    backColor=HexColor("#ECFDF5"),
    borderColor=HexColor("#A7F3D0"),
    borderWidth=0.6,
    borderPadding=9,
    spaceAfter=10,
)
ISSUE = ParagraphStyle(
    "AuditIssue",
    parent=BODY,
    backColor=HexColor("#F8FAFC"),
    borderColor=LINE,
    borderWidth=0.6,
    borderPadding=8,
)


def p(text: str, style=BODY) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], style=BODY) -> list[Paragraph]:
    return [Paragraph(f"• {item}", style) for item in items]


def section(title: str) -> list:
    return [Spacer(1, 2 * mm), p(title, H1), HRFlowable(width="100%", thickness=1, color=LINE), Spacer(1, 2 * mm)]


def severity_donut(severity: dict[str, int]) -> Drawing:
    values = [
        severity.get("critical", 0),
        severity.get("high", 0),
        severity.get("medium", 0),
        severity.get("low", 0),
        severity.get("informational", 0),
    ]
    palette = [CRITICAL, HIGH, MEDIUM, LOW, INFO]
    labels = ["Crítica", "Alta", "Média", "Baixa", "Informativa"]
    if sum(values) == 0:
        values = [1]
        palette = [STRONG]
        labels = ["Sem achados"]

    d = Drawing(240, 165)
    pie = Pie()
    pie.x = 10
    pie.y = 27
    pie.width = 105
    pie.height = 105
    pie.data = values
    pie.sideLabels = False
    for idx, color in enumerate(palette):
        pie.slices[idx].fillColor = color
        pie.slices[idx].strokeColor = WHITE
        pie.slices[idx].strokeWidth = 1
    d.add(pie)
    d.add(Circle(62.5, 79.5, 28, fillColor=WHITE, strokeColor=WHITE))
    d.add(String(62.5, 83, str(sum(severity.values())), fontName=FONT_BOLD, fontSize=17, fillColor=NAVY, textAnchor="middle"))
    d.add(String(62.5, 69, "observação", fontName=FONT, fontSize=7.5, fillColor=MUTED, textAnchor="middle"))
    d.add(String(10, 149, "Achados por severidade", fontName=FONT_BOLD, fontSize=10, fillColor=NAVY))
    y = 127
    for label, value, color in zip(labels, values, palette):
        if len(labels) > 1 and value == 0:
            display_value = 0
        else:
            display_value = value
        d.add(Rect(135, y - 7, 8, 8, fillColor=color, strokeColor=None))
        d.add(String(149, y - 6, f"{label}: {display_value}", fontName=FONT, fontSize=7.6, fillColor=SLATE))
        y -= 19
    return d


def category_bars(categories: dict[str, int]) -> Drawing:
    labels = [
        ("Banco", categories.get("banco_sem_tranca", 0)),
        ("Permissão", categories.get("permissao_no_navegador", 0)),
        ("IDOR", categories.get("idor", 0)),
        ("Segredos", categories.get("chaves_expostas", 0)),
        ("XSS", categories.get("xss", 0)),
    ]
    d = Drawing(240, 165)
    d.add(String(8, 149, "Achados por categoria", fontName=FONT_BOLD, fontSize=10, fillColor=NAVY))
    max_value = max(1, max(value for _, value in labels))
    chart_x = 68
    chart_width = 145
    y = 124
    for label, value in labels:
        d.add(String(8, y, label, fontName=FONT, fontSize=7.4, fillColor=SLATE))
        d.add(Rect(chart_x, y - 2, chart_width, 9, fillColor=HexColor("#E2E8F0"), strokeColor=None))
        if value:
            d.add(Rect(chart_x, y - 2, chart_width * value / max_value, 9, fillColor=INFO, strokeColor=None))
        d.add(String(220, y, str(value), fontName=FONT_BOLD, fontSize=7.6, fillColor=NAVY))
        y -= 24
    d.add(String(8, 6, "A barra de XSS é informativa; não representa vulnerabilidade atual.", fontName=FONT, fontSize=6.5, fillColor=MUTED))
    return d


def card(value: str, label: str, color: colors.Color) -> Table:
    content = [
        p(value, ParagraphStyle("cv", parent=H1, alignment=TA_CENTER, textColor=color, spaceAfter=1)),
        p(label, ParagraphStyle("cl", parent=SMALL, alignment=TA_CENTER, fontName=FONT_SEMI)),
    ]
    table = Table([[content]], colWidths=[30 * mm], rowHeights=[22 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def build_story(data: dict) -> list:
    story: list = []

    cover = Table(
        [[[
            p("RELATÓRIO TÉCNICO", ParagraphStyle("eyebrow", parent=SMALL, fontName=FONT_BOLD, textColor=HexColor("#93C5FD"), spaceAfter=6)),
            p("Relatório de Auditoria de Segurança — FDT Sales Manager", TITLE),
            p("Auditoria orientada às cinco categorias solicitadas, adaptadas à arquitetura desktop Python/SQLite.", SUBTITLE),
        ]]],
        colWidths=[170 * mm],
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 0, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))
    story += [Spacer(1, 12 * mm), cover, Spacer(1, 12 * mm)]
    meta = [
        [p("DATA", SMALL), p("03/09/2026", BODY)],
        [p("ESCOPO", SMALL), p("Código atual, histórico Git, SQLite, GUI, relatório HTML, scripts e configuração PyInstaller.", BODY)],
        [p("STACK", SMALL), p("Python + CustomTkinter + sqlite3 + Jinja2; sem API, ORM, autenticação ou frontend web.", BODY)],
        [p("RESULTADO", SMALL), p("0 vulnerabilidades confirmadas · 0 configurações perigosas · 1 melhoria defensiva informativa", BODY)],
    ]
    mt = Table(meta, colWidths=[30 * mm, 140 * mm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [mt, Spacer(1, 10 * mm), p(
        "Nota metodológica: banco sem tranca foi mapeado para o isolamento real pelo usuário/processo do Windows; permissão no navegador e IDOR foram avaliados pela ausência/presença de rotas, identidades e gates; segredos foram verificados no estado atual e histórico; XSS foi validado estaticamente e com payloads em base temporária.",
        CALLOUT,
    ), PageBreak()]

    story += section("1. Resumo executivo")
    cards = Table([[
        card("0", "CRÍTICAS", CRITICAL),
        card("0", "ALTAS", HIGH),
        card("0", "MÉDIAS", MEDIUM),
        card("0", "BAIXAS", LOW),
        card("1", "INFORMATIVA", INFO),
    ]], colWidths=[34 * mm] * 5)
    cards.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1)]))
    story += [cards, Spacer(1, 7 * mm)]
    charts = Table([[
        severity_donut(data["summary"]["severity"]),
        category_bars(data["summary"]["categories"]),
    ]], colWidths=[85 * mm, 85 * mm])
    charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOX", (0, 0), (-1, -1), 0.6, LINE)]))
    story += [charts, Spacer(1, 5 * mm)]
    story += [p(
        "Não foi demonstrado caminho explorável nas cinco categorias. A única observação acionável é preventiva: adicionar Content-Security-Policy e testes permanentes para todos os campos persistidos do relatório HTML.",
        CALLOUT,
    )]

    story += section("2. Stack e adaptação das categorias")
    stack_rows = [
        [p("Camada", TABLE_HEAD), p("Detecção", TABLE_HEAD), p("Implicação para a auditoria", TABLE_HEAD)],
        [p("Aplicação", TABLE_TEXT), p("Python desktop / CustomTkinter", TABLE_TEXT), p("Sem servidor ou navegador como frontend", TABLE_TEXT)],
        [p("Dados", TABLE_TEXT), p("SQLite via sqlite3; sem ORM", TABLE_TEXT), p("107 chamadas SQL revisadas diretamente", TABLE_TEXT)],
        [p("Auth", TABLE_TEXT), p("Nenhuma identidade/sessão/papel", TABLE_TEXT), p("Trust boundary: conta/processo do Windows", TABLE_TEXT)],
        [p("HTML", TABLE_TEXT), p("Jinja2 + SVG em data URI", TABLE_TEXT), p("Autoescape e sinks manuais auditados", TABLE_TEXT)],
        [p("Deploy", TABLE_TEXT), p("PyInstaller onedir", TABLE_TEXT), p("Sem Docker, CI, Helm ou Terraform", TABLE_TEXT)],
    ]
    st = Table(stack_rows, colWidths=[28 * mm, 54 * mm, 88 * mm], repeatRows=1)
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SURFACE]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [st, Spacer(1, 4 * mm)]
    mapping = [
        "Banco sem tranca: verificação do isolamento por conta do Windows e diretório LocalAppData; não existe tenant de aplicação.",
        "Permissão no navegador: busca de gates por papel e cruzamento de todas as ações da GUI com seus serviços.",
        "IDOR: enumeração AST de todos os handlers (0 HTTP) e revisão dos 37 métodos públicos de negócio.",
        "Chaves expostas: workspace, scripts, documentação, commits e bundle PyInstaller final.",
        "XSS: sinks HTML/JS, template, SVG, URLs, autoescape e teste dinâmico com dados persistidos.",
    ]
    story += bullets(mapping)

    story += [PageBreak()] + section("3. Pontos fortes e pontos fracos")
    story += [p("Pontos fortes", H2)]
    strengths = [
        "Jinja2 com autoescape para HTML/XML (`relatorio_html_service.py:268-271`).",
        "Escape manual antes de inserir texto nos SVGs (`relatorio_html_service.py:101-115, 165-169`).",
        "Valores SQL externos usam placeholders; as únicas duas f-strings SQL contêm identificadores internos fixos.",
        "Transações com rollback em pedido, conversão de lead e importação CSV.",
        "Foreign keys e constraints de integridade ativadas no SQLite (`database.py:15-18, 295-428`).",
        "No build, dados graváveis ficam no LocalAppData por usuário (`paths.py:32-38`).",
        "Banco `.db` ignorado e ausente do histórico versionado.",
    ]
    story += bullets(strengths)
    story += [p("Pontos fracos / limitações", H2)]
    weaknesses = [
        "Ausência de CSP e de testes versionados para todos os campos persistidos exibidos no HTML (I-001, informativa).",
        "A arquitetura local precisará de novo threat model antes de qualquer API, sincronização ou base compartilhada.",
        "A suíte geral chegou a 59% antes do timeout; a suíte específica de relatório passou 5/5.",
    ]
    story += bullets(weaknesses)

    story += section("4. Resultado detalhado por categoria")
    category_rows = [
        [p("Categoria", TABLE_HEAD), p("Resultado", TABLE_HEAD), p("Evidência principal", TABLE_HEAD)],
        [p("1. Banco sem tranca", TABLE_TEXT), p("Não aplicável como vulnerabilidade", TABLE_TEXT), p("Base local por usuário; sem tenant/auth (`paths.py:27-38`)", TABLE_TEXT)],
        [p("2. Permissão no navegador", TABLE_TEXT), p("Não aplicável", TABLE_TEXT), p("GUI desktop; zero gates de papel; matriz completa auditada", TABLE_TEXT)],
        [p("3. IDOR", TABLE_TEXT), p("Não aplicável", TABLE_TEXT), p("0 handlers HTTP; 37 métodos de negócio inventariados", TABLE_TEXT)],
        [p("4. Chaves expostas", TABLE_TEXT), p("Nenhum achado", TABLE_TEXT), p("0 no workspace/histórico; bundle final varrido", TABLE_TEXT)],
        [p("5. XSS", TABLE_TEXT), p("0 vulnerabilidades; 1 melhoria informativa", TABLE_TEXT), p("Autoescape + escape SVG + teste dinâmico aprovado", TABLE_TEXT)],
    ]
    ct = Table(category_rows, colWidths=[44 * mm, 50 * mm, 76 * mm], repeatRows=1)
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SURFACE]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [ct, Spacer(1, 5 * mm)]

    story += section("5. Tabela de achados")
    finding = data["findings"][0]
    chip = Table([[p("INFORMATIVA", ParagraphStyle("chip", parent=TABLE_TEXT, fontName=FONT_BOLD, textColor=WHITE, alignment=TA_CENTER))]], colWidths=[25 * mm])
    chip.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INFO), ("BOX", (0, 0), (-1, -1), 0, INFO), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    finding_rows = [
        [p("Severidade", TABLE_HEAD), p("Arquivo:linha", TABLE_HEAD), p("Descrição", TABLE_HEAD)],
        [chip, p("src/templates/relatorio_comercial.html:3-8<br/>tests/test_relatorio_html_service.py:92-103", TABLE_TEXT), p(xml_escape(finding["title"]) + "<br/><br/><b>Classificação:</b> melhoria defensiva; não é vulnerabilidade atual.", TABLE_TEXT)],
    ]
    ft = Table(finding_rows, colWidths=[30 * mm, 60 * mm, 80 * mm], repeatRows=1)
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    finding_detail = [
        p("I-001 - Reforçar defesa em profundidade e testes XSS", H2),
        p("O template não declara Content-Security-Policy e o teste versionado cobre apenas o título. A auditoria dinâmica confirmou que cliente, produto, referência e SVG estão escapados na versão atual; portanto, não há exploração atual demonstrada."),
        Preformatted(
        "# src/services/relatorio_html_service.py:268-271\n"
        "ambiente = Environment(\n"
        "    loader=FileSystemLoader(TEMPLATES_DIR),\n"
        "    autoescape=select_autoescape((\"html\", \"xml\")),\n"
        ")",
        CODE,
        ),
        Preformatted(
        "# tests/test_relatorio_html_service.py:92-103\n"
        "titulo=\"<script>alert('x')</script>\"\n"
        "assert \"<script>alert\" not in conteudo\n"
        "assert \"&lt;script&gt;\" in conteudo",
        CODE,
        ),
        p("<b>Condição de explorabilidade:</b> exigiria regressão futura no escape ou novo sink HTML inseguro, seguida da abertura do relatório com dado malicioso."),
    ]
    story += [ft, Spacer(1, 5 * mm), KeepTogether(finding_detail)]

    story += section("6. Recomendações priorizadas")
    rec_rows = [
        [p("Prioridade", TABLE_HEAD), p("Ação", TABLE_HEAD), p("Motivo", TABLE_HEAD)],
        [p("P1", TABLE_TEXT), p("Nenhuma correção urgente", TABLE_TEXT), p("0 vulnerabilidades confirmadas", TABLE_TEXT)],
        [p("P2", TABLE_TEXT), p("Automatizar secret scan no histórico e bundle em CI", TABLE_TEXT), p("Transformar a verificação manual em controle contínuo", TABLE_TEXT)],
        [p("P2", TABLE_TEXT), p("Revisar threat model antes de API/base compartilhada", TABLE_TEXT), p("Tenant/auth/IDOR hoje não se aplicam", TABLE_TEXT)],
        [p("P3", TABLE_TEXT), p("Adicionar CSP e testes XSS amplos", TABLE_TEXT), p("I-001, defesa em profundidade", TABLE_TEXT)],
    ]
    rt = Table(rec_rows, colWidths=[24 * mm, 86 * mm, 60 * mm], repeatRows=1)
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SURFACE]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [rt, Spacer(1, 7 * mm)]
    story += [p("Cobertura e limitações", H2)]
    story += bullets(data["limitations"])

    story += [PageBreak()] + section("7. ISSUES PARA O GITHUB")
    story += [p("--- ISSUE 1 ---", ISSUE)]
    story += [p("### Título", H2)]
    story += [p(xml_escape("[Segurança] Reforçar defesa contra regressões XSS no relatório HTML"))]
    story += [p("### Labels sugeridas", H2)]
    story += [p(xml_escape("`security`, `informativa`"))]
    story += [p("### Descrição do problema e explorabilidade", H2)]
    story += [p("O relatório está protegido atualmente por autoescape do Jinja2 e escape manual dos SVGs; não há XSS explorável confirmado. Como defesa em profundidade, falta CSP e o teste versionado cobre apenas o título. Uma regressão futura com `safe`, `Markup` ou HTML manual poderia executar conteúdo quando o operador abrisse um relatório malicioso.")]
    story += [p("### Evidência", H2)]
    story += [Preformatted(
        "`src/templates/relatorio_comercial.html:3-8`\n\n"
        "```html\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <title>{{ titulo }}</title>\n"
        "  <link rel=\"icon\" type=\"image/png\" href=\"{{ favicon_data_uri }}\">\n"
        "  <style>\n"
        "```",
        CODE,
    )]
    story += [p("Não há meta CSP no cabeçalho.")]
    story += [Preformatted(
        "`tests/test_relatorio_html_service.py:92-103`\n\n"
        "```python\n"
        "def test_relatorio_escapa_titulo_html(...):\n"
        "    titulo=\"<script>alert('x')</script>\"\n"
        "    assert \"<script>alert\" not in conteudo\n"
        "    assert \"&lt;script&gt;\" in conteudo\n"
        "```",
        CODE,
    )]
    story += [p("O teste cobre o título, mas não os demais campos persistidos nem o SVG decodificado.")]
    story += [p("### Impacto", H2)]
    story += [p("Defesa preventiva contra uma futura regressão de XSS em relatórios locais. Não há vulnerabilidade explorável confirmada na versão atual.")]
    story += [p("### Sugestão de correção", H2)]
    for line in [
        "1. Adicionar CSP compatível com o documento autônomo: `default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'`.",
        "2. Criar testes parametrizados para título, cliente, produto, categoria, referência externa e nome de arquivo.",
        "3. Decodificar os SVGs base64 e verificar ausência do payload bruto e presença da versão escapada.",
        "4. Manter proibidos `|safe`, `Markup`, `mark_safe`, HTML manual com dados e URLs de usuário sem validação.",
    ]:
        story += [p(xml_escape(line))]
    criteria = [
        "- [ ] O HTML inclui CSP documentada e compatível com os recursos locais.",
        "- [ ] Gráficos e estilos continuam funcionando offline.",
        "- [ ] Testes cobrem título, cliente, produto, categoria, referência e nome de arquivo.",
        "- [ ] Testes decodificam os SVGs e verificam o escape.",
        "- [ ] Nenhum payload bruto aparece no HTML ou SVG.",
        "- [ ] `tests/test_relatorio_html_service.py` permanece verde.",
    ]
    story += [KeepTogether([
        p("### Critérios de aceite", H2),
        p(xml_escape(criteria[0])),
    ])]
    for line in criteria[1:]:
        story += [p(xml_escape(line))]
    story += [p("--- FIM ISSUE 1 ---", ISSUE)]

    story += section("8. Evidências de validação")
    story += [p("Resultados automatizados", H2)]
    evidence_rows = [
        [p("Verificação", TABLE_HEAD), p("Resultado", TABLE_HEAD)],
        [p("Enumeração de rotas", TABLE_TEXT), p("0 handlers HTTP", TABLE_TEXT)],
        [p("Métodos públicos de negócio", TABLE_TEXT), p("37 revisados + 1 serializador DTO", TABLE_TEXT)],
        [p("Chamadas SQL", TABLE_TEXT), p("107; 105 literais e 2 f-strings internas de migração", TABLE_TEXT)],
        [p("Segredos no histórico", TABLE_TEXT), p("0 correspondências", TABLE_TEXT)],
        [p("Teste dinâmico XSS", TABLE_TEXT), p("10/10 assertivas de escape aprovadas", TABLE_TEXT)],
        [p("Testes de relatório", TABLE_TEXT), p("5/5 aprovados em 8,84 s", TABLE_TEXT)],
        [p("Bundle", TABLE_TEXT), p("1.907 arquivos / 115.981.209 bytes; 0 segredos confirmados", TABLE_TEXT)],
    ]
    et = Table(evidence_rows, colWidths=[70 * mm, 100 * mm], repeatRows=1)
    et.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SURFACE]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [et, Spacer(1, 7 * mm)]
    story += [p("Arquivos complementares", H2)]
    story += bullets([
        "docs/security-audit/relatorio-auditoria-seguranca.md",
        "docs/security-audit/achados.json",
        "docs/security-audit/inventario-rotas.md",
        "docs/security-audit/metodologia.md",
        "docs/security-audit/gerar_relatorio_pdf.py",
    ])
    story += [Spacer(1, 8 * mm), p("Conclusão: nenhuma das cinco classes apresentou vulnerabilidade explorável na arquitetura e no código auditados. A observação I-001 é explicitamente preventiva.", CALLOUT)]
    return story


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    doc = AuditDocTemplate(str(OUTPUT_PATH))
    doc.build(build_story(data))
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
