# 17/07/2026

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

# 20/07/2026

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
21/07/2026

Dia 3 

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


