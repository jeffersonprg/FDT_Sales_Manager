# Relatório de Auditoria de Segurança — FDT Sales Manager

**Data:** 03/09/2026  
**Escopo:** código atual do workspace, histórico Git, persistência, interface,
relatório HTML, scripts de build e configuração de empacotamento.  
**Resultado:** **0 vulnerabilidades confirmadas**, **0 configurações perigosas
confirmadas** e **1 melhoria defensiva informativa**.

> A auditoria não transformou a ausência de recursos multiusuário em falhas
> artificiais. O produto é um aplicativo desktop local, sem API, sessões ou
> identidades concorrentes. Cada categoria foi adaptada a essa arquitetura.

## 1. Resumo executivo

| Classificação | Crítica | Alta | Média | Baixa | Informativa |
|---|---:|---:|---:|---:|---:|
| Vulnerabilidade confirmada | 0 | 0 | 0 | 0 | 0 |
| Configuração perigosa confirmada | 0 | 0 | 0 | 0 | 0 |
| Melhoria defensiva | 0 | 0 | 0 | 0 | 1 |

Não foi demonstrado caminho explorável para isolamento de tenant, autorização
apenas no frontend, IDOR, segredo hardcoded ou XSS. A única observação acionável é
defesa em profundidade: adicionar CSP ao HTML estático e ampliar os testes de
regressão XSS para todos os campos persistidos exibidos no relatório.

### Riscos centrais

- Não há risco remoto demonstrado: nenhuma porta, servidor ou rota HTTP existe.
- O modelo de segurança depende do usuário/processo do Windows e das ACLs do
  diretório local. Isso é coerente com o produto atual, mas deve ser reavaliado se
  houver compartilhamento de base, API, sincronização ou múltiplos operadores.
- O bundle PyInstaller final foi produzido e varrido sem segredo confirmado em
  1.907 arquivos (115.981.209 bytes).

## 2. Stack detectada

| Camada | Tecnologia detectada | Evidência |
|---|---|---|
| Linguagem | Python 3.13 documentado; 3.14.2 na validação | `README.md:5-13`; saída do pytest |
| Tipo de aplicação | Desktop monousuário | `app.py:7-12`; `src/views/main_window.py:14-43` |
| Framework/UI | CustomTkinter/Tkinter | `requirements.txt:5`; imports em `src/views/` |
| Persistência | SQLite | `src/database/database.py:1-20` |
| ORM/query builder | Nenhum; módulo `sqlite3` e SQL direto | 107 chamadas `execute` enumeradas por AST |
| Auth | Nenhum login, sessão, token, usuário ou papel | Busca global e modelo de dados |
| Frontend web | Não existe | Zero framework/handler web; GUI desktop |
| HTML | Jinja2, relatório estático autônomo | `relatorio_html_service.py:268-298` |
| Deploy | PyInstaller `onedir` | `FDT_Sales_Manager.spec:10-47` |
| Docker/CI/Helm/Terraform | Não encontrados | Inventário de arquivos de deploy |

### Mapeamento metodológico das cinco categorias

1. **Banco sem tranca:** em vez de procurar RLS, foi identificado o modelo de
   isolamento efetivo. A base é local ao usuário do Windows no executável
   (`src/config/paths.py:32-38`) e não há tenant/usuário de aplicação.
2. **Permissão definida no navegador:** não existe navegador como frontend nem
   papéis. Todas as ações da GUI foram cruzadas com os métodos de serviço; a matriz
   completa está em `inventario-rotas.md`.
3. **IDOR:** a enumeração completa encontrou zero handlers HTTP. Todos os 37
   métodos públicos de negócio foram revisados como superfícies equivalentes.
4. **Chaves expostas:** foram examinados código/config/scripts/docs, todos os
   commits alcançáveis e a configuração PyInstaller. Nenhum segredo foi encontrado.
5. **XSS:** foram procurados sinks HTML/JS, revisados template, SVG e filtros, e
   executado teste dinâmico com payloads em dados persistidos.

## 3. Resultado por categoria

### 3.1 Banco sem tranca - não aplicável como vulnerabilidade

**Mecanismo detectado:** isolamento pelo processo/conta do sistema operacional e
diretório de dados por usuário no build.

Evidência:

```python
# src/config/paths.py:27-38
override = ambiente.get("FDT_DATA_DIR")
if override:
    return Path(override).expanduser()
...
local_app_data = ambiente.get("LOCALAPPDATA")
base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
return base / "FDT Sales Manager"
```

O esquema (`src/database/database.py:295-428`) não contém `user_id`, `tenant_id`,
organização ou workspace. Também não há identidade autenticada à qual uma linha
possa pertencer. As listagens globais são comportamento funcional da base local,
não quebra de isolamento. Se `FDT_DATA_DIR` for configurado para um diretório
compartilhado, as ACLs desse diretório passam a ser a fronteira de acesso; essa
configuração insegura não foi observada no repositório.

### 3.2 Permissão definida no navegador - não aplicável

Não existe frontend web nem modelo de papéis. A busca por `isAdmin`, `role`,
`canEdit`, permissão, sessão e equivalentes retornou zero gates. As ações sensíveis
são botões locais sempre visíveis, como:

```python
# src/views/list_views.py:429-432
self.adicionar_acao("Novo pedido", self.novo, destaque=True)
self.adicionar_acao("Detalhes", self.detalhes)
self.adicionar_acao("Marcar pago", self.pagar)
self.adicionar_acao("Cancelar", self.cancelar)
```

O serviço volta a validar as regras de domínio, por exemplo transições de pedido em
`src/services/pedido_service.py:350-464` e imutabilidade de lead convertido em
`src/services/lead_service.py:179-236`. Não há gate de papel apenas no cliente a ser
contornado. Consulte a matriz completa em `inventario-rotas.md`.

### 3.3 IDOR - não aplicável

A enumeração AST de todos os `*.py` de `src/` encontrou **0 decorators/handlers
HTTP**. Não existe chamador autenticado, path/query/body remoto ou objeto de outro
tenant. O inventário registra todos os métodos por ID e suas validações.

Exemplos corretos:

```python
# src/services/pedido_service.py:297-313
def buscar_pedido(pedido_id: int) -> Pedido | None:
    if pedido_id <= 0:
        raise ValueError(...)
    ...
    row_pedido = connection.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,),
    ).fetchone()
    ...
    itens = PedidoService._listar_itens(connection, pedido_id)
```

```python
# src/services/acesso_service.py:42-81
cliente = connection.execute(... "WHERE id = ?", (cliente_id,)).fetchone()
...
WHERE pedidos.cliente_id = ?
  AND pedidos.estado = 'PAGO'
```

Esses filtros preservam integridade entre entidades; não constituem autorização de
tenant porque não há tenant na aplicação.

### 3.4 Chaves expostas - nenhum achado

Foram pesquisados API keys, tokens, senhas, segredos JWT/webhook, chaves privadas,
credenciais padrão e padrões conhecidos de provedores em:

- arquivos atuais versionados e não versionados relevantes;
- `requirements.txt`, scripts PowerShell, `.spec`, documentação e templates;
- todos os commits retornados por `git rev-list --all`.

Resultado: **0 correspondências de segredo**. Nenhum valor sensível é reproduzido
neste relatório.

O banco local `src/data/fdt_sales_manager.db` está ignorado por `*.db`
(`.gitignore:22-25`) e não aparece em `git ls-files`. Seu conteúdo não foi lido,
pois não era necessário para provar hardcode ou histórico.

O comando de build ultrapassou o timeout de 300 segundos, mas o processo filho
concluiu e criou `dist/FDT Sales Manager`. Foram lidos **1.907 arquivos** e
**115.981.209 bytes** do bundle. Seis correspondências preliminares do padrão
genérico `sk-*` foram verificadas e eram nomes de símbolos compilados de OpenSSL,
MSVC, NumPy e Pandas, não credenciais. Não havia `.env`, `.key`, `.pfx`, `.p12`,
`.db`, `.sqlite` ou PEM com `PRIVATE KEY` no artefato. Resultado final: nenhum
segredo confirmado no bundle.

### 3.5 Inputs sem tratamento (XSS) - sem vulnerabilidade; 1 melhoria informativa

Não foram encontrados `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `eval`,
`new Function`, `Markup`, `mark_safe` ou filtro `safe`.

Proteções verificadas:

```python
# src/services/relatorio_html_service.py:268-271
ambiente = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(("html", "xml")),
)
```

```python
# src/services/relatorio_html_service.py:101-115
nome = escape(str(item["produto_nome"]))
valor = escape(RelatorioHTMLService._formatar_moeda(...))
...
f'<text ...>{nome}</text>'
```

O teste dinâmico gravou em SQLite temporário payloads HTML em cliente, produto,
referência e título. O HTML gerado e o SVG decodificado continham apenas as versões
escapadas. Os 5 testes de `tests/test_relatorio_html_service.py` também passaram.

## 4. Achado detalhado - arquivo por arquivo, linha por linha

### I-001 - Reforçar defesa em profundidade e testes XSS

- **Classificação:** melhoria defensiva/informativa.
- **Severidade:** informativa.
- **Vulnerabilidade atual:** não.
- **Explorabilidade atual:** nenhuma demonstrada; depende de regressão futura.

#### `src/templates/relatorio_comercial.html:3-8`

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ titulo }}</title>
  <link rel="icon" type="image/png" href="{{ favicon_data_uri }}">
  <style>
```

O cabeçalho não declara Content-Security-Policy. Isso não torna o relatório
explorável hoje, pois as interpolações estão escapadas e não há script, mas elimina
uma camada de contenção caso um sink inseguro seja introduzido no futuro.

#### `tests/test_relatorio_html_service.py:92-103`

```python
def test_relatorio_escapa_titulo_html(...):
    RelatorioHTMLService.gerar(
        ...,
        titulo="<script>alert('x')</script>",
    )
    ...
    assert "<script>alert" not in conteudo
    assert "&lt;script&gt;" in conteudo
```

O teste versionado cobre somente o título. Os campos persistidos estão protegidos
no código atual e foram validados dinamicamente durante esta auditoria, mas faltam
testes de regressão permanentes para cliente, produto, referência, nome de arquivo
e conteúdo SVG decodificado.

**Impacto potencial:** uma regressão futura poderia executar HTML/script quando o
operador abrisse um relatório com dado malicioso.  
**Correção sugerida:** CSP restritiva e testes parametrizados de todos os campos.  
**Prioridade:** P3, pois não existe caminho explorável na versão auditada.

## 5. Pontos fortes com evidência

- **SQL parametrizado:** 107 chamadas `execute` auditadas; 105 usam string literal.
  As duas f-strings (`src/database/database.py:28-30` e `53-60`) interpolam somente
  nomes fixos de tabela/coluna passados internamente pelas migrações. Valores de
  usuário usam placeholders.
- **Escape HTML ativado:** `src/services/relatorio_html_service.py:268-271`.
- **Escape manual de SVG:** `src/services/relatorio_html_service.py:101-115` e
  `165-169`.
- **Transações e rollback:** criação de pedido em
  `src/services/pedido_service.py:219-294`, conversão de lead em
  `src/services/lead_service.py:341-427` e importação com `BEGIN IMMEDIATE` em
  `src/services/importacao_csv_service.py:264-407`.
- **Integridade no banco:** foreign keys ativadas em
  `src/database/database.py:15-18`; constraints e FKs em `295-428`.
- **Dados do build por usuário:** `src/config/paths.py:32-38`.
- **Banco local não versionado:** `.gitignore:22-25` e confirmação por
  `git ls-files`.
- **Validação do domínio fora da UI:** modelos em `src/models/` e serviços
  revalidam as operações sensíveis, reduzindo bypass de regra visual.

## 6. Pontos fracos e limitações

- Ausência de CSP e cobertura permanente de XSS para campos persistidos (I-001).
- O modelo de confiança local não deve ser reutilizado sem mudanças se o produto
  evoluir para API, banco compartilhado ou múltiplos usuários.
- A suíte completa coletou 156 testes e avançou até 59% antes do timeout de 120
  segundos. A suíte específica de relatório concluiu com **5/5 aprovados**.

## 7. Recomendações priorizadas

| Prioridade | Recomendação | Origem |
|---|---|---|
| P1 | Nenhuma correção urgente identificada | 0 vulnerabilidades confirmadas |
| P2 | Automatizar varredura de segredos no histórico e no artefato PyInstaller em CI quando CI for adotado | Manter a verificação manual como controle contínuo |
| P2 | Formalizar novo threat model antes de introduzir API, sincronização ou diretório compartilhado | Categorias tenant/auth/IDOR hoje não aplicáveis |
| P3 | Implementar I-001: CSP e testes XSS parametrizados | Melhoria defensiva informativa |

## 8. ISSUES PARA O GITHUB

--- ISSUE 1 ---

### Título

`[Segurança] Reforçar defesa contra regressões XSS no relatório HTML`

### Labels sugeridas

`security`, `informativa`

### Descrição

O relatório HTML está protegido atualmente por `autoescape` do Jinja2 e por escape
manual dos valores inseridos nos SVGs. A auditoria não encontrou XSS explorável.
Como defesa em profundidade, porém, o documento não declara Content-Security-Policy
e o teste versionado de XSS cobre apenas o campo `titulo`. Campos persistidos como
nome de cliente, produto, referência externa e nome de importação também são
renderizados e deveriam possuir testes permanentes contra regressão.

### Por que isso importa

Uma alteração futura que use `safe`, `Markup`, HTML manual ou outro sink inseguro
poderia permitir a execução de conteúdo ativo quando o usuário abrisse um relatório
com dados maliciosos. Uma CSP restritiva limita o impacto, e testes abrangentes
detectam a regressão antes da distribuição.

### Evidência

`src/templates/relatorio_comercial.html:3-8`

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ titulo }}</title>
  <link rel="icon" type="image/png" href="{{ favicon_data_uri }}">
  <style>
```

Não há meta CSP no cabeçalho.

`tests/test_relatorio_html_service.py:92-103`

```python
def test_relatorio_escapa_titulo_html(...):
    ...
    titulo="<script>alert('x')</script>",
    ...
    assert "<script>alert" not in conteudo
    assert "&lt;script&gt;" in conteudo
```

O teste cobre o título, mas não os demais campos persistidos nem o SVG decodificado.

### Impacto

Defesa preventiva contra uma futura regressão de XSS em relatórios locais. Não há
vulnerabilidade explorável confirmada na versão atual.

### Sugestão de correção

1. Adicionar uma CSP compatível com o documento autônomo, por exemplo começando com
   `default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none';
   form-action 'none'`, ajustada após testes nos navegadores suportados.
2. Criar testes parametrizados com payloads em título, cliente, produto, categoria,
   referência externa e nome de arquivo importado.
3. Decodificar os SVGs base64 nos testes e confirmar ausência do payload bruto e
   presença da versão escapada.
4. Manter proibidos `|safe`, `Markup`, `mark_safe`, HTML manual com dados e URLs de
   usuário sem validação de esquema.

### Critérios de aceite

- [ ] O HTML gerado inclui uma CSP documentada e compatível com os recursos locais.
- [ ] Os gráficos e estilos continuam funcionando offline nos navegadores suportados.
- [ ] Testes cobrem título, cliente, produto, categoria, referência e nome de arquivo.
- [ ] Testes decodificam os SVGs e verificam o escape do texto persistido.
- [ ] Nenhum payload bruto aparece no HTML ou no SVG decodificado.
- [ ] A suíte `tests/test_relatorio_html_service.py` permanece verde.

--- FIM ISSUE 1 ---

## 9. Referências internas

- Inventário completo: `docs/security-audit/inventario-rotas.md`
- Dados estruturados: `docs/security-audit/achados.json`
- Comandos e validações: `docs/security-audit/metodologia.md`
- Gerador do PDF: `docs/security-audit/gerar_relatorio_pdf.py`
