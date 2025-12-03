# Handoff Sprint 1 - Symforge Core SDK

**Data**: 2025-12-02
**Versão**: v0.1.2
**Status**: Concluída e Aprovada

---

## 1. Resumo Executivo

A Sprint 1 estabeleceu a fundação do Symforge SDK com CLI funcional, persistência YAML+Git e runtime completo para execução de processos como código.

| Métrica | Resultado |
|---------|-----------|
| Story Points | 23/23 (100%) |
| Features | 4/4 entregues |
| Testes BDD | 18 cenários passando |
| Testes TDD | 146 testes passando |
| Cobertura | 87% (meta: 80%) |
| forge_coder Score | 9.2/10 |
| Jorge Process Review | APROVADO |

---

## 2. Features Entregues

### F01: Init Processos (5 pts)
**Track**: value_init_multi_dominios

Comandos CLI para inicialização e validação de projetos:
```bash
symforge init -p <processo> <target>
symforge validate <process.yml> [--recursive]
```

**Arquivos principais**:
- `src/symforge/application/usecases/init_process.py`
- `src/symforge/adapters/cli/init_cli.py`

---

### F02: Processos como Código (8 pts)
**Track**: value_processos_codigo_rollback

Runtime para execução de processos com state machine:
```bash
symforge start --process <name> [--required file.md]
symforge resume <session_id>
symforge reset <session_id> <step_id>
```

**Estados implementados**:
- `RUNNING` - Sessão em execução
- `AWAITING_INPUT` - Aguardando artefato obrigatório
- `AWAITING_DECISION` - Aguardando decisão humana (HIL)

**Arquivos principais**:
- `src/symforge/domain/session.py` - Entidade de domínio
- `src/symforge/domain/states.py` - Enum de estados
- `src/symforge/application/usecases/runtime.py` - Use cases
- `src/symforge/adapters/cli/runtime_cli.py` - Adapter CLI

---

### F03: Symbiotas HIL (5 pts)
**Track**: value_symbiotas_hil

Human-in-the-loop checkpoints para decisões críticas:
```bash
symforge decide <session_id> <decision>
symforge status <session_id>
```

**Comportamento**:
- Passo HIL coloca sessão em `AWAITING_DECISION`
- Decisão registrada no histórico como `decision:<valor>`
- Fallback humano quando symbiota falha

**Arquivos principais**:
- `src/symforge/domain/session.py` - mark_awaiting_decision(), register_decision()
- `src/symforge/application/usecases/runtime.py` - mark_decision()

---

### F04: Persistência YAML+Git (5 pts)
**Track**: SUPPORT

Persistência de sessões com auto-commit Git opcional:
```bash
symforge start --process demo --auto-commit
symforge resume <id> --auto-commit
```

**Estrutura de dados**:
```
.symforge/
└── sessions/
    └── <session_id>.yaml
```

**Arquivos principais**:
- `src/symforge/infrastructure/session_repository.py`

---

## 3. Arquitetura

```
src/symforge/
├── domain/                    # Pure business logic (100% coverage)
│   ├── session.py             # Session entity + state machine
│   ├── states.py              # SessionState enum
│   ├── exceptions.py          # Domain-specific exceptions
│   └── process_definition.py  # Process definition VO
│
├── application/               # Use cases (95-100% coverage)
│   ├── usecases/
│   │   ├── runtime.py         # start, resume, reset, decide
│   │   ├── init_process.py    # init, validate
│   │   └── observability.py   # diagrams, handoff
│   └── plugins/
│       └── manager.py         # Plugin lifecycle
│
├── adapters/cli/              # CLI adapters (61-100% coverage)
│   ├── runtime_cli.py         # Runtime commands
│   └── plugins_cli.py         # Plugin commands
│
├── infrastructure/            # Persistence (96% coverage)
│   └── session_repository.py  # YAML + Git integration
│
└── cli.py                     # Main entrypoint
```

**Princípios seguidos**:
- Clean/Hexagonal Architecture (ForgeBase)
- Domain sem I/O
- Exceções de domínio específicas (nunca Exception genérico)
- CLI-first, offline-first

---

## 4. Exceções de Domínio

Criadas em `src/symforge/domain/exceptions.py`:

| Exceção | Uso |
|---------|-----|
| `DomainException` | Base para todas |
| `StepNotFoundError` | Reset para passo inexistente |
| `NoPendingDecisionError` | Decide sem decisão pendente |
| `SessionNotFoundError` | Sessão não encontrada |
| `InvalidManifestError` | Manifesto de plugin inválido |
| `PluginNotFoundError` | Plugin não instalado |
| `PluginTypeError` | Tipo de plugin incorreto |
| `NetworkPermissionDeniedError` | Network em modo offline |

---

## 5. Testes

### Estrutura
```
tests/
├── bdd/                       # 18 cenários Gherkin
│   ├── test_init_processos_steps.py
│   ├── test_processos_codigo_steps.py
│   └── test_symbiotas_hil_steps.py
│
└── unit/                      # 146 testes TDD
    ├── domain/
    │   └── test_session.py    # 32 testes
    ├── infrastructure/
    │   ├── test_session_repository.py  # 23 testes
    │   └── test_git_integration.py     # 10 testes
    ├── application/
    │   ├── test_runtime_usecases.py    # 25 testes
    │   └── test_plugin_manager.py      # 28 testes
    └── test_cli.py            # 9 testes
```

### Execução
```bash
# Todos os testes
pytest

# Apenas BDD
pytest tests/bdd/

# Apenas TDD
pytest tests/unit/

# Com cobertura
pytest --cov=src/symforge --cov-report=term-missing
```

---

## 6. ADRs

### ADR-001: Runtime CLI, Persistência YAML+Git e Plugins no-code
**Status**: Aceito (Implementado na Sprint 1)

Decisões principais:
1. Arquitetura em camadas (ForgeBase)
2. Persistência em `.symforge/sessions/` (YAML)
3. Auto-commit Git opcional por step
4. Plugins instalados via `symforge plugin add <git-url>`
5. CLI-first (sem HTTP/TUI no MVP)

---

## 7. Débitos Técnicos

| Item | Cobertura Atual | Meta | Prioridade |
|------|-----------------|------|------------|
| `plugins_cli.py` | 61% | 80% | Média |
| `cli.py` | 68% | 80% | Média |
| Testes e2e | 0 | TBD | Baixa |

---

## 8. Backlog Sprint 2

### Features (Stretch Goals da Sprint 1)
| ID | Feature | Story Points | Track |
|----|---------|--------------|-------|
| F05 | Plugins no-code (send/export) | 8 pts | value_plugins_no_code |
| F06 | Observabilidade (diagrama/handoff) | 5 pts | value_observabilidade_handoff |

### Melhorias de Processo
| ID | Ação | Prioridade |
|----|------|------------|
| A1 | Aumentar cobertura CLI >= 80% | Alta |
| A2 | Criar ADR-010 (Pre-Stakeholder Validation) | Média |
| A3 | Adotar commits por feature | Média |
| A4 | Criar templates review/retro em /process | Baixa |

---

## 9. Como Continuar

### Setup do ambiente
```bash
cd /mnt/c/Users/palha/dev/symforge
source .venv/bin/activate
pip install -e ".[dev]"
```

### Verificar estado atual
```bash
# Testes
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Comandos CLI disponíveis
```bash
# Init
symforge init -p forgeprocess myproject
symforge validate process.yml

# Runtime
symforge start --process demo --required doc.md
symforge resume <session_id>
symforge reset <session_id> <step_id>
symforge decide <session_id> approved
symforge status <session_id>

# Plugins
symforge plugin add <repo_path>
symforge plugin list
symforge plugin send <id> <payload>
symforge plugin export <id> <input>
```

---

## 10. Artefatos de Sprint

| Artefato | Localização |
|----------|-------------|
| Planning | `project/sprints/sprint-1/planning.md` |
| Progress | `project/sprints/sprint-1/progress.md` |
| Review Técnico | `project/sprints/sprint-1/review.md` |
| Retrospectiva | `project/sprints/sprint-1/retrospective.md` |
| Jorge Process Review | `project/sprints/sprint-1/jorge-process-review.md` |
| Handoff BDD | `docs/handoff_bdd.md` |
| Handoff MDD | `docs/handoff_mdd.md` |

---

## 11. Contatos

**Stakeholder**: Palhano
**Team**: Agent Coders (Claude Code)
**Symbiotas**: forge_coder (técnico), Jorge the Forge (processo)

---

**Assinado por**: Claude Code
**Data**: 2025-12-02
**Versão**: v0.1.2
