"""Telas de consulta e operações dos módulos comerciais."""

from __future__ import annotations

import customtkinter as ctk

from src.i18n import tr
from src.models.cliente import Cliente
from src.models.lead import Lead
from src.models.pedido import Pedido
from src.models.produto import Produto
from src.presentation import (
    formatar_data,
    formatar_moeda,
    formatar_texto,
    interpretar_decimal,
    interpretar_id_opcao,
    interpretar_inteiro_opcional,
    interpretar_datetime_evento,
    formatar_opcao_entidade,
    texto_opcional,
)
from src.services.cliente_service import ClienteService
from src.services.lead_service import LeadService
from src.services.pedido_service import PedidoService
from src.services.produto_service import ProdutoService
from src.views.components import (
    ConfirmationDialog,
    DataTable,
    FormDialog,
    PageHeader,
    StatusBanner,
)
from src.views.order_dialog import OrderDetailsDialog, OrderDialog
from src.views.theme import COLORS, FONT_FAMILY


class ListView(ctk.CTkFrame):
    """Reúne pesquisa, ações, tabela e mensagens num layout comum."""

    def __init__(self, master, title, subtitle, columns):
        super().__init__(master, fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        PageHeader(self, title, subtitle, self.carregar).grid(
            row=0, column=0, sticky="ew", padx=28, pady=(26, 18)
        )
        self.filters = ctk.CTkFrame(self, fg_color="transparent")
        self.filters.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))
        self.filters.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(
            self.filters, placeholder_text=tr("Pesquisar…"), height=38,
            fg_color=COLORS["surface"], border_color=COLORS["border"],
            font=(FONT_FAMILY, 12),
        )
        self.search.grid(row=0, column=0, sticky="ew")
        self.search.bind("<Return>", lambda _event: self.carregar())
        ctk.CTkButton(
            self.filters, text=tr("Pesquisar"), width=100, height=38, command=self.carregar,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
        ).grid(row=0, column=1, padx=(10, 0))
        self.table = DataTable(self, columns)
        self.table.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 10))
        self.status = StatusBanner(self)
        self.status.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 26))
        self.status.mostrar("Selecione uma linha para editar ou alterar o estado.")

    def carregar(self):
        rows = self.obter_linhas(self.search.get().strip())
        self.table.definir_linhas(rows)
        total = len(rows)
        mensagem = "{count} registo apresentado." if total == 1 else "{count} registos apresentados."
        self.status.mostrar(tr(mensagem, count=total))

    def adicionar_acao(self, texto, command, destaque=False):
        column = max(
            int(widget.grid_info()["column"])
            for widget in self.filters.grid_slaves(row=0)
        ) + 1
        button = ctk.CTkButton(
            self.filters, text=tr(texto), width=110, height=38, command=command,
            fg_color=COLORS["blue"] if destaque else COLORS["navy"],
            hover_color=COLORS["blue_hover"] if destaque else COLORS["navy_hover"],
            font=(FONT_FAMILY, 11, "bold"),
        )
        button.grid(row=0, column=column, padx=(10, 0))
        return button

    def id_selecionado(self):
        row = self.table.obter_linha_selecionada()
        if row is None:
            self.status.mostrar("Selecione primeiro um registo na tabela.", "error")
            return None
        return int(row[0])


class ClientesView(ListView):
    """Permite consultar e manter clientes sem apagar o histórico."""

    def __init__(self, master):
        super().__init__(master, "Clientes", "Clientes ativos e respetivos contactos.", (
            ("id", "ID", 60), ("nome", "Nome", 210), ("empresa", "Empresa", 170),
            ("email", "Email", 220), ("telefone", "Telefone", 130),
            ("pais", "País", 100), ("estado", "Estado", 90),
        ))
        self.adicionar_acao("Novo cliente", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Ativar/Inativar", self.alternar_estado)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    FIELDS = (
        ("nome", "Nome *"), ("empresa", "Empresa"), ("email", "Email"),
        ("telefone", "Telefone"), ("morada", "Morada"), ("pais", "País"),
        ("tipo_documento", "Tipo de documento"),
        ("numero_documento", "Número do documento"),
        ("observacoes", "Observações", "text"),
    )

    def obter_linhas(self, termo):
        clientes = ClienteService.pesquisar_clientes(termo, incluir_inativos=True)
        return [(c.id, c.nome, formatar_texto(c.empresa), formatar_texto(c.email),
                 formatar_texto(c.telefone), c.pais, tr(c.estado)) for c in clientes]

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo cliente", self.FIELDS, {"pais": "Portugal"}, self._criar,
        )

    def _cliente_dos_valores(self, values, cliente_id=None, estado="ATIVO"):
        return Cliente(
            id=cliente_id, nome=values["nome"], empresa=texto_opcional(values["empresa"]),
            email=texto_opcional(values["email"]), telefone=texto_opcional(values["telefone"]),
            morada=texto_opcional(values["morada"]), pais=values["pais"],
            tipo_documento=texto_opcional(values["tipo_documento"]),
            numero_documento=texto_opcional(values["numero_documento"]),
            observacoes=texto_opcional(values["observacoes"]), estado=estado,
        )

    def _criar(self, values):
        ClienteService.criar_cliente(self._cliente_dos_valores(values))
        self.carregar()
        self.status.mostrar("Cliente criado com sucesso.", "success")

    def editar(self):
        cliente_id = self.id_selecionado()
        if cliente_id is None:
            return
        cliente = ClienteService.buscar_cliente(cliente_id, incluir_inativos=True)
        initial = {key: getattr(cliente, key) or "" for key, *_ in self.FIELDS}
        self.dialog = FormDialog(
            self, "Editar cliente", self.FIELDS, initial,
            lambda values: self._atualizar(cliente, values),
        )

    def _atualizar(self, original, values):
        cliente = self._cliente_dos_valores(values, original.id, original.estado)
        ClienteService.atualizar_cliente(cliente)
        self.carregar()
        self.status.mostrar("Cliente atualizado com sucesso.", "success")

    def alternar_estado(self):
        cliente_id = self.id_selecionado()
        if cliente_id is None:
            return
        cliente = ClienteService.buscar_cliente(cliente_id, incluir_inativos=True)
        if cliente.estado == "ATIVO":
            self.dialog = ConfirmationDialog(
                self,
                "Inativar cliente",
                tr("O cliente {name} deixará de receber novos pedidos. O histórico será preservado.", name=cliente.nome),
                lambda: self._inativar(cliente_id),
                confirm_text="Inativar",
                danger=True,
            )
            return
        else:
            ClienteService.reativar_cliente(cliente_id)
            mensagem = "Cliente reativado com sucesso."
        self.carregar()
        self.status.mostrar(mensagem, "success")

    def _inativar(self, cliente_id):
        ClienteService.remover_cliente(cliente_id)
        self.carregar()
        self.status.mostrar(
            "Cliente inativado; o histórico foi preservado.", "success",
        )


class ProdutosView(ListView):
    """Mantém o catálogo e as regras de validade de cada produto."""

    def __init__(self, master):
        super().__init__(master, "Produtos", "Catálogo, preços e condições de acesso.", (
            ("id", "ID", 60), ("nome", "Produto", 230), ("categoria", "Categoria", 150),
            ("preco", "Preço", 110), ("validade", "Validade", 150),
            ("estado", "Estado", 90),
        ))
        self.adicionar_acao("Novo produto", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Ativar/Inativar", self.alternar_estado)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    FIELDS = (
        ("nome", "Nome *"), ("categoria", "Categoria"), ("preco", "Preço *"),
        ("tipo_validade", "Tipo de validade", "combo", ("VITALICIO", "TEMPORARIO")),
        ("duracao_dias", "Duração em dias (apenas temporário)"),
        ("descricao", "Descrição", "text"),
    )

    def obter_linhas(self, termo):
        produtos = ProdutoService.pesquisar_produtos(termo, apenas_ativos=False)
        return [(p.id, p.nome, formatar_texto(p.categoria), formatar_moeda(p.preco),
                 tr("Vitalício") if p.tipo_validade == "VITALICIO" else tr("{days} dias", days=p.duracao_dias),
                 tr("ATIVO" if p.ativo else "INATIVO")) for p in produtos]

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo produto", self.FIELDS,
            {"tipo_validade": "VITALICIO", "preco": "0,00"}, self._criar,
        )

    def _produto_dos_valores(self, values, produto_id=None, ativo=True):
        tipo = values["tipo_validade"]
        duracao = interpretar_inteiro_opcional(values["duracao_dias"], "duração")
        if tipo == "VITALICIO":
            duracao = None
        return Produto(
            id=produto_id, nome=values["nome"], categoria=texto_opcional(values["categoria"]),
            preco=interpretar_decimal(values["preco"], "preço"),
            descricao=texto_opcional(values["descricao"]), tipo_validade=tipo,
            duracao_dias=duracao, ativo=ativo,
        )

    def _criar(self, values):
        ProdutoService.criar_produto(self._produto_dos_valores(values))
        self.carregar()
        self.status.mostrar("Produto criado com sucesso.", "success")

    def editar(self):
        produto_id = self.id_selecionado()
        if produto_id is None:
            return
        produto = ProdutoService.buscar_produto(produto_id)
        initial = {key: getattr(produto, key) or "" for key, *_ in self.FIELDS}
        self.dialog = FormDialog(
            self, "Editar produto", self.FIELDS, initial,
            lambda values: self._atualizar(produto, values),
        )

    def _atualizar(self, original, values):
        produto = self._produto_dos_valores(values, original.id, original.ativo)
        ProdutoService.atualizar_produto(produto)
        self.carregar()
        self.status.mostrar("Produto atualizado com sucesso.", "success")

    def alternar_estado(self):
        produto_id = self.id_selecionado()
        if produto_id is None:
            return
        produto = ProdutoService.buscar_produto(produto_id)
        if produto.ativo:
            self.dialog = ConfirmationDialog(
                self,
                "Inativar produto",
                tr("O produto {name} deixará de estar disponível em novos pedidos. As vendas anteriores serão preservadas.", name=produto.nome),
                lambda: self._inativar(produto_id),
                confirm_text="Inativar",
                danger=True,
            )
            return
        else:
            ProdutoService.reativar_produto(produto_id)
            mensagem = "Produto reativado com sucesso."
        self.carregar()
        self.status.mostrar(mensagem, "success")

    def _inativar(self, produto_id):
        ProdutoService.desativar_produto(produto_id)
        self.carregar()
        self.status.mostrar(
            "Produto inativado; o histórico foi preservado.", "success",
        )


class LeadsView(ListView):
    """Acompanha o funil e converte oportunidades em clientes."""

    def __init__(self, master):
        super().__init__(master, "Leads", "Oportunidades e evolução do funil comercial.", (
            ("id", "ID", 60), ("nome", "Nome", 210), ("empresa", "Empresa", 160),
            ("contacto", "Contacto", 210), ("origem", "Origem", 120),
            ("produto", "Produto", 170), ("estado", "Estado", 120),
            ("criado", "Criado em", 110),
        ))
        self.adicionar_acao("Novo lead", self.novo, destaque=True)
        self.adicionar_acao("Editar", self.editar)
        self.adicionar_acao("Converter", self.converter)
        self.table.tree.bind("<Double-1>", lambda _event: self.editar())
        self.carregar()

    def obter_linhas(self, termo):
        leads = LeadService.pesquisar_leads(termo=termo)
        produtos = {p.id: p.nome for p in ProdutoService.listar_produtos()}
        return [(l.id, l.nome, formatar_texto(l.empresa),
                 formatar_texto(l.email or l.telefone), formatar_texto(l.origem),
                 formatar_texto(produtos.get(l.produto_interesse_id)),
                 tr(l.estado), formatar_data(l.criado_em)) for l in leads]

    def _opcoes_produtos(self):
        return (tr("— Sem produto —"),) + tuple(
            formatar_opcao_entidade(produto.id, produto.nome)
            for produto in ProdutoService.listar_produtos(apenas_ativos=True)
        )

    def _fields(self):
        return (
            ("nome", "Nome *"), ("empresa", "Empresa"),
            ("telefone", "Telefone"), ("email", "Email"),
            ("origem", "Origem"),
            ("estado", "Estado", "combo", ("NOVO", "CONTACTADO", "QUALIFICADO", "PERDIDO")),
            ("produto_interesse", "Produto de interesse", "combo", self._opcoes_produtos()),
            ("observacoes", "Observações", "text"),
        )

    def _opcao_produto(self, produto_id):
        if produto_id is None:
            return tr("— Sem produto —")
        produto = ProdutoService.buscar_produto(produto_id)
        return formatar_opcao_entidade(produto.id, produto.nome)

    def _lead_dos_valores(self, values, lead_id=None):
        return Lead(
            id=lead_id, nome=values["nome"], empresa=texto_opcional(values["empresa"]),
            telefone=texto_opcional(values["telefone"]), email=texto_opcional(values["email"]),
            origem=texto_opcional(values["origem"]), estado=values["estado"],
            produto_interesse_id=interpretar_id_opcao(values["produto_interesse"]),
            observacoes=texto_opcional(values["observacoes"]),
        )

    def novo(self):
        self.dialog = FormDialog(
            self, "Novo lead", self._fields(),
            {"estado": "NOVO", "produto_interesse": tr("— Sem produto —")}, self._criar,
        )

    def _criar(self, values):
        LeadService.criar_lead(self._lead_dos_valores(values))
        self.carregar()
        self.status.mostrar("Lead criado com sucesso.", "success")

    def editar(self):
        lead_id = self.id_selecionado()
        if lead_id is None:
            return
        lead = LeadService.buscar_lead(lead_id)
        if lead.estado == "CONVERTIDO":
            self.status.mostrar("Leads convertidos não podem ser editados.", "error")
            return
        fields = self._fields()
        initial = {
            "nome": lead.nome, "empresa": lead.empresa or "",
            "telefone": lead.telefone or "", "email": lead.email or "",
            "origem": lead.origem or "", "estado": lead.estado,
            "produto_interesse": self._opcao_produto(lead.produto_interesse_id),
            "observacoes": lead.observacoes or "",
        }
        self.dialog = FormDialog(
            self, "Editar lead", fields, initial,
            lambda values: self._atualizar(lead, values),
        )

    def _atualizar(self, original, values):
        atualizado = LeadService.atualizar_lead(
            self._lead_dos_valores(values, original.id)
        )
        if not atualizado:
            raise ValueError("O lead já foi convertido e não pode ser alterado.")
        self.carregar()
        self.status.mostrar("Lead atualizado com sucesso.", "success")

    def converter(self):
        lead_id = self.id_selecionado()
        if lead_id is None:
            return
        lead = LeadService.buscar_lead(lead_id)
        if lead.estado == "CONVERTIDO":
            self.status.mostrar("Este lead já foi convertido em cliente.", "error")
            return
        fields = (
            ("morada", "Morada do cliente"), ("pais", "País"),
            ("tipo_documento", "Tipo de documento"),
            ("numero_documento", "Número do documento"),
            ("observacoes_cliente", "Observações do cliente", "text"),
        )
        initial = {"pais": "Portugal", "observacoes_cliente": lead.observacoes or ""}
        self.dialog = FormDialog(
            self, tr("Converter {name}", name=lead.nome), fields, initial,
            lambda values: self._converter(lead, values),
        )

    def _converter(self, lead, values):
        # A conversão fica no serviço para garantir cliente e lead na mesma transação.
        cliente_id = LeadService.converter_em_cliente(
            lead_id=lead.id, morada=texto_opcional(values["morada"]),
            pais=values["pais"].strip() or "Portugal",
            tipo_documento=texto_opcional(values["tipo_documento"]),
            numero_documento=texto_opcional(values["numero_documento"]),
            observacoes_cliente=texto_opcional(values["observacoes_cliente"]),
        )
        self.carregar()
        self.status.mostrar(
            tr("Lead convertido com sucesso no cliente #{id}.", id=cliente_id), "success",
        )


class PedidosView(ListView):
    """Cria pedidos e aplica as transições comerciais permitidas."""

    def __init__(self, master):
        super().__init__(master, "Pedidos", "Histórico de pedidos e respetivos estados.", (
            ("id", "ID", 70), ("referencia", "Referência", 160),
            ("cliente", "Cliente", 200), ("data", "Data", 120),
            ("estado", "Estado", 110), ("itens", "Itens", 80), ("total", "Total", 120),
        ))
        self.adicionar_acao("Novo pedido", self.novo, destaque=True)
        self.adicionar_acao("Detalhes", self.detalhes)
        self.adicionar_acao("Marcar pago", self.pagar)
        self.adicionar_acao("Cancelar", self.cancelar)
        self.table.tree.bind("<Double-1>", lambda _event: self.detalhes())
        self.carregar()

    def obter_linhas(self, termo):
        pedidos = PedidoService.listar_pedidos()
        clientes = {
            cliente.id: cliente.nome
            for cliente in ClienteService.listar_clientes(incluir_inativos=True)
        }
        termo = termo.casefold()
        if termo:
            pedidos = [p for p in pedidos if (
                termo in (p.referencia_externa or "").casefold()
                or termo in str(p.id)
                or termo in clientes.get(p.cliente_id, "").casefold()
            )]
        return [(p.id, formatar_texto(p.referencia_externa),
                 clientes.get(p.cliente_id, tr("Cliente #{id}", id=p.cliente_id)),
                 formatar_data(p.data_pedido), tr(p.estado), len(p.itens),
                 formatar_moeda(p.total)) for p in pedidos]

    def novo(self):
        clientes = ClienteService.listar_clientes()
        produtos = ProdutoService.listar_produtos(apenas_ativos=True)
        if not clientes or not produtos:
            self.status.mostrar(
                "É necessário ter pelo menos um cliente e um produto ativos.", "error",
            )
            return
        self.dialog = OrderDialog(self, clientes, produtos, self._criar)

    def _criar(self, pedido: Pedido):
        pedido_id = PedidoService.criar_pedido(pedido)
        self.carregar()
        self.status.mostrar(tr("Pedido #{id} criado como PENDENTE.", id=pedido_id), "success")

    def detalhes(self):
        pedido_id = self.id_selecionado()
        if pedido_id is None:
            return
        pedido = PedidoService.buscar_pedido(pedido_id)
        cliente = ClienteService.buscar_cliente(pedido.cliente_id, incluir_inativos=True)
        produtos = {p.id: p.nome for p in ProdutoService.listar_produtos()}
        self.dialog = OrderDetailsDialog(self, pedido, cliente.nome, produtos)

    def pagar(self):
        self._abrir_transicao("PAGO", "Registar pagamento")

    def cancelar(self):
        self._abrir_transicao("CANCELADO", "Cancelar pedido")

    def _abrir_transicao(self, novo_estado, titulo):
        pedido_id = self.id_selecionado()
        if pedido_id is None:
            return
        pedido = PedidoService.buscar_pedido(pedido_id)
        if novo_estado not in PedidoService.TRANSICOES_VALIDAS[pedido.estado]:
            self.status.mostrar(
                tr("Não é possível alterar um pedido {current} para {new}.", current=tr(pedido.estado), new=tr(novo_estado)), "error",
            )
            return
        fields = (("data_evento", "Data e hora (AAAA-MM-DD HH:MM). Deixe vazio para agora"),)
        self.dialog = FormDialog(
            self, titulo, fields, {},
            lambda values: self._aplicar_transicao(pedido_id, novo_estado, values),
            submit_text="Confirmar pagamento" if novo_estado == "PAGO" else "Confirmar cancelamento",
            danger=novo_estado == "CANCELADO",
        )

    def _aplicar_transicao(self, pedido_id, novo_estado, values):
        # A data vazia delega ao serviço o uso do momento atual.
        data_evento = interpretar_datetime_evento(values["data_evento"])
        atualizado = PedidoService.atualizar_estado_pedido(
            pedido_id, novo_estado, data_evento=data_evento,
        )
        if not atualizado:
            raise ValueError("Pedido não encontrado.")
        self.carregar()
        acao = tr("pago" if novo_estado == "PAGO" else "cancelado")
        self.status.mostrar(tr("Pedido #{id} marcado como {action}.", id=pedido_id, action=acao), "success")
