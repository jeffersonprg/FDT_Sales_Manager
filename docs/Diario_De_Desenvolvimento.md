# 16/07/2026 - 1h

## Objetivo
Iniciar o projeto.

## Atividades realizadas
- Definição dos requisitos.
- Escolha das tecnologias.
- Estrutura inicial da documentação.

## Decisões
- Interface: CustomTkinter.
- Banco de dados: SQLite.
- Organização em módulos.

## Próximo passo
Criar a estrutura de pastas e configurar o ambiente.

____

# 17/07/2026 - 1h30

# Dia 02 – Arquitetura do Projeto 

## Objetivo

Definir a arquitetura e a organização das pastas antes do início da implementação.

## Atividades realizadas

- Definida a estrutura de diretórios do projeto.
- Separação das camadas (Views, Models, Controllers e Services).
- Organização da documentação desde o início do desenvolvimento.

## Decisões técnicas

Foi adotada uma arquitetura modular para facilitar a manutenção, reutilização do código e futura expansão do sistema.

## Conhecimentos adquiridos

- Importância da separação de responsabilidades.
- Organização de projetos Python de médio porte.

## Problemas encontrados

Nenhum.

## Próxima atividade

Configurar o ambiente de desenvolvimento, criar o ambiente virtual, instalar as dependências e iniciar o repositório Git.

____
# 20/07/2026 - 3h

# Dia 3 

# Objetivo

Configurar o controle da versão do projeto
Configurar o ambiente de desenvolvimento e instalar as dependências do projeto.
Definir a modelagem inicial do sistema.
Definir o diagrama entidade-relacionamento (ERD) do sistema antes da implementação da base de dados.


# Atividades realizadas

Inicialização do repositório Git.
Criação do arquivo .gitignore.
Definição dos arquivos e pastas que não serão versionados.
Criação e ativação do ambiente virtual.
Instalação das bibliotecas necessárias.
Geração do requirements.txt.
Criação do README.md.
Identificação das entidades principais.
Definição dos campos de cada entidade.
Modelagem das relações.
Planejamento da estrutura do banco de dados.
Identificação das entidades principais.
Definição dos relacionamentos.
Criação da primeira versão do diagrama ERD em Mermaid.
Revisão da modelagem para suportar múltiplos produtos por pedido.


# Decisões técnicas

Foi criado um .gitignore para evitar o versionamento de arquivos temporários, caches, ambientes virtuais e configurações locais, mantendo o repositório limpo e portátil.
Foi adotada uma modelagem simples e escalável, suficiente para atender aos requisitos do estágio e permitir futuras expansões.
Foi adotado um modelo relacional que separa Pedidos e Itens do Pedido, permitindo que uma única venda contenha vários produtos. Essa abordagem é amplamente utilizada em sistemas comerciais e facilita futuras expansões.

# Conhecimentos adquiridos

Modelagem de entidades e relacionamentos.
Diferença entre um modelo simplificado e um modelo escalável.
Uso de diagramas Mermaid para documentação técnica.

# Problemas

Nenhum

# Próxima atividade

Modelar a arquitetura da aplicação e criar a primeira versão do banco de dados SQLite.
Criar o banco de dados SQLite e implementar as primeiras tabelas.


____
# 21/07/2026 - 2h

# Dia 4 

# Objetivo

Modelar a base de dados SQLite a partir do diagrama ERD.

# Atividades realizadas

Definição das tabelas.
Definição dos tipos de dados do SQLite.
Criação das chaves primárias.
Definição das chaves estrangeiras.
Inclusão da tabela itens_pedido para suportar múltiplos produtos por pedido.


# Decisões técnicas

Foi escolhido SQLite com SQL puro (sqlite3), por ser leve, nativo do Python e adequado ao escopo do projeto. A modelagem foi ajustada para permitir que um pedido contenha vários produtos, seguindo uma prática comum em sistemas comerciais.

# Conhecimentos adquiridos

Diferença entre modelo conceitual e modelo físico.
Tipos de dados do SQLite.
Uso de chaves primárias e estrangeiras.
Normalização básica para evitar duplicação de dados.

______

# 22/07/2026 - 3h

# Dia 5 

## Atividade — Revisão da validade dos produtos

### Objetivo

Adaptar a modelagem do sistema para representar diferentes períodos de acesso aos produtos comercializados pela FDT.

### Análise realizada

Durante a revisão do domínio do negócio, foi identificado que os produtos podem possuir diferentes regras de validade. Alguns cursos e mentorias possuem acesso limitado a um determinado período, enquanto outros podem ser adquiridos com acesso vitalício.

### Alterações realizadas

- Adicionado o campo `tipo_validade` à entidade Produto.
- Adicionado o campo `duracao_dias` à entidade Produto.
- Adicionados os campos `inicio_acesso` e `fim_acesso` à entidade ItemPedido.
- Atualizado o modelo físico da base de dados.
- Atualizado o diagrama ERD.

### Decisões técnicas

A validade padrão é definida no Produto. No momento da compra, o período efetivo de acesso é registrado no ItemPedido.

Essa separação permite preservar o histórico da aquisição mesmo que a configuração padrão do produto seja alterada posteriormente.

Produtos temporários possuem uma duração definida em dias.

Produtos vitalícios não possuem data de expiração, sendo representados por `NULL` no campo `fim_acesso`.

### Exemplo

Um curso com validade de 365 dias adquirido em 01/08/2026 terá:

- inicio_acesso: 01/08/2026
- fim_acesso: 01/08/2027

Um produto vitalício terá:

- inicio_acesso: data da aquisição
- fim_acesso: NULL

### Conhecimentos adquiridos

- Modelagem de regras de negócio em bases de dados.
- Diferença entre validade padrão do produto e validade efetiva da aquisição.
- Preservação de histórico de acesso.

### Problemas encontrados

A modelagem inicial não representava produtos com validade temporária ou vitalícia.

### Solução

A validade foi adicionada ao Produto e o período efetivo de acesso foi armazenado no ItemPedido.

### Próxima atividade

Revisar o modelo completo da base de dados e implementar as tabelas SQLite.

____

# 23/07/2026 - 2h

# Dia 6 

## Atividade — Inspeção e conversão dos dados e validação da estrutura do ficheiro CSV

### Objetivo

Recalculando roto, pois havia focado no MiniCRM que é "secundario" e deixado de lado o principal que é a leitura do CSV e geração do html. 

Inspecionar os dados carregados a partir do ficheiro CSV e garantir que as colunas possuem tipos de dados adequados para a análise.

Garantir que o ficheiro CSV contém todas as colunas obrigatórias antes de iniciar a análise dos dados.

### Atividades realizadas

- Leitura do ficheiro CSV utilizando a biblioteca Pandas.
- Visualização das primeiras linhas do DataFrame.
- Verificação da quantidade de linhas e colunas.
- Identificação dos nomes das colunas.
- Verificação dos tipos de dados.
- Conversão da coluna `data` de texto para o tipo `datetime`.
- Definida uma lista de colunas obrigatórias.
- Implementada a verificação da existência dessas colunas no DataFrame.
- Implementada uma mensagem de erro para indicar colunas em falta.
- Testado o ficheiro CSV de exemplo.


### Decisão técnica

A coluna `data` foi convertida utilizando `pd.to_datetime()`.

Antes da conversão:

```text```
data → object

### Conhecimentos adquiridos

- Estrutura de um DataFrame do Pandas.
- Diferença entre dados do tipo object, int64, float64 e datetime64.
- Importância da conversão correta dos tipos de dados antes da análise.
- Validação da estrutura de um DataFrame.
- Verificação da existência de colunas.
- Utilização de listas e estruturas de repetição para validar dados.
- Importância da validação antes da análise.


### Problemas encontrados

A coluna data foi inicialmente interpretada como texto pelo Pandas.

## Solução

A coluna foi convertida explicitamente para o tipo datetime utilizando pd.to_datetime().

### Próxima atividade

- Validar os valores presentes nas colunas e identificar dados vazios ou inválidos.

____

# 24/07/2026 - 2h

# Dia 7

## Atividade — Verificação de valores ausentes, Validação de valores numéricos e Validação da consistência da faturação

### Objetivo

Identificar campos vazios ou valores ausentes no ficheiro CSV antes da realização da análise.
Verificar se os valores numéricos relacionados às vendas são válidos.
Verificar se o valor de faturação de cada venda corresponde à quantidade de produtos multiplicada pelo preço unitário.


### Atividades realizadas

- Utilizada a função `isnull()` do Pandas.
- Contabilizados os valores ausentes em cada coluna.
- Testado o ficheiro CSV de exemplo.
- Verificadas quantidades negativas.
- Verificados preços unitários negativos.
- Verificados valores de faturação negativos.
- Testado o ficheiro CSV de exemplo.
- Calculado o valor esperado da faturação.
- Comparado o valor calculado com o valor presente no CSV.
- Criada uma coluna de controlo indicando se cada venda é consistente.
- Testado o ficheiro CSV de exemplo.


### Resultado

O ficheiro CSV de exemplo não possui valores ausentes.

Todas as colunas apresentaram:

```text```
0 valores ausentes

## Conhecimentos adquiridos

- Identificação de valores ausentes em DataFrames.
- Utilização de isnull() e sum() para contabilizar dados em falta.
- Importância da qualidade dos dados antes da análise.

____

# 25/07/2026 - 2h

# Dia 8

## Atividade — Separação do módulo de validação e Criação da conexão com a base de dados SQLite

### Objetivo

Separar a leitura dos dados da lógica de validação, melhorando a organização e a manutenção do código.
Criar a conexão inicial com a base de dados SQLite que será utilizada pelo MiniCRM.

### Atividades realizadas

- Criado o ficheiro `validator.py`.
- Criada a função `validar_colunas()`.
- Criada a função `validar_valores_ausentes()`.
- Criada a função `validar_valores_negativos()`.
- Criada a função `validar_faturacao()`.
- Alterado o `csv_reader.py` para utilizar as funções do módulo de validação.
- Testado o funcionamento conjunto dos módulos.
- Criado o módulo `src/database/database.py`.
- Utilizada a biblioteca `sqlite3`, incluída nativamente no Python.
- Criada uma função responsável por estabelecer a conexão com a base de dados.
- Configurado o SQLite para utilizar `Row` como factory de resultados.
- Ativada a verificação de chaves estrangeiras através de `PRAGMA foreign_keys = ON`.
- Criado o ficheiro local da base de dados `fdt_sales_manager.db`.
- Testada a conexão com sucesso.


### Estrutura atual

```text```
src/
├── csv_reader.py
├── validator.py
└── data/
│   └── imports/
│       └── vendas_exemplo.csv
│   └── fdt_sales_manager.db
├── database/
│   └── database.py

### Resultado

O sistema conseguiu ler e validar corretamente os dados do ficheiro CSV.
A conexão com a base de dados SQLite foi estabelecida com sucesso.

### Decisão técnica

A lógica de validação foi separada da lógica de leitura do ficheiro CSV.

Essa separação permite reutilizar o módulo de validação futuramente durante a importação de dados para o MiniCRM.

### Conhcimentos adquiridos
- Organização de código em módulos.
- Criação e utilização de funções.
- Importação de funções entre ficheiros Python.
- Separação de responsabilidades.

### Problema encontrado

Inicialmente, o teste não apresentou qualquer resultado porque as alterações no ficheiro Python não tinham sido guardadas antes da execução.

## Solução

O ficheiro foi guardado e o teste foi executado novamente com sucesso.

### Próxima atividade

Criar a tabela clientes na base de dados SQLite.

_____

# 27/07/2026

# Dia 9

## Atividade — Criação da conexão com a base de dados SQLite e Criação da tabela de clientes

### Objetivo

Criar a conexão inicial com a base de dados SQLite que será utilizada pelo MiniCRM.
Criar a primeira tabela do MiniCRM para armazenar os dados dos clientes.

### Atividades realizadas

- Criado o módulo `src/database/database.py`.
- Utilizada a biblioteca `sqlite3`, incluída nativamente no Python.
- Criada uma função responsável por estabelecer a conexão com a base de dados.
- Configurado o SQLite para utilizar `Row` como factory de resultados.
- Ativada a verificação de chaves estrangeiras através de `PRAGMA foreign_keys = ON`.
- Criado o ficheiro local da base de dados `fdt_sales_manager.db`.
- Testada a conexão com sucesso.
- Criada a função `create_tables()`.
- Criada a tabela `clientes` utilizando SQL.
- Utilizado `CREATE TABLE IF NOT EXISTS` para evitar erros caso a tabela já exista.
- Utilizado `PRIMARY KEY AUTOINCREMENT` para gerar identificadores automaticamente.
- Definido o campo `nome` como obrigatório através de `NOT NULL`.
- Utilizado `CURRENT_TIMESTAMP` para registar automaticamente a data de criação.
- Executado o teste de criação da tabela com sucesso.

### Estrutura atual

```text```
src/
├── database/
│   └── database.py
└── data/
    └── fdt_sales_manager.db


###   Resultado

A conexão com a base de dados SQLite foi estabelecida com sucesso.

## Problema encontrado

Inicialmente, o teste não apresentou qualquer resultado porque as alterações no ficheiro Python não tinham sido guardadas antes da execução.

## Solução

O ficheiro foi guardado e o teste foi executado novamente com sucesso.

###   Conhecimentos adquiridos
- Utilização do módulo sqlite3.
- Criação de uma conexão com uma base de dados SQLite.
- Utilização da biblioteca pathlib para construir caminhos de ficheiros.
- Importância de guardar as alterações antes de executar o código.

____

# 28/07/2026

# Dia 10

### Atividades realizadas:

- Criada a classe Cliente utilizando @dataclass.
- Adicionados type hints (Optional e datetime) para melhorar a legibilidade e a segurança do código.
- Definido o modelo de domínio da entidade Cliente.
- Realizado teste de instanciação do objeto Cliente, confirmando o funcionamento da dataclass.
- Iniciada a arquitetura em camadas (Model → Service → Base de Dados), preparando a implementação do CRUD de clientes.


___

# 29/07/2026

# Dia 11

### Atividades realizadas
- Implementado o ClienteService.
- Desenvolvido o método criar_cliente().
- Integrado o Model Cliente com a base de dados SQLite.
- Realizado o primeiro INSERT utilizando a arquitetura em camadas.
- Confirmada a persistência dos dados através de testes na base de dados.
- Corrigidos problemas de indentação e validado o fluxo completo de gravação.
- Implementado o método listar_clientes().
- Desenvolvida a conversão de registros SQLite (sqlite3.Row) para objetos Cliente.
- Validado o primeiro método de leitura da base de dados.
- Confirmado o funcionamento do CRUD (operações Create e Read).
- Identificada e corrigida uma falha causada por arquivo não salvo durante os testes.
- Iniciada a refatoração do ClienteService para eliminar duplicação de código (princípio DRY).

______

# 30/07/2026

# Dia 12

### Atividades realizadas

- Implementado o método buscar_cliente().
- Utilizado fetchone() para recuperação de um único registo.
- Tratamento de clientes inexistentes através do retorno None.
- Reutilizado o método _row_para_cliente(), eliminando duplicação de código.
- Validado o funcionamento da pesquisa por ID.
- Implementado o método atualizar_cliente().
- Desenvolvida a operação UPDATE na base de dados SQLite.
- Atualização automática do campo atualizado_em.
- Validado o ciclo completo de edição de clientes.
- Concluídas as operações de criação, leitura e atualização do CRUD.

____

# 31/07/2026

## Dia 13 — Início dos testes automatizados

### Objetivo

Substituir os scripts manuais por testes automatizados, isolados e repetíveis.

### Atividades realizadas

- Instalado e configurado o pytest.
- Criada a pasta `tests`.
- Removidos os antigos scripts manuais de teste da pasta `src`.
- Implementado o teste do modelo `Cliente`.
- Implementados testes das operações de criação, pesquisa, listagem,
  atualização e remoção de clientes.
- Criada uma base de dados SQLite exclusiva para cada teste.
- Utilizado `monkeypatch` para redirecionar temporariamente o caminho da base de
  dados.
- Configurada a pasta temporária utilizada pelos testes.

### Resultado

```text
6 passed
```

____

# 03/08/2026

## Dia 14 — Modelo de produtos

### Objetivo

Implementar a representação dos produtos comercializados no MiniCRM.

### Atividades realizadas

- Criada a tabela `produtos` na base de dados.
- Criado o model `Produto` com `dataclass`.
- Implementadas validações para nome e preço.
- Implementadas as regras de validade temporária e vitalícia.
- Normalizado o campo `tipo_validade`.
- Criados testes para produtos válidos e inválidos.

____

# 04/08/2026

## Dia 15 — Serviço de produtos

### Objetivo

Disponibilizar as operações de gestão de produtos.

### Atividades realizadas

- Implementado o `ProdutoService`.
- Adicionadas as operações de criação, pesquisa, listagem e atualização.
- Implementada a desativação lógica de produtos.
- Definida a regra que impede a utilização de produtos desativados em novas
  operações, preservando o histórico.
- Ampliados os testes automatizados do módulo de produtos.

____

# 05/08/2026

## Dia 16 — Modelos de pedidos e itens

### Objetivo

Representar vendas com um ou mais produtos.

### Atividades realizadas

- Criadas as tabelas `pedidos` e `itens_pedido`.
- Implementados os models `Pedido` e `ItemPedido`.
- Implementada a validação de que um pedido deve possuir pelo menos um item.
- Implementado o cálculo automático do subtotal de cada item.
- Implementado o cálculo do total do pedido.
- Criados testes das regras dos models de pedidos.

____

# 06/08/2026

## Dia 17 — Serviço de pedidos

### Objetivo

Implementar o fluxo de persistência e consulta dos pedidos.

### Atividades realizadas

- Implementado o `PedidoService`.
- Adicionada a gravação transacional de pedidos e respetivos itens.
- Implementadas a pesquisa e a listagem de pedidos.
- Implementada a atualização do estado dos pedidos.
- Adicionado rollback completo quando ocorre um erro durante a transação.
- Criados testes para persistência, consulta e falhas transacionais.

____

# 07/08/2026

## Dia 18 — Gestão de leads

### Objetivo

Criar a estrutura inicial para acompanhamento de potenciais clientes.

### Atividades realizadas

- Criada a tabela `leads`.
- Implementado o model `Lead`.
- Implementado o `LeadService`.
- Adicionadas as operações de criação, pesquisa e atualização.
- Implementada a alteração do estado dos leads.
- Criados testes automatizados para o model e o serviço.

____

# 10/08/2026

## Dia 19 — Conversão de leads

### Objetivo

Permitir a conversão segura de um lead em cliente.

### Atividades realizadas

- Implementada a conversão de lead em cliente.
- Associado o lead convertido ao cliente criado.
- Agrupada a conversão numa única transação.
- Implementado rollback para impedir registos parciais em caso de erro.
- Criados testes para conversões válidas, repetidas e interrompidas.

____

# 11/08/2026

## Dia 20 — Períodos de acesso

### Objetivo

Calcular e consultar o acesso concedido pelos produtos adquiridos.

### Atividades realizadas

- Implementado o cálculo automático do período de acesso.
- Definidas datas de início e fim para produtos temporários.
- Representado o acesso vitalício sem data de fim.
- Implementado o `AcessoService`.
- Adicionadas consultas de acessos ativos, expirados e vitalícios.
- Criados testes para as diferentes regras de validade.

____

# 12/08/2026

## Dia 21 — Indicadores do dashboard

### Objetivo

Disponibilizar os primeiros indicadores comerciais do MiniCRM.

### Atividades realizadas

- Implementado o `DashboardService`.
- Adicionados totais de clientes, produtos, leads e pedidos.
- Implementado o cálculo de faturação com base nos pedidos pagos.
- Garantido que pedidos não pagos não entram na faturação.
- Criados testes dos indicadores e dos filtros utilizados no dashboard.

____

# 13/08/2026

## Dia 22 — Consultas e resumo comercial

### Objetivo

Facilitar a localização de registos e a consulta do histórico de clientes.

### Atividades realizadas

- Implementado o resumo comercial individual de clientes.
- Adicionadas pesquisas de clientes, produtos e leads.
- Integradas informações de pedidos e acessos no resumo do cliente.
- Padronizada a conversão dos registos SQLite para objetos de domínio.
- Adicionados testes das pesquisas e dos resumos comerciais.

____

# 14/08/2026

## Dia 23 — Integração do núcleo do MiniCRM

### Objetivo

Validar o funcionamento conjunto dos models, serviços e regras de negócio.

### Atividades realizadas

- Criado um teste integrado do fluxo completo do MiniCRM.
- Testados models, services e restrições da base de dados.
- Testadas as transações, pesquisas, regras de acesso e indicadores.
- Corrigidas inconsistências encontradas durante os testes integrados.
- Confirmada a estabilidade da primeira versão funcional do backend.

### Resultado

```text
101 passed
```

____

# 17/08/2026

## Dia 24 — Reforço das validações

### Objetivo

Impedir a persistência de dados inválidos no backend.

### Atividades realizadas

- Adicionadas validações completas para clientes e produtos.
- Reforçadas as validações de pedidos e itens de pedido.
- Configurada a revalidação dos dados nos models e nos serviços antes da
  persistência.
- Adicionados testes para campos obrigatórios, valores inválidos e limites das
  regras de negócio.

____

# 18/08/2026

## Dia 25 — Unicidade e desativação lógica

### Objetivo

Evitar duplicações e preservar o histórico dos registos.

### Atividades realizadas

- Implementada a unicidade case-insensitive de emails e documentos de clientes.
- Implementada a unicidade case-insensitive de nomes de produtos.
- Substituída a exclusão física de clientes por desativação lógica.
- Adicionadas operações de reativação de clientes e produtos.
- Ajustados os serviços para utilizar rollback e fechamento garantido das
  ligações à base de dados.
- Criados testes de duplicação, desativação e reativação.

____

# 19/08/2026

## Dia 26 — Ciclo de pagamento e cancelamento

### Objetivo

Controlar de forma consistente as mudanças de estado dos pedidos.

### Atividades realizadas

- Implementados os campos `pago_em` e `cancelado_em`.
- Definidas as transições permitidas entre os estados dos pedidos.
- Impedidas transições inválidas ou incompatíveis com o estado atual.
- Implementada a unicidade case-insensitive das referências externas.
- Criados testes para pagamento, cancelamento e referências duplicadas.

____

# 20/08/2026

## Dia 27 — Ajustes das regras de acesso

### Objetivo

Alinhar o período de acesso com a data efetiva do pagamento.

### Atividades realizadas

- Transferido o início do acesso da data do pedido para a data do pagamento.
- Garantido que apenas pedidos pagos concedem acesso aos produtos.
- Ajustada a validade temporária para representar exatamente o número de dias
  contratado.
- Mantida a ausência de data final para produtos vitalícios.
- Atualizados os testes do ciclo de pagamento e dos períodos de acesso.

____

# 21/08/2026

## Dia 28 — Faturação, estatísticas e dashboard

### Objetivo

Expandir os indicadores comerciais disponíveis no sistema.

### Atividades realizadas

- Criado o serviço de faturação com filtros por período.
- Criado o serviço de estatísticas e vendas por produto.
- Adicionado o produto mais vendido ao dashboard.
- Adicionada a listagem dos últimos pedidos.
- Ajustado o total do dashboard para considerar apenas clientes ativos.
- Criados testes de faturação, estatísticas e indicadores.

____

# 24/08/2026

## Dia 29 — Migrações e estabilização do backend

### Objetivo

Concluir e endurecer o backend antes da integração do CSV e dos relatórios HTML.

### Atividades realizadas

- Criado o controlo incremental de migrações do SQLite através da tabela
  `schema_migrations`.
- Preparados os índices únicos case-insensitive exigidos pelas novas regras.
- Validada a migração sobre uma cópia da base existente antes da aplicação.
- Criado um backup da base anterior à migração.
- Executada a suíte completa de testes automatizados.
- Validada a integridade da base atualizada.
- Atualizada a documentação técnica do backend.

### Resultado

```text
129 passed
```

O banco atualizado foi validado com `integrity_check=ok` e sem violações de
chaves estrangeiras.

### Próxima atividade

Integrar a importação CSV aos serviços do MiniCRM, com prevenção de duplicações,
transações e resumo da importação.

# 24/08/2026 - Integração CSV

## Objetivo

Integrar o arquivo CSV ao núcleo estabilizado do MiniCRM.

## Atividades realizadas

- Transformado o leitor experimental em módulo reutilizável e comando CLI.
- Criado serviço transacional de importação.
- Implementada validação de esquema, valores, datas, quantidades e faturação.
- Implementado agrupamento de múltiplas linhas pela referência do pedido.
- Implementada agregação do mesmo produto repetido no pedido.
- Implementada criação e reutilização de clientes por nome e morada.
- Implementada criação e reutilização de produtos por nome.
- Pedidos importados passam a ser pagos na data informada no CSV.
- Períodos de acesso são calculados conforme a validade do produto.
- Criado histórico de importações com hash SHA-256.
- Referências já existentes são ignoradas e reportadas no resumo.
- Qualquer erro provoca rollback de toda a importação.

## Validação

O arquivo de exemplo produziu, em banco isolado:

- 4 clientes criados;
- 2 produtos criados;
- 5 pedidos pagos;
- 5 itens;
- faturação importada de 2.696,00 euros.

Resultado da suíte completa:

```text
137 passed
```

## Próxima atividade

Criar o relatório HTML utilizando dados reais do MiniCRM e os resumos de
faturação, estatísticas e importações.

# 24/08/2026 - Relatório HTML integrado

## Objetivo

Consolidar os dados do MiniCRM e das importações CSV em um relatório comercial
autônomo, legível no navegador e adequado para impressão.

## Atividades realizadas

- Criado serviço de geração de relatório com filtros opcionais por período.
- Integrados dashboard, faturação, estatísticas por produto, pedidos pagos e
  histórico de importações.
- Criada a série de faturação mensal.
- Criado template HTML responsivo com indicadores, tabelas e estados vazios.
- Criados gráficos SVG incorporados no próprio arquivo, sem dependências
  externas para visualização.
- Adicionados escape de conteúdo, formatação monetária e gravação atômica.
- Criado comando `python -m src.report_generator`.
- Gerados um relatório da base atual e um relatório demonstrativo usando banco
  temporário, sem alterar os dados reais.
- Adicionados testes de conteúdo, período, base vazia, segurança de HTML e
  argumentos inválidos.

## Validação

O relatório demonstrativo apresentou:

- 4 clientes;
- 2 produtos;
- 5 pedidos pagos;
- faturação total de 2.696,00 euros;
- gráficos, tabelas e histórico de importação no mesmo HTML.

Resultado da suíte completa:

```text
143 passed
```

O navegador interno não abriu o arquivo local devido à política de segurança
para URLs `file://`. A validação automatizada confirmou a estrutura, o conteúdo,
os gráficos incorporados e o comportamento responsivo definido no template.

## Próxima atividade

Construir a interface gráfica e conectar nela os módulos concluídos do
MiniCRM, da importação CSV e dos relatórios HTML.

# 25/08/2026 - Fundação da interface gráfica

## Objetivo

Criar a estrutura visual da aplicação e tornar acessíveis, numa única janela,
os dados e ferramentas já concluídos no backend.

## Atividades realizadas

- Implementada a janela principal em CustomTkinter.
- Criada navegação lateral para Dashboard, Clientes, Produtos, Leads, Pedidos,
  Importar CSV e Relatórios.
- Criado dashboard com seis indicadores, taxa de conversão, produto em destaque
  e últimos pedidos.
- Criadas tabelas pesquisáveis para os quatro módulos comerciais.
- Criada interface de seleção e importação de CSV com resumo e erros visíveis.
- Criada interface de geração de relatório com caminho de saída e período.
- Criados componentes compartilhados de cabeçalho, cartão, tabela e estado.
- Separada a transformação dos dados numa camada de apresentação testável.
- Adicionado carregamento sob demanda de Pandas e Jinja2.

## Validação

- A janela foi construída pelo Tk com todos os sete módulos.
- Todas as telas foram alternadas e renderizadas com escala do Windows ativa.
- O runtime de inspeção visual não expôs a janela Tk para captura automatizada;
  a validação do ciclo real da janela confirmou geometria, visibilidade e
  construção dos componentes.
- O banco real não recebeu dados durante a validação da interface.

Resultado da suíte completa:

```text
148 passed
```

## Próxima atividade

Adicionar formulários de criação e edição para clientes, produtos, leads e
pedidos, seguidos das ações de conversão, pagamento e cancelamento.

# 25/08/2026 - CRUD visual de clientes e produtos

## Objetivo

Transformar as telas de consulta de clientes e produtos em módulos operacionais
sem duplicar as regras comerciais do backend.

## Atividades realizadas

- Criado modal reutilizável e rolável para formulários.
- Adicionados campos completos de cliente, incluindo contactos, morada,
  documento e observações.
- Implementadas criação e edição de clientes.
- Implementadas inativação e reativação de clientes com histórico preservado.
- Adicionados campos de produto, preço, categoria, validade, duração e descrição.
- Implementadas criação e edição de produtos vitalícios e temporários.
- Implementadas inativação e reativação de produtos com histórico preservado.
- Adicionada edição por duplo clique e controlo de seleção na tabela.
- Criados conversores de formulário para moeda, inteiros e textos opcionais.
- Erros de validação do domínio são apresentados dentro do próprio modal.

## Validação

O fluxo visual foi exercitado num banco temporário:

- cliente criado, editado e inativado;
- produto temporário criado, editado e inativado;
- preço em formato português convertido corretamente;
- modais de cliente e produto construídos e visíveis;
- nenhuma alteração realizada no banco real.

Resultado da suíte completa:

```text
150 passed
```

## Próxima atividade

Adicionar CRUD visual de leads, incluindo conversão em cliente, e depois criar
o fluxo visual de pedidos, pagamento e cancelamento.

# 26/08/2026 - CRUD visual e conversão de leads

## Objetivo

Tornar o módulo de leads operacional na interface e ligar a conversão ao fluxo
transacional já estabilizado no backend.

## Atividades realizadas

- Adicionado formulário de criação de leads.
- Adicionado formulário de edição com estados do funil.
- Produtos ativos passam a ser selecionados pelo nome no formulário.
- Adicionada coluna de produto de interesse na tabela.
- Adicionada edição por botão e duplo clique.
- Criado formulário específico para conversão em cliente.
- Integrados morada, país, documento e observações na conversão.
- Leads convertidos são protegidos contra edição e nova conversão.
- Erros de email ou documento duplicado continuam a provocar rollback completo.
- Adicionados conversores testáveis entre opções visuais e IDs internos.

## Validação

O fluxo foi exercitado num banco temporário:

- produto de interesse criado;
- lead criado e associado ao produto;
- estado alterado de NOVO para QUALIFICADO;
- modal de conversão construído e visível;
- lead convertido num cliente com contactos e morada preservados;
- nenhuma alteração realizada no banco real.

Resultado da suíte completa:

```text
151 passed
```

## Próxima atividade

Criar o fluxo visual de pedidos com seleção de cliente e produtos, composição
dos itens, pagamento e cancelamento.
