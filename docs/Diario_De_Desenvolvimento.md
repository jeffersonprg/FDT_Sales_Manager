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