# Symforge

SDK para orquestração de processos com versionamento Git, checkpoints Human-in-the-Loop (HIL) e plugins no-code.

## Installation

```bash
pip install symforge
```

Ou para desenvolvimento:

```bash
git clone https://github.com/symlabs-ai/symforge.git
cd symforge
pip install -e .
```

## Quick Start

### 1. Inicializar um projeto

```bash
# Criar estrutura para ForgeProcess
symforge init -p forgeprocess my_project

# Ou para BookForge
symforge init -p bookforge my_book
```

### 2. Validar o processo

```bash
symforge validate my_project/process/PROCESS.yml

# Validar recursivamente (inclui artefatos referenciados)
symforge validate my_project/process/PROCESS.yml --recursive
```

### 3. Iniciar uma sessão

```bash
cd my_project

# Iniciar sessão de processo
symforge start --process demo --workspace .

# Com artefatos obrigatórios
symforge start --process demo --required doc.md --workspace .

# Com auto-commit Git
symforge start --process demo --workspace . --auto-commit
```

### 4. Gerenciar sessão

```bash
# Ver status da sessão
symforge status <session_id> --workspace .

# Retomar sessão pausada
symforge resume <session_id> --workspace .

# Registrar decisão HIL
symforge decide <session_id> "approved" --workspace .

# Resetar para passo anterior
symforge reset <session_id> step_id --workspace .
```

## CLI Reference

### Comandos principais

| Comando | Descrição |
|---------|-----------|
| `init` | Inicializa estrutura de processo |
| `validate` | Valida PROCESS.yml |
| `start` | Inicia sessão de processo |
| `resume` | Retoma sessão aguardando input |
| `status` | Mostra estado da sessão |
| `decide` | Registra decisão HIL |
| `reset` | Reseta sessão para passo anterior |
| `pause` | Pausa sessão e gera handoff |
| `complete` | Completa sessão e gera handoff final |

### Comandos de plugin

| Comando | Descrição |
|---------|-----------|
| `plugin add <repo>` | Instala plugin de repositório local |
| `plugin list` | Lista plugins instalados |
| `plugin send <id> <payload>` | Executa plugin tipo send |
| `plugin export <id> <input>` | Executa plugin tipo export |
| `plugin hook <id> <context>` | Executa plugin tipo hook |
| `plugin generate <id> <payload>` | Executa plugin tipo generate |

## Plugin Development

Plugins são componentes no-code que estendem o Symforge. Cada plugin consiste em:

### Estrutura do plugin

```
my_plugin/
  plugin.yml    # Manifesto
  plugin.py     # Código
```

### Manifesto (plugin.yml)

```yaml
id: my_plugin
name: My Plugin
version: "1.0.0"
type: send  # send | export | hook | generate
entrypoint: plugin:run
permissions:
  network: false  # Deve ser false (offline-first)
  fs: []          # Lista de paths permitidos
  env: []         # Lista de env vars permitidas
```

### Código (plugin.py)

```python
# Para tipo 'send'
def run(payload: dict) -> dict:
    return {"status": "ok", "data": payload}

# Para tipo 'export'
def export_file(input_path, output_path=None):
    content = input_path.read_text()
    return {"exported": True}

# Para tipo 'hook'
def on_event(context: dict) -> dict:
    return {"event": context.get("event"), "handled": True}

# Para tipo 'generate'
def generate(payload: dict) -> dict:
    return {"content": f"Generated: {payload.get('prompt')}"}
```

### Instalando um plugin

```bash
symforge plugin add /path/to/my_plugin
symforge plugin list
```

## Project Structure

Após `symforge init`, a estrutura gerada inclui:

```
my_project/
  process/
    PROCESS.yml       # Definição do processo
  .symforge/
    sessions/         # Sessões ativas
    plugins/          # Plugins instalados
```

## Architecture

Symforge segue Clean Architecture:

```
src/symforge/
  domain/           # Entidades e regras de negócio
  application/      # Casos de uso
  infrastructure/   # Repositórios e I/O
  adapters/         # CLI e interfaces externas
```

## Development

### Rodar testes

```bash
# Todos os testes
pytest tests/

# Com cobertura
pytest tests/ --cov=src/symforge

# Apenas BDD
pytest tests/bdd/

# Apenas E2E
pytest tests/e2e/
```

### Lint e type check

```bash
ruff check src/ tests/
mypy src/
```

## License

MIT

## Links

- [GitHub](https://github.com/symlabs-ai/symforge)
- [Issues](https://github.com/symlabs-ai/symforge/issues)
