# Handoff diário — Fase BDD (core)

## Contexto e objetivo
- Fechamos a fase BDD (@ci-fast) com todas as features Gherkin executáveis e passos implementados para o núcleo (init/processos como código), plugins no-code e observabilidade/handoff, alinhados ao ForgeBase (CLI-first, offline, YAML+Git, Clean/Hex).
- Preparar terreno para Delivery/TDD seguindo ADR-001 e os prompts dos symbiotas já ajustados.

## Setup de ambiente e tooling
- Ambiente Python 3.12 em `.venv`; instalação via `python -m pip install -r requirements-dev.txt`.
- `requirements-dev.txt` inclui pytest, pytest-bdd, ruff, mypy, hypothesis, import-linter, deptry, pyyaml.
- Pre-commit configurado (`scripts/pre-commit-config.yaml`) e instalado para o git local (`scripts/install_precommit.sh`); deve rodar antes dos commits.
- `pytest.ini` criado para registrar marcas BDD (@ci-fast, @sdk, @plugins, @observabilidade, @hil etc.) e evitar warnings de marks desconhecidas.
- `PYTHONPATH=src` usado para rodar testes (não há pyproject ainda).

## Workflow adotado (ForgeBase)
- Arquitetura Clean/Hex: CLI → aplicação/usecases → ports → adapters/plugins → infra (FS/Git).
- Persistência declarativa em YAML com auto-commit Git por step (a implementar na fase Delivery).
- Plugins offline: instalados via git clone/cópia local para `plugins/`, com manifesto e `entrypoint` Python simples; sandbox por padrão.
- CLI-first, modo offline; containerização futura (Docker) somente para entrega final.
- ADR-001 registrado: runtime mantém `status` (RUNNING/AWAITING_INPUT/ERROR), storage YAML+Git, plugin manifest/permissions, integração CLI.

## Symbiotas e governança
- `AGENTS.md` ampliado: visão do repositório, pilares (Clean/Hex, CLI offline, YAML+Git, manifest), links para docs ForgeBase (`docs/guides/forgebase_guides/...`), regras gerais.
- Prompts ajustados:
  - `process/symbiotes/tdd_coder/prompt.md` e `process/symbiotes/test_writer/prompt.md` agora citam ForgeBase rules e AGENTS, reforçam TDD estrito.
  - `process/symbiotes/bill_review/prompt.md` aponta para `docs/guides/forgebase_guides/usuarios/forgebase-rules.md`.
- Persona `test_writer` usada para conduzir a escrita BDD.

## Entregas BDD
- Features (PT-BR, lowercase keywords, `# language: pt`): mapeadas em `specs/bdd/tracks.yml`.
  - `10_forge_core/init_processos.feature` — init de processo, validação de PROCESS.yml (com/sem erro).
  - `10_forge_core/processos_codigo.feature` — processos como código, status AWAITING_INPUT quando artefatos faltam.
  - `10_forge_core/symbiotas_hil.feature` — humano-no-loop para completar artefatos faltantes.
  - `30_plugins/plugins_no_code.feature` — criar/listar/rodar plugins `send/export/hook/generate` no-code.
  - `50_observabilidade/rastreabilidade_handoff.feature` — gerar diagrama Mermaid simples e handoff markdown.
- Passos implementados em `tests/bdd/*` — todos verdes: `PYTHONPATH=src . .venv/bin/activate && pytest tests/bdd -q` → 18 passed.
- Templates/processo BDD atualizados (`process/bdd/etapa_02_escrita_features.md`, `process/bdd/templates/template_feature.md`) para exigir PT-BR, tags padrão e `pytest --collect-only` na revisão.

## Implementações de apoio (mínimas para BDD)
- Runtime: `src/symforge/application/usecases/runtime.py` — status RUNNING/AWAITING_INPUT/ERROR conforme artefatos faltantes.
- Plugins: `src/symforge/plugins/manager.py` — add/list/execute (send/export/hook/generate), valida manifesto básico e carrega entrypoint via importlib.
- Observabilidade: `src/symforge/application/usecases/observability.py` — gera diagrama mermaid e handoff markdown simplificado.
- CLI adapters (ainda sem entrypoint final): `src/symforge/adapters/cli/runtime_cli.py` e `plugins_cli.py` para delegar aos usecases.

## Próximos passos (Delivery/TDD)
- Abrir fase TDD: implementar testes unit/integration reais antes do código, guiados pelo `test_writer`.
- Consolidar CLI real (`symforge`), wire dos adapters e auto-commit Git/YAML store conforme ADR-001.
- Implementar manifest/permissions de plugins de forma efetiva e fluxo de instalação offline.
- Evoluir observabilidade (diagramas/rastreio) e storage Git (commits por step) para os cenários BDD.
