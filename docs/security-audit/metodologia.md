# Metodologia e comandos de validação

Data: 03/09/2026  
Diretório de trabalho: `D:\FDT_Sales_Manager`

## Princípios

- Revisão somente local; nenhuma requisição foi enviada a produção, banco real ou
  serviço externo.
- `node_modules`, `venv`, `.venv`, `vendor`, `dist`, `build`, caches e artefatos
  gerados foram excluídos da primeira passagem.
- Achados exigiram evidência no código atual e caminho de exploração demonstrável.
- Ausência de tenant/auth em um aplicativo desktop monousuário foi tratada como
  não aplicável, não como vulnerabilidade.
- Segredos, caso encontrados, seriam mascarados; nenhum foi encontrado.

## 1. Inventário e detecção de stack

```powershell
Get-ChildItem -Force
rg --files -g '!node_modules/**' -g '!venv/**' -g '!.venv/**' `
  -g '!vendor/**' -g '!dist/**' -g '!build/**' -g '!coverage/**' -g '!.git/**'
git status --short
git rev-parse --show-toplevel
git log -1 --format='%H %ad %s' --date=iso-strict
```

```powershell
rg -n -i '(flask|fastapi|django|starlette|quart|bottle|sanic|@app\.|@router\.|add_route|route\()' `
  . -g '*.py' -g '!venv/**' -g '!.venv/**'
```

Resultado: zero framework ou rota HTTP; stack confirmada por `requirements.txt`,
imports, `README.md` e `docs/02_Decisoes_Tecnicas.md`.

## 2. Autenticação, tenant e gates da interface

```powershell
rg -n -i '(auth|login|logout|session|current_user|user_id|tenant|workspace|organization|role|admin|permission|can_edit|is_admin|jwt|oauth|password|senha)' `
  src tests README.md docs scripts -g '!**/*.db' -g '!**/*.png' -g '!**/*.ico'
```

```powershell
rg -n -i '(admin|role|papel|permiss|privil|is_[a-z]+|can_[a-z]+|state\s*=\s*["'']disabled)' `
  src/views src -g '*.py'
```

Resultado: zero mecanismo de autenticação/papel e zero gate por papel. Todas as
ações em `src/views/list_views.py`, `src/views/tools_views.py` e
`src/views/order_dialog.py` foram cruzadas manualmente com o serviço chamado.

## 3. Inventário sistemático de handlers e SQL

Foi executado um script AST somente leitura sobre todos os `src/**/*.py` para:

- contar decorators compatíveis com rotas HTTP;
- listar todos os métodos públicos em `src/services/`;
- classificar o primeiro argumento de cada `execute`, `executemany` e
  `executescript` como literal, f-string ou outro.

Comando-base:

```powershell
@'
import ast
from pathlib import Path

for path in sorted(Path('src').rglob('*.py')):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        # enumeração de decorators, métodos públicos e chamadas SQL
        ...
'@ | .\.venv\Scripts\python.exe -
```

Resultados registrados:

- handlers HTTP: **0**;
- métodos públicos em `src/services/`: **38**, dos quais 37 são superfícies de
  negócio/dados e 1 é serialização de DTO;
- chamadas SQL `execute`: **107**;
- SQL literal: **105**;
- SQL em f-string: **2**, ambas em `src/database/database.py:28` e `:53`, usadas
  apenas com nomes fixos de tabela/coluna das migrações;
- outras formas dinâmicas: **0**.

Busca textual complementar:

```powershell
rg -n 'execute\(|executemany\(|executescript\(|SELECT |INSERT |UPDATE |DELETE |PRAGMA |CREATE TABLE' `
  src -g '*.py'
```

## 4. Sinks XSS e teste dinâmico

```powershell
rg -n -i '(innerHTML|outerHTML|dangerouslySetInnerHTML|v-html|\[innerHTML\]|eval\(|new Function|Markup\(|mark_safe|\|safe|autoescape|Environment\(|render_template|href=|src=|javascript:)' `
  src tests README.md docs scripts -g '!src/data/reports/**'
```

Resultado: apenas o template Jinja2, data URIs internas e a configuração de
`autoescape`; nenhum sink de execução dinâmica.

O teste dinâmico criou uma base SQLite em `tempfile.TemporaryDirectory`, persistiu
payloads HTML em cliente, produto e referência de pedido, gerou um relatório com
título malicioso e verificou com `markupsafe.escape`:

```text
html_raw_cliente_absent=True
html_escaped_cliente_present=True
html_raw_produto_absent=True
html_escaped_produto_present=True
html_raw_referencia_absent=True
html_escaped_referencia_present=True
html_raw_titulo_absent=True
html_escaped_titulo_present=True
svg_raw_produto_absent=True
svg_escaped_produto_present=True
```

Teste versionado executado:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider `
  tests\test_relatorio_html_service.py
```

Resultado: **5 passed in 8.84s**.

## 5. Segredos no estado atual e no histórico Git

Busca no workspace:

```powershell
rg -n -i '(api[_-]?key|secret|token|password|passwd|senha|private[_ -]?key|client[_-]?secret|jwt|webhook|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk[-_][A-Za-z0-9_-]{12,})' `
  . -g '!venv/**' -g '!.venv/**' -g '!**/*.db' -g '!**/*.png' -g '!**/*.ico'
```

Busca em todos os commits alcançáveis:

```powershell
$regex = '(api[_-]?key|client[_-]?secret|jwt[_-]?secret|webhook[_-]?secret|password|passwd|senha|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk[-_][A-Za-z0-9_-]{12,})'
foreach ($commit in (git rev-list --all)) {
  git grep -I -n -E $regex $commit -- ':!*.png' ':!*.ico'
}
```

Comandos adicionais:

```powershell
git ls-files
git log --all --name-status --format='COMMIT %H %ad %s' --date=iso-strict
git status --ignored --short
```

Resultado: `HISTORY_SECRET_HITS=0`; o banco `.db` está ignorado e não foi
versionado.

## 6. Arquivos de deploy e bundle

```powershell
rg --files -g 'Dockerfile*' -g 'docker-compose*.yml' -g 'docker-compose*.yaml' `
  -g '.github/**' -g '.gitlab-ci.yml' -g 'azure-pipelines.yml' -g 'Jenkinsfile' `
  -g 'Chart.yaml' -g 'values*.yaml' -g 'helm/**' -g '*.tf' -g '*.tfvars' `
  -g 'k8s/**' -g 'deploy/**' -g '.env*'
```

Resultado: nenhum desses arquivos. O deploy presente é `FDT_Sales_Manager.spec` e
`scripts/build_release.ps1`.

```powershell
.\.venv\Scripts\python.exe -c "import PyInstaller; print(PyInstaller.__version__)"
powershell -ExecutionPolicy Bypass -File .\scripts\build_release.ps1
```

Resultado: PyInstaller **6.22.2**. O comando ultrapassou **300 segundos** durante a
análise de dependências de Pandas/Matplotlib, mas o processo filho concluiu depois e
criou `dist/FDT Sales Manager`.

O bundle foi lido sem execução por um script Python que aplicou expressões regulares
binárias para chaves AWS, tokens GitHub, chaves no formato `sk-*`, chaves privadas e
atribuições de credenciais. O script reportou somente caminho, tipo e contagem; uma
segunda passagem exibiu apenas versões mascaradas dos matches para triagem.

Resultados:

```text
BUNDLE_FILES_SCANNED=1907
BUNDLE_BYTES_SCANNED=115981209
BUNDLE_SECRET_HITS=6 (preliminares)
SENSITIVE_EXTENSION_FILES=0
PRIVATE_PEM_FILES=0
```

Os seis hits preliminares eram símbolos compilados em OpenSSL/MSVC/NumPy/Pandas,
como prefixos `sk_se...func`, `sk_cl...back` e `sk_ob...rray`; nenhum era segredo.
Resultado verificado do bundle: **0 segredos confirmados**.

## 7. Suíte geral

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado: 156 testes coletados; execução chegou a 59% sem falha exibida antes do
timeout de 120 segundos. Isso é uma limitação de tempo, não aprovação integral.

## 8. Geração e validação do PDF

```powershell
& 'C:\Users\Gebruiker\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  docs\security-audit\gerar_relatorio_pdf.py
```

Validações executadas após a geração:

```powershell
& 'C:\Users\Gebruiker\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  -c "from pypdf import PdfReader; ..."
```

```powershell
# Rasterização com pypdfium2 para tmp/pdfs/security-audit/
& 'C:\Users\Gebruiker\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  docs\security-audit\renderizar_pdf.py
```

Resultado final: PDF A4 com **6 páginas** e **76.669 bytes**. A extração com
`pypdf` confirmou título, delimitadores da issue, marcadores Markdown, rodapé em
todas as páginas e zero caracteres de substituição. As 6 páginas foram
rasterizadas com `pypdfium2` em escala 1,8 e inspecionadas; após duas correções de
paginação, não restaram cortes, sobreposições, cabeçalhos órfãos ou tabelas/gráficos
ilegíveis.
