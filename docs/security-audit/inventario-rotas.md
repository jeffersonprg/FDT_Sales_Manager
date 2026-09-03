# Inventário completo de rotas e superfícies de entrada

Projeto: FDT Sales Manager  
Data da auditoria: 03/09/2026

## Resultado da enumeração de handlers HTTP

A varredura AST de todos os arquivos `*.py` em `src/` e a busca por Flask,
FastAPI, Django, Starlette, Bottle, Sanic, decorators `route/get/post/put/patch/delete`
e registradores equivalentes encontraram **zero handlers HTTP**.

| Método | Rota | Arquivo:linha | Autenticação | Autorização | Posse/tenant |
|---|---|---|---|---|---|
| N/A | Nenhuma rota HTTP existe | Todos os `*.py` de `src/` | N/A | N/A | N/A |

Consequência para IDOR: não existe cliente remoto, sessão autenticada, parâmetro de
rota nem recurso pertencente a identidades diferentes. Assim, IDOR não se aplica à
arquitetura atual. Tratar cada `WHERE id = ?` como IDOR produziria falso positivo,
pois as chamadas ocorrem dentro do mesmo processo desktop e da mesma base local.

## Mecanismo de isolamento detectado

- Tipo de aplicação: desktop monousuário, sem entidades `user`, `organization`,
  `workspace` ou `tenant` e sem mecanismo de login.
- Fronteira de confiança: usuário/processo do Windows.
- Desenvolvimento: banco em `src/data` (`src/config/paths.py:32-34`).
- Executável: banco em `%LOCALAPPDATA%\FDT Sales Manager`
  (`src/config/paths.py:36-38`).
- Override operacional: `FDT_DATA_DIR` (`src/config/paths.py:27-30`), sujeito às
  permissões do diretório escolhido pelo operador.

## Superfícies equivalentes auditadas

Embora não sejam rotas, todos os métodos públicos de serviço foram inventariados
para provar a cobertura das operações por ID e das escritas. Em todas as linhas,
"N/A - processo local" significa que autenticação/autorização por papel não faz
parte do produto atual, e não que um endpoint remoto esteja sem proteção.

| Interface/método | Arquivo:linha | Entrada/objeto | Autenticação | Autorização | Validação de posse/tenant ou integridade |
|---|---|---|---|---|---|
| `AcessoService.listar_acessos_cliente` | `src/services/acesso_service.py:23` | `cliente_id` | N/A - processo local | N/A - sem papéis | Confirma cliente em 42-49 e filtra pedidos por `cliente_id` em 75-81 |
| `ClienteResumoService.obter_resumo` | `src/services/cliente_resumo_service.py:16` | `cliente_id` | N/A - processo local | N/A - sem papéis | Agregação restrita ao cliente solicitado em 90-100 |
| `ClienteService.criar_cliente` | `src/services/cliente_service.py:51` | `Cliente` | N/A - processo local | N/A - sem papéis | Modelo normaliza/valida; insert parametrizado em 56-81 |
| `ClienteService.listar_clientes` | `src/services/cliente_service.py:103` | filtro de estado | N/A - processo local | N/A - sem papéis | Base única; filtro lógico de ativo em 109-114 |
| `ClienteService.buscar_cliente` | `src/services/cliente_service.py:121` | `cliente_id` | N/A - processo local | N/A - sem papéis | Valida ID positivo e busca parametrizada em 125-136 |
| `ClienteService.atualizar_cliente` | `src/services/cliente_service.py:146` | `Cliente.id` | N/A - processo local | N/A - sem papéis | Exige ID, revalida modelo e atualiza exatamente o ID em 147-183 |
| `ClienteService.remover_cliente` | `src/services/cliente_service.py:203` | `cliente_id` | N/A - processo local | N/A - sem papéis | ID positivo; desativação lógica do ID ativo em 206-220 |
| `ClienteService.reativar_cliente` | `src/services/cliente_service.py:228` | `cliente_id` | N/A - processo local | N/A - sem papéis | ID positivo; reativa exatamente o ID inativo em 229-243 |
| `ClienteService.pesquisar_clientes` | `src/services/cliente_service.py:251` | termo/filtro | N/A - processo local | N/A - sem papéis | SQL parametrizado em 260-288; sem tenant por design monousuário |
| `DashboardService.obter_resumo` | `src/services/dashboard_service.py:6` | limite | N/A - processo local | N/A - sem papéis | Valida limite; agregações da base local única em 13-101 |
| `EstatisticasService.obter_resumo_vendas` | `src/services/estatisticas_service.py:9` | período | N/A - processo local | N/A - sem papéis | Período validado e placeholders em 20-33 |
| `EstatisticasService.vendas_por_produto` | `src/services/estatisticas_service.py:52` | período | N/A - processo local | N/A - sem papéis | Período validado e placeholders em 63-80 |
| `EstatisticasService.faturacao_por_mes` | `src/services/estatisticas_service.py:100` | período | N/A - processo local | N/A - sem papéis | Período validado e placeholders em 111-122 |
| `FaturacaoService.obter_resumo` | `src/services/faturacao_service.py:33` | período | N/A - processo local | N/A - sem papéis | Período validado em 20-30; consulta parametrizada em 44-55 |
| `FaturacaoService.listar_pedidos_faturados` | `src/services/faturacao_service.py:68` | período | N/A - processo local | N/A - sem papéis | Lista apenas pagos e período solicitado em 79-86 |
| `ImportacaoCSVService.listar_historico` | `src/services/importacao_csv_service.py:46` | limite | N/A - processo local | N/A - sem papéis | Limite positivo e placeholder em 47-59 |
| `ImportacaoCSVService.importar` | `src/services/importacao_csv_service.py:216` | caminho CSV/config | N/A - processo local | N/A - sem papéis | Arquivo local explícito; validação de CSV e transação `BEGIN IMMEDIATE` em 221-264 |
| `LeadService.criar_lead` | `src/services/lead_service.py:67` | `Lead` | N/A - processo local | N/A - sem papéis | Revalida modelo/produto e insert parametrizado em 68-105 |
| `LeadService.buscar_lead` | `src/services/lead_service.py:122` | `lead_id` | N/A - processo local | N/A - sem papéis | Busca parametrizada do ID em 126-130 |
| `LeadService.listar_leads` | `src/services/lead_service.py:141` | estado | N/A - processo local | N/A - sem papéis | Enum de estado validado; consulta parametrizada em 147-168 |
| `LeadService.atualizar_lead` | `src/services/lead_service.py:179` | `Lead.id` | N/A - processo local | N/A - sem papéis | Exige ID, revalida modelo/produto e bloqueia convertido em 180-225 |
| `LeadService.atualizar_estado` | `src/services/lead_service.py:239` | ID/estado | N/A - processo local | N/A - sem papéis | Estado permitido; impede conversão direta e convertido imutável em 243-270 |
| `LeadService.converter_em_cliente` | `src/services/lead_service.py:284` | `lead_id`/dados cliente | N/A - processo local | N/A - sem papéis | Confirma lead, unicidade e atualiza o mesmo ID na transação em 299-401 |
| `LeadService.pesquisar_leads` | `src/services/lead_service.py:429` | termo/estado/produto | N/A - processo local | N/A - sem papéis | Valida filtros; todos os valores usam placeholders em 439-515 |
| `PedidoService.criar_pedido` | `src/services/pedido_service.py:160` | `Pedido` | N/A - processo local | N/A - sem papéis | Confirma cliente ativo e produtos ativos em 195-217; grava tudo em transação |
| `PedidoService.buscar_pedido` | `src/services/pedido_service.py:297` | `pedido_id` | N/A - processo local | N/A - sem papéis | ID positivo; pedido em 304-307 e itens restritos ao mesmo pedido em 121-130 |
| `PedidoService.listar_pedidos` | `src/services/pedido_service.py:318` | `cliente_id` opcional | N/A - processo local | N/A - sem papéis | Quando informado, filtra por cliente em 332-337; base única quando omitido |
| `PedidoService.atualizar_estado_pedido` | `src/services/pedido_service.py:350` | ID/estado/data | N/A - processo local | N/A - sem papéis | Confirma pedido, transição e datas; atualiza o mesmo ID em 367-457 |
| `PedidoService.buscar_por_referencia_externa` | `src/services/pedido_service.py:467` | referência | N/A - processo local | N/A - sem papéis | Referência não vazia; busca parametrizada e itens do pedido encontrado em 470-490 |
| `ProdutoService.criar_produto` | `src/services/produto_service.py:29` | `Produto` | N/A - processo local | N/A - sem papéis | Revalida modelo; insert parametrizado em 30-53 |
| `ProdutoService.listar_produtos` | `src/services/produto_service.py:75` | filtro ativo | N/A - processo local | N/A - sem papéis | Base única; filtro lógico em 79-84 |
| `ProdutoService.buscar_produto` | `src/services/produto_service.py:91` | `produto_id` | N/A - processo local | N/A - sem papéis | ID positivo; busca parametrizada em 92-101 |
| `ProdutoService.atualizar_produto` | `src/services/produto_service.py:111` | `Produto.id` | N/A - processo local | N/A - sem papéis | Exige ID, revalida modelo e atualiza o mesmo ID em 112-141 |
| `ProdutoService.desativar_produto` | `src/services/produto_service.py:161` | `produto_id` | N/A - processo local | N/A - sem papéis | Delega à alteração parametrizada por ID em 169-180 |
| `ProdutoService.reativar_produto` | `src/services/produto_service.py:165` | `produto_id` | N/A - processo local | N/A - sem papéis | Delega à alteração parametrizada por ID em 169-180 |
| `ProdutoService.pesquisar_produtos` | `src/services/produto_service.py:191` | termo/filtro | N/A - processo local | N/A - sem papéis | Todos os valores usam placeholders em 195-220 |
| `RelatorioHTMLService.gerar` | `src/services/relatorio_html_service.py:216` | saída/período/título/limites | N/A - processo local | N/A - sem papéis | Extensão e limites validados; HTML autoescapado em 268-298 |

O método `ResumoImportacaoCSV.to_dict` em
`src/services/importacao_csv_service.py:40` também foi enumerado pelo AST, mas é
somente serialização de DTO e não acessa dados.

## Entradas de linha de comando

| Comando | Arquivo:linha | Ação | Observação de segurança |
|---|---|---|---|
| `python -m src.csv_reader` | `src/csv_reader.py:32` | Importa CSV local | Tipos/choices do argparse e validação completa antes da transação |
| `python -m src.report_generator` | `src/report_generator.py:17` | Gera HTML local | Datas tipadas, saída deve terminar em `.html`, autoescape Jinja2 |

## Matriz de gates da interface

Não há `isAdmin`, `role`, `canEdit`, permissões, sessão ou ocultação condicional por
papel. Os botões abaixo são sempre apresentados ao usuário local. Como não existe
endpoint, a coluna correspondente aponta para o método de serviço chamado.

| Componente/gate | Ação | Endpoint/equivalente | Validação equivalente no backend local |
|---|---|---|---|
| `ClientesView`, sem gate (`list_views.py:105`) | Criar cliente | `ClienteService.criar_cliente` | Validação do modelo e constraints (`cliente_service.py:51-100`) |
| `ClientesView`, sem gate (`list_views.py:106`) | Editar cliente | `ClienteService.atualizar_cliente` | ID obrigatório e revalidação (`cliente_service.py:146-200`) |
| `ClientesView`, sem gate (`list_views.py:107`) | Ativar/inativar | `reativar_cliente` / `remover_cliente` | ID/estado exato (`cliente_service.py:203-248`) |
| `ProdutosView`, sem gate (`list_views.py:200`) | Criar produto | `ProdutoService.criar_produto` | Modelo/constraints (`produto_service.py:29-72`) |
| `ProdutosView`, sem gate (`list_views.py:201`) | Editar produto | `ProdutoService.atualizar_produto` | ID/modelo (`produto_service.py:111-158`) |
| `ProdutosView`, sem gate (`list_views.py:202`) | Ativar/inativar | `reativar_produto` / `desativar_produto` | ID e mudança de estado (`produto_service.py:161-188`) |
| `LeadsView`, sem gate (`list_views.py:299`) | Criar lead | `LeadService.criar_lead` | Modelo/produto (`lead_service.py:67-119`) |
| `LeadsView`, sem gate (`list_views.py:300`) | Editar lead | `LeadService.atualizar_lead` | Bloqueia convertido também no serviço (`lead_service.py:179-236`) |
| `LeadsView`, sem gate (`list_views.py:301`) | Converter lead | `LeadService.converter_em_cliente` | Operação transacional e estado validado (`lead_service.py:284-427`) |
| `PedidosView`, sem gate (`list_views.py:429`) | Criar pedido | `PedidoService.criar_pedido` | Cliente/produtos/itens validados (`pedido_service.py:160-294`) |
| `PedidosView`, sem gate (`list_views.py:431`) | Marcar pago | `PedidoService.atualizar_estado_pedido` | Transição e datas validadas (`pedido_service.py:350-464`) |
| `PedidosView`, sem gate (`list_views.py:432`) | Cancelar | `PedidoService.atualizar_estado_pedido` | Transição e datas validadas (`pedido_service.py:350-464`) |
| `CSVImportView`, sem gate (`tools_views.py:53-57`) | Importar vendas | `ImportacaoCSVService.importar` | CSV validado e transação imediata (`importacao_csv_service.py:216-407`) |
| `ReportsView`, sem gate (`tools_views.py:103-107`) | Gerar relatório | `RelatorioHTMLService.gerar` | Extensão/período/limites e autoescape (`relatorio_html_service.py:216-304`) |

Conclusão da matriz: não existe gate definido apenas na interface a ser contornado.
Se o produto ganhar múltiplos usuários ou uma API, autenticação e autorização terão
de ser introduzidas como requisito novo; isso não é uma vulnerabilidade explorável
na aplicação local auditada.
