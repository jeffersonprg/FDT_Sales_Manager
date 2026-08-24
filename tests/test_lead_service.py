import pytest

from src.models.lead import Lead
from src.models.produto import Produto
from src.services.lead_service import LeadService
from src.services.produto_service import ProdutoService
from src.models.cliente import Cliente
from src.services.cliente_service import ClienteService



def criar_produto_interesse(
    nome: str = "Curso para Leads"
) -> int:
    return ProdutoService.criar_produto(
        Produto(
            nome=nome,
            preco=150,
            tipo_validade="VITALICIO"
        )
    )


def test_criar_e_buscar_lead(banco_temporario):
    produto_id = criar_produto_interesse()

    lead = Lead(
        nome="Maria Silva",
        email="maria@email.pt",
        origem="Instagram",
        produto_interesse_id=produto_id
    )

    lead_id = LeadService.criar_lead(lead)

    lead_encontrado = LeadService.buscar_lead(lead_id)

    assert lead_encontrado is not None
    assert lead_encontrado.id == lead_id
    assert lead_encontrado.nome == "Maria Silva"
    assert lead_encontrado.estado == "NOVO"
    assert lead_encontrado.produto_interesse_id == produto_id


def test_buscar_lead_inexistente(banco_temporario):
    lead = LeadService.buscar_lead(9999)

    assert lead is None


def test_listar_leads_e_filtrar_por_estado(
    banco_temporario
):
    LeadService.criar_lead(
        Lead(
            nome="Lead Novo",
            estado="NOVO"
        )
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead Qualificado",
            estado="QUALIFICADO"
        )
    )

    todos = LeadService.listar_leads()

    qualificados = LeadService.listar_leads(
        estado="qualificado"
    )

    assert len(todos) == 2
    assert len(qualificados) == 1
    assert qualificados[0].nome == "Lead Qualificado"
    assert qualificados[0].estado == "QUALIFICADO"


def test_atualizar_lead(banco_temporario):
    lead_id = LeadService.criar_lead(
        Lead(
            nome="Lead Inicial",
            telefone="910000000"
        )
    )

    lead = LeadService.buscar_lead(lead_id)

    assert lead is not None

    lead.nome = "Lead Atualizado"
    lead.telefone = "919999999"
    lead.estado = "CONTACTADO"
    lead.observacoes = "Contacto realizado por telefone."

    atualizado = LeadService.atualizar_lead(lead)

    lead_atualizado = LeadService.buscar_lead(lead_id)

    assert atualizado is True
    assert lead_atualizado is not None
    assert lead_atualizado.nome == "Lead Atualizado"
    assert lead_atualizado.telefone == "919999999"
    assert lead_atualizado.estado == "CONTACTADO"


def test_atualizar_estado_lead(banco_temporario):
    lead_id = LeadService.criar_lead(
        Lead(nome="Lead Estado")
    )

    atualizado = LeadService.atualizar_estado(
        lead_id,
        "qualificado"
    )

    lead = LeadService.buscar_lead(lead_id)

    assert atualizado is True
    assert lead is not None
    assert lead.estado == "QUALIFICADO"


def test_atualizar_estado_invalido(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="O estado deve ser"
    ):
        LeadService.atualizar_estado(
            1,
            "EM_ANALISE"
        )


def test_estado_convertido_exige_operacao_de_conversao(
    banco_temporario
):
    lead_id = LeadService.criar_lead(
        Lead(nome="Lead Conversão")
    )

    with pytest.raises(
        ValueError,
        match="Utilize a operação de conversão"
    ):
        LeadService.atualizar_estado(
            lead_id,
            "CONVERTIDO"
        )


def test_lead_nao_aceita_produto_desativado(
    banco_temporario
):
    produto_id = criar_produto_interesse(
        "Produto desativado para lead"
    )

    ProdutoService.desativar_produto(produto_id)

    lead = Lead(
        nome="Lead Produto Desativado",
        produto_interesse_id=produto_id
    )

    with pytest.raises(
        ValueError,
        match="produto de interesse está desativado"
    ):
        LeadService.criar_lead(lead)

def test_converter_lead_em_cliente(
    banco_temporario
):
    lead_id = LeadService.criar_lead(
        Lead(
            nome="Ana Convertida",
            empresa="Trading Academy",
            telefone="910000000",
            email="ana.convertida@email.pt",
            origem="Instagram",
            estado="QUALIFICADO",
            observacoes="Interessada em formação avançada."
        )
    )

    cliente_id = LeadService.converter_em_cliente(
        lead_id=lead_id,
        morada="Rua Central, Porto",
        pais="Portugal",
        tipo_documento="NIF",
        numero_documento="123456789"
    )

    cliente = ClienteService.buscar_cliente(cliente_id)
    lead = LeadService.buscar_lead(lead_id)

    assert cliente is not None
    assert cliente.id == cliente_id
    assert cliente.nome == "Ana Convertida"
    assert cliente.empresa == "Trading Academy"
    assert cliente.telefone == "910000000"
    assert cliente.email == "ana.convertida@email.pt"
    assert cliente.morada == "Rua Central, Porto"
    assert cliente.tipo_documento == "NIF"
    assert cliente.numero_documento == "123456789"
    assert cliente.observacoes == (
        "Interessada em formação avançada."
    )

    assert lead is not None
    assert lead.estado == "CONVERTIDO"
    assert lead.cliente_id == cliente_id
    assert lead.convertido_em is not None


def test_converter_lead_inexistente(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="Lead não encontrado"
    ):
        LeadService.converter_em_cliente(9999)


def test_nao_converter_lead_duas_vezes(
    banco_temporario
):
    lead_id = LeadService.criar_lead(
        Lead(
            nome="Lead Conversão Única",
            email="conversao.unica@email.pt"
        )
    )

    LeadService.converter_em_cliente(lead_id)

    with pytest.raises(
        ValueError,
        match="já foi convertido"
    ):
        LeadService.converter_em_cliente(lead_id)


def test_conversao_nao_aceita_email_duplicado(
    banco_temporario
):
    ClienteService.criar_cliente(
        Cliente(
            nome="Cliente Existente",
            email="duplicado@email.pt"
        )
    )

    lead_id = LeadService.criar_lead(
        Lead(
            nome="Lead Duplicado",
            email="duplicado@email.pt"
        )
    )

    quantidade_antes = len(
        ClienteService.listar_clientes()
    )

    with pytest.raises(
        ValueError,
        match="Já existe um cliente com este email"
    ):
        LeadService.converter_em_cliente(lead_id)

    quantidade_depois = len(
        ClienteService.listar_clientes()
    )

    lead = LeadService.buscar_lead(lead_id)

    assert quantidade_depois == quantidade_antes

    assert lead is not None
    assert lead.estado == "NOVO"
    assert lead.cliente_id is None
    assert lead.convertido_em is None

def test_pesquisar_leads_por_texto(
    banco_temporario
):
    LeadService.criar_lead(
        Lead(
            nome="Maria Silva",
            empresa="FDT Academy",
            telefone="912345678",
            email="maria@fdt.pt",
            origem="Instagram",
            observacoes="Interessada em análise técnica."
        )
    )

    LeadService.criar_lead(
        Lead(
            nome="João Costa",
            email="joao@email.pt",
            origem="Indicação"
        )
    )

    termos = [
        "Maria",
        "FDT Academy",
        "912345678",
        "maria@fdt.pt",
        "Instagram",
        "análise técnica"
    ]

    for termo in termos:
        leads = LeadService.pesquisar_leads(
            termo=termo
        )

        assert len(leads) == 1
        assert leads[0].nome == "Maria Silva"


def test_filtrar_leads_por_estado(
    banco_temporario
):
    LeadService.criar_lead(
        Lead(
            nome="Lead Novo",
            estado="NOVO"
        )
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead Qualificado",
            estado="QUALIFICADO"
        )
    )

    leads = LeadService.pesquisar_leads(
        estado="qualificado"
    )

    assert len(leads) == 1
    assert leads[0].nome == "Lead Qualificado"
    assert leads[0].estado == "QUALIFICADO"


def test_pesquisar_lead_pelo_nome_do_produto(
    banco_temporario
):
    produto_id = criar_produto_interesse(
        "Mentoria Especial"
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead com Interesse",
            produto_interesse_id=produto_id
        )
    )

    LeadService.criar_lead(
        Lead(nome="Lead sem Interesse")
    )

    leads = LeadService.pesquisar_leads(
        termo="Mentoria Especial"
    )

    assert len(leads) == 1
    assert leads[0].nome == "Lead com Interesse"
    assert leads[0].produto_interesse_id == produto_id


def test_filtrar_leads_por_produto_interesse(
    banco_temporario
):
    produto_1_id = criar_produto_interesse(
        "Produto Lead 1"
    )

    produto_2_id = criar_produto_interesse(
        "Produto Lead 2"
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead Produto 1",
            produto_interesse_id=produto_1_id
        )
    )

    LeadService.criar_lead(
        Lead(
            nome="Lead Produto 2",
            produto_interesse_id=produto_2_id
        )
    )

    leads = LeadService.pesquisar_leads(
        produto_interesse_id=produto_1_id
    )

    assert len(leads) == 1
    assert leads[0].nome == "Lead Produto 1"


def test_pesquisa_vazia_lista_todos_os_leads(
    banco_temporario
):
    LeadService.criar_lead(
        Lead(nome="Primeiro Lead")
    )

    LeadService.criar_lead(
        Lead(nome="Segundo Lead")
    )

    leads = LeadService.pesquisar_leads()

    assert len(leads) == 2


def test_pesquisa_leads_rejeita_estado_invalido(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="O estado deve ser"
    ):
        LeadService.pesquisar_leads(
            estado="EM_ANALISE"
        )


def test_pesquisa_leads_rejeita_produto_invalido(
    banco_temporario
):
    with pytest.raises(
        ValueError,
        match="O ID do produto de interesse deve ser válido"
    ):
        LeadService.pesquisar_leads(
            produto_interesse_id=0
        )