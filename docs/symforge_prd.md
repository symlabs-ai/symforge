# Symforge – Product Requirements Document (PRD)

## 1. Visão e Objetivo
- **Propósito**: Symforge é um motor universal para definir e executar processos estruturados (software, livros, gestão, etc.) com rastreabilidade de ponta a ponta, sessões dirigidas por agentes (LLMs) e symbiotas especializados.
- **Resultado esperado**: Usuários adotam processos versionáveis (YAML/Markdown), os executam via CLI/TUI, coletam evidências de valor (artefatos, métricas) e mantêm handoffs consistentes.
- **Pilares**: Processos como código (`PROCESS.yml` + Markdown), execução guiada por fluxo e checkpoints, decisões Human-in-the-Loop (HIL), publicação e validação automatizadas.
- **Benefícios para usuários**:
  1) Processos em linguagem natural: o fluxo é descrito como se fala com a equipe, sem notações complexas, e o Symforge traduz em execução organizada.
  2) Voltar atrás sem medo: cada passo fica versionado, com histórico de decisões e artefatos, permitindo rollback seguro e recuperação rápida.
  3) Symbiotas 24x7: agentes acompanham o processo, aprendem com o contexto e pedem aprovação apenas nos pontos críticos.
  4) Plugins sem código: integrações (e-mail, WhatsApp, exportações) são criadas ou ajustadas pelo usuário usando modelos simples, sem programar.
  5) Diagramas sob demanda: visões automáticas e sempre atualizadas facilitam entendimento, alinhamento e apresentação para stakeholders.
  6) Composição fácil de novos processos: em qualquer área, combinam-se blocos e templates em linguagem natural para criar e adaptar fluxos rápido, sem depender de ferramentas diferentes ou time técnico.

## 2. Escopo
- **Incluído**
  - Biblioteca de processos em `processes/*` (ForgeProcess como referência).
  - CLI/TUI para iniciar, retomar, validar e visualizar execuções.
  - Symbiotas (prompts) para coaching, revisão, publicação e auditoria.
  - Geração de diagramas Mermaid e validação de schema/processo.
  - Templates e policies para estrutura alvo de projetos.
  - Versionamento do repositorio com Git controlado pelo symforge
  - Persistência de sessões em YAML (`.symforge/sessions`)  também versionadas.
- **Excluído**
  - UI web (roadmap futuro).
  - Execução distribuída/colaborativa em tempo real.
  - Orquestração de CI/CD (fora do motor; pode integrar via scripts externos).

## 3. Personas
- **Product Owner / Stakeholder**: define visão, aprova fases MDD/Delivery, toma decisões HIL.
- **Tech Lead / Engenheiro(a)**: estrutura roadmap, arquitetura, TDD, conduz sessions.
- **Agente LLM / Symbiota**: auxilia em coaching, revisão técnica, publicação, auditoria de processo.
- **Facilitador(a) de Processo**: garante compliance com policies e handoffs.

## 4. Casos de Uso Principais
- Inicializar projeto a partir de um processo (`symforge init -p forgeprocess myproject`).
- Validar um processo (`symforge validate processes/forgeprocess/PROCESS.yml --recursive`).
- Executar fluxo de um processo: `start` → (processar steps/decisions) → `end`.
- Retomar sessão pausada ou aguardando input (`symforge resume`).
- Registrar decisão HIL (`symforge decide <opcao>`).
- Navegar no fluxo (`goto <node_id>`, `reset <node_id>`).
- Registrar handoff de sessão (`symforge handoff`) e notas (`symforge note`).
- Gerar diagramas (`symforge diagram ...`) e inspeções (`symforge info ...`).
- Operar via TUI (`symforge tui`) para acompanhamento interativo. (opcional)

## 5. Funcionalidades

### 5.1 Biblioteca de Processos
- Estrutura em `processes/<processo>/` com `PROCESS.yml` (macro) e subprocessos (ex.: `mdd/PROCESS.yml`).
- Artefatos versionáveis (Markdown) referenciados por paths e templates.
- Diagramas Mermaid juntamente com os arquivos PROCESS.md e yml (colocar na mesma pasta DIAGRAM.md)
- Symbiotas em `symbiotes/<nome>/prompt.md`. (prompt deve ter front-matter)

### 5.2 CLI
- Descoberta e resolução de `--lib-root` ou `SYMFORGE_LIB_ROOT`.
- Comandos de biblioteca/processos:
  - `init -p <processo> <projeto>`: copia processo para `process/` e estrutura alvo.
  - `update`: sincroniza processo existente (PROJECT_ROOT) com a biblioteca (LIB_ROOT) (executar dentro do projeto).
  - `list-processes`: lista processos disponíveis.
  - `list-agents`: lista coding agentes LLM configurados (config global).
  - `list-symbiotes`: lista symbiotas (ambiente projeto).
- Prompts e produção de conteúdo:
  - `-prompt <prompt_file> <target_file>` (flag global): executa prompt com LLM configurado.
  - `produce ...` (arquitetura de plugins para produtores e extensões no-code: ex: Gamma.ai):
    - `produce generate`: gera apresentação/documento/webpage/social com opções de texto, formato, tema, imagem, export (pdf/pptx), pastas.
    - `produce from-template`: adapta template existente com prompt, tema e export opcional.
    - `produce status [--wait --interval --timeout] <generation_id>`: consulta estado e opcionalmente espera.
    - `produce themes [--limit --after]`: lista temas do workspace.
    - `produce folders [--limit --after]`: lista pastas do workspace.
- Inspeção e validação de processos:
  - `validate <PROCESS.yml> [...] [--recursive]`: valida contra `esquemas/process.schema.json`.
  - `info <PROCESS.yml>`: imprime resumo (fases, steps, symbiotas, layout) em formato arvore.
  - `diagram <PROCESS.yml> -t <flowchart|state|summary|all> [-o <file>]`: gera diagramas Mermaid.
- Execução de processos:
  - `start [-f <process_file>] [-n <nome>] [--interactive|--batch]`: inicia sessão.
  - `status [session_id] [-v | --json | -a]`: estado e histórico.
  - `resume [session_id] [--interactive|--batch] [--force]`: retoma sessão.
  - `decide <decision> [rationale] [-s <session>] [-a <actor>] [--batch]`: registra decisão HIL.
  - `log [session_id] [--node <id>] [--type <tipo>] [--limit N] [--json]`: exibe log detalhado.
  - `end [session_id] [--cancel] [-m <note>]`: encerra sessão (completed/cancelled).
  - `delete [session_id] [-f]`: deleta sessão.
  - `reset [node_id] [--commit HASH] [--dry-run] [-f]`: reseta execução e outputs afetados.
  - `sessions list [--status] | sessions delete <id> | sessions export <id>`: gestão de sessões.
  - `reply <message> [--batch]`: responde symbiota e continua (note+resume).
- Notas, handoff e configuração:
  - `handoff [session_id] [-o file] [--no-history] [--no-decisions]`: exporta contexto completo.
  - handon recupera contexto da sessão ativa com base no documento gerado anteriormente pelo handoff
  - `config [key] [value]`: exibe ou altera configurações do projeto (ex.: verbose).
- Interface:
  - `tui [session_id]`: dashboard interativo Textual para acompanhar sessões.
  - `plugin <cmd>` (planejado): listar/adicionar/inspecionar plugins no-code (send/export/hook/generate) instalados no projeto.

### 5.3 Engine de Execução
- **FlowGraph + FlowInterpreter**: lê `PROCESS.yml`, executa nodes (start, step, decision, call subprocess, end), gerencia stack de subprocessos.
- **Estados de sessão**: `RUNNING`, `PROCESSING`, `AWAITING_DECISION`, `AWAITING_INPUT`, `PAUSED`, `COMPLETED`, `FAILED`, `CANCELLED` (definidos em `docs/SESSION_STATES.md`). fonte da verdade
- **Loop protection**: limite de iterações e visitas por nó (para evitar loops).
- **Validação de inputs/outputs**: bloqueia execução e aponta arquivos faltantes.
- **Symbiota integration**: steps podem invocar prompts; decisões podem ser HIL ou por symbiota (quando permitido).
- **Auto-commit**: registros git por step ou final de phase. Imprescindivel para o controle de versão com rollback

#### 5.3.1 Sistema de Estados de Sessão (Resumo de docs/SESSION_STATES.md)
- **Governança**: A CLI é a única fonte de transições; a TUI apenas reflete estado, dispara comandos e mostra ações válidas (nunca altera arquivos/estado diretamente).
- **Estados e significados**:
  - RUNNING: executando nós do fluxo; origem em `start/resume/decide`.
  - PROCESSING: symbiota/AI trabalhando (transiente); retorna a RUNNING ou AWAITING_INPUT.
  - AWAITING_DECISION: bloqueado em decisão HIL; requer `symforge decide`.
  - AWAITING_INPUT: inputs/outputs obrigatórios faltando; requer criação e `symforge resume`.
  - PAUSED: pausa intencional; retoma com `resume`.
  - COMPLETED/FAILED/CANCELLED: terminais (sem transições posteriores).
- **Transições chave**: `start` → RUNNING; `decide` ou `resume` liberam AWAITING_DECISION/INPUT; `end` encerra (completed/cancelled); erros/loops → FAILED; `reset` retorna a RUNNING e limpa outputs afetados.
- **TUI por estado**: mostra rótulos e ações rápidas (ex.: AWAITING_DECISION → tecla `d`; AWAITING_INPUT/PAUSED → `c`; FAILED → `R`; COMPLETED/CANCELLED → `h`; RUNNING/PROCESSING → apenas visualizar).
- **Invariantes**: um status por vez; apenas AWAITING_DECISION carrega `pending_decision`; apenas AWAITING_INPUT carrega `pending_input`; terminais não saem; PROCESSING sempre transiente.
- **Sessões órfãs**: detectadas quando RUNNING/PROCESSING sem execução real (possivel encerramento com crash); recupera com `symforge resume --force` (ou tecla `c` na TUI que chama o comando).
### 5.4 Persistência
- Diretório `.symforge/` em projeto: `config.yml`, `env.example`, `credentials/`, `sessions/`.  (não versionado .gitignore)
- Sessões em YAML: `session.yml`, `history.yml`, `decisions.yml`, `notes.yml`. (versionado)
- Handoff exportável via comando `handoff` (MD em `sessions/`). (versionado)

### 5.5 TUI
- Base Textual: painel de sessão, status bar, modal de decisões, viewer de arquivos (MD), atalhos (`q`, `r`, `d`, `v`, `e`, `c`, `R`, `h`).
- Regras de interface por estado (não exibir ações inválidas).
- Pendências: árvore de processo, preview de próximos passos, histórico de comandos, log viewer (ver TODO).

### 5.6 Diagramas e Validação
- `diagram_generator.py` para flowcharts/summary.
- `semantic_validator.py` e `scripts/validate_process.py` para schema + checks.
- `scripts/validate_diagrams.py` para verificar blocos Mermaid.

### 5.7 Symbiotas e Prompts
- Symbiotas padrão (ForgeProcess): `mdd_coach`, `mdd_publisher`, `bill_review`, `jorge_forge`, `orchestrator`.
- Prompts reutilizáveis para handoff/handon (`prompts/handoff.md`, `prompts/handon.md`) e conversão MD → YAML (`prompts/process_to_yaml.md`).
- Suporte a provedores (Codex, Claude, Gemini) configurados em ; `.symforge/config.yml`

### 5.8 Plugins
- Manifestos em `plugins/<nome>/plugin.yml` definem tipo (`send|export|hook|generate`), entrypoint/comando e permissões (rede/arquivos).
- Execução no-code: usuário configura payloads/inputs sem escrever código; plugins podem enviar (e-mail, WhatsApp, Slack), exportar (MD→CSV/Excel), gerar conteúdos ou reagir a eventos.
- Descoberta e gestão planejadas via CLI (`plugin list/info/add`); sandbox/timeout para segurança.

### 5.9 Integrações Externas
- **Gamma API**: geração e exportação de apresentações (helpers em `gamma_api.py`). Integrar na arquiteura de plugins para produce
- **Git**: auto-commits e resets controlados pelo engine (não usar comandos destrutivos fora do fluxo).
- **LLM providers**: usados pelos symbiotas via prompts (`.symforge/config.yml` ).

### 5.10 Guia para Criar Novos Processos (Resumo de docs/guides/creating-processes.md)
- **Anatomia**: cada processo tem `PROCESS.md` (documentação humana) e `PROCESS.yml` (contrato executável). Markdown é fonte de verdade e deve ser convertido para YAML usando o prompt `process_to_yaml.md`.
- **Fluxo recomendado**:
  1) Criar pasta em `processes/<nome>/`.
  2) Copiar `esquemas/PROCESS_TEMPLATE.md` para `PROCESS.md` e preencher (ID, versão semver, narrativa, fases, passos).
  3) Gerar YAML via `symforge -prompt process_to_yaml.md processes/<nome>/PROCESS.md`.
  4) Validar com `symforge validate processes/<nome>/PROCESS.yml` (ou `scripts/validate_process.py`).
- **Obrigatórios**: identificação (id, versão), descrição/narrativa, estrutura de pastas alvo, ao menos uma fase com um passo.
- **Opcionais úteis**: symbiotas por fase, decisões HIL, métricas de qualidade, artefatos mapeados com paths.
- **Erros comuns**: fase sem `steps`, versão fora do semver, ausência de `narrative` em fases/passos. Use o schema `esquemas/process.schema.json` para prevenir.
- **Automação/CI**: exemplo de workflow para validar `PROCESS.yml` em push/PR; usar `pip install pyyaml jsonschema` e `scripts/validate_process.py processes/*/PROCESS.yml`.
- **Referências**: template (`esquemas/PROCESS_TEMPLATE.md`), schema (`esquemas/process.schema.json`), validador (`scripts/validate_process.py`), prompt (`prompts/process_to_yaml.md`).

### 5.11 Visão de Produto (Resumo de docs/VISION.md)
- **Tese central**: motor universal de processos; o que muda por domínio é o processo carregado (ForgeProcess, BookForge, BizForge, etc.), com humanos no centro e pontos HIL explícitos.
- **Componentes do ecossistema**:
  - Biblioteca de processos (`processes/`), com fases, artefatos, políticas, templates, diagramas e symbiotas.
  - CLI `symforge` para scaffold (`init`) e orquestração inicial conforme `docs/SYMFORGE_CLI.md`.
  - Motor/runtime (em `src/`): carrega processos, coordena symbiotas, registra sessões/handoffs/métricas.
- **Princípios**: agnóstico de domínio; processo como código; documentação como fonte de verdade; HIL por padrão; symbiotas especializados; estruturas previsíveis (layout).
- **Experiência-alvo**: time escolhe processo (`symforge init -p <processo>`), recebe estrutura-alvo (`process/`, `specs/`, `project/`, `src/`, `tests/`), trabalha em sessões guiadas por symbiotas, registra handoffs, evolui o processo e pode devolver melhorias para a biblioteca.
- **Roadmap alto nível**: V1 biblioteca + CLI básica; V2 runtime; V3 observabilidade (métricas, visualizações); V4 ecossistema multi-processo (BookForge, BizForge, etc.).
- **Contribuição**: evoluir motor (`src/`), processos (`processes/**`), prompts/handoffs (`prompts/`, `sessions/`), e CLI docs (`docs/SYMFORGE_CLI.md`) alinhados à visão.

## 6. Requisitos Funcionais
- RF01: Carregar biblioteca de processos a partir de `processes/` ou `--lib-root`, respeitando ordem de resolução (CLI flag > SYMFORGE_LIB_ROOT > auto-detect do arquivo/cwd) e falhando com mensagem clara se `processes/` não for encontrado.
- RF02: Validar `PROCESS.yml` (macro e subprocessos) contra `esquemas/process.schema.json`, incluindo validação recursiva de `sub_phase`/`subprocesses`, tipos de nós (`start`, `step`, `call`, `decision`, `end`), enums e presença de artefatos/layout; relatório deve apontar campo, causa e sugestão.
- RF03: Executar fluxo completo, incluindo chamadas a subprocessos, decisões HIL e steps com symbiotas; manter stack de chamadas e contexto ao retornar (`on_return`), garantindo que o fluxo termina em nó `end` ou entra em estado terminal.
- RF04: Persistir estado da sessão (histórico, decisões, notas, pending_input/pending_decision) em YAML em `.symforge/sessions/<id>/`, com IDs estáveis e reabríveis via `resume`.
- RF05: Detectar e bloquear loops acima de limites configurados (iterações totais e visitas por nó); registrar motivo no histórico e mover sessão para `FAILED`.
- RF06: Checar existência de inputs/outputs obrigatórios antes de avançar um step; se faltar, mover para `AWAITING_INPUT`, listar caminhos faltantes e retomar após criação (`resume`).
- RF07: Gerar diagramas Mermaid a partir de processos (`diagram`), suportando tipos `flowchart` e `summary`, com saída em Markdown e caminhos de entrada/saída configuráveis.
- RF08: Exportar handoff/notes em Markdown (`handoff`, `note`, `notes`) incluindo estado atual, histórico resumido, decisões, bloqueios e próximos passos.
- RF09: Operar via TUI refletindo estados em tempo real (RUNNING, PROCESSING, AWAITING_DECISION, AWAITING_INPUT, PAUSED, COMPLETED, FAILED, CANCELLED); permitir decidir (`d`), visualizar (`v`), editar (`e`), continuar (`c`) quando aplicável.
- RF10: Scaffold de projeto (`init`) respeitando layout-alvo do processo escolhido (`project_layout.required_dirs/files`), copiando processo para `process/` e exibindo `getting_started`.
- RF11: Atualizar processo em projeto existente (`update`) sem corromper customizações locais; no mínimo detectar conflitos e avisar (merge seguro planejado no roadmap).
- RF12: Listar processos disponíveis (`list-processes`) com ID, título, versão e breve descrição; indicar qual é default.
- RF13: Integrar symbiotas com prompts definidos no processo, carregando `prompt_file`, passando contexto do step e honrando `can_decide` (somente HIL decide quando `can_decide: false`).
- RF14: Suportar HIL checkpoints (MDD aprovação, Delivery reviews, Feedback loop) preservando decisão humana; registrar decisão, ator e timestamp; bloquear avanço até escolha explícita.

## 7. Requisitos Não Funcionais
- RNF01: CLI responsiva; carregamento preguiçoso de dependências pesadas.
- RNF02: Compatibilidade com Python 3.x e ambientes POSIX/Windows.
- RNF03: Arquivos UTF-8; preferir Markdown/YAML legíveis.
- RNF04: Diagramas somente em Mermaid; sem PlantUML.
- RNF05: Segurança de credenciais: `.symforge/credentials/` gitignored; `.env` não versionado.
- RNF06: Extensibilidade de processos (novos domínios) sem alterar engine.
- RNF07: Observabilidade mínima: logs em `logs/` (gitignored), status em TUI/CLI.
- RNF08: Resiliência a falhas de rede/LLM: fallback para HIL, mensagens claras.

## 8. Fluxos Principais
- **Init Projeto**
  1. `symforge init -p <processo> <projeto>`
  2. Cria `process/`, `specs/`, `project/`, `src/`, `tests/` conforme `project_layout`.
  3. Copia processo escolhido para `process/`.
  4. Exibe `getting_started` do processo.
- **Execução de Processo**
  1. `symforge start` cria sessão (`RUNNING`).
  2. Steps executados; se input/output faltante → `AWAITING_INPUT`.
  3. Decisões HIL → `AWAITING_DECISION` (registro com `decide`).
  4. Symbiotas podem entrar em `PROCESSING`.
  5. Fluxo termina em `COMPLETED` ou `FAILED/CANCELLED`.
  6. Handoff opcional (`symforge handoff`).
- **Validação**
  - `symforge validate <PROCESS.yml> --recursive`: valida macro + subprocessos e exibe resumo.
- **Diagramas**
  - `symforge diagram ...`: gera MD com bloco Mermaid para flowchart ou summary table.
- **Handoff/Notas**
  - `symforge note "..."` e `symforge handoff` → salva em `sessions/` (MD).

## 9. Dados e Estrutura
- **Processo**: `PROCESS.yml` com `phases`, `flow`, `artifacts`, `symbiotes`, `quality_metrics`, `project_layout`, `getting_started`.
- **Sessão**: YAMLs em `.symforge/sessions/<id>/` com estado, histórico, decisões, notas.
- **Artefatos-alvo**: conforme `PROJECT_LAYOUT.md` do processo (ex.: `specs/`, `project/`, `src/`, `tests/`).
- **Prompts/Symbiotas**: `symbiotes/<nome>/prompt.md`.
- **Diagramas**: blocos Mermaid em `docs/diagrams/<processo>/*.md`.

## 10. Políticas e Regras
- Seguir `AGENTS.md` (não criar arquivos soltos na raiz de `process/`; respeitar HIL).
- Manter Execução (`execution/`) separada de Delivery (`delivery/`); diagramas devem refletir.
- Usar Mermaid para diagramas; evitar PlantUML.
- Preservar decisões humanas nos pontos marcados `🔸 HIL`.

## 11. Métricas e Sucesso
- Adoção: nº de projetos inicializados via `symforge init`.
- Qualidade de processo: % de validações que passam sem erro; % de artefatos obrigatórios presentes.
- Eficiência: tempo médio de execução de comandos de validação/diagramas.
- Fluxo: nº de sessões completadas vs. falhadas; incidência de loops detectados.
- Valor de negócio (para ForgeProcess): % de ValueTracks entregues, KPIs atingidos (definidos no processo).

## 12. Roadmap (a partir de TODO.md)
- TUI: árvore do processo, preview de próximos passos, histórico/auto-complete, log viewer.
- Git: branch automático por sessão, log de decisões em commits, integração PR.
- Web UI: dashboard, visualização interativa de flow graph, métricas e decisões HIL.
- Multi-session: execução paralela e merge de resultados.
- Testes: YamlStore, loop protection, engine (FlowInterpreter), E2E CLI.
- Documentação: guia de criação de symbiotas, guia de prompts, troubleshooting.

## 13. Critérios de Aceite (MVP do motor)
- Validar com sucesso `processes/forgeprocess/PROCESS.yml` e subprocessos via CLI.
- Executar sessão completa do ForgeProcess com transições e bloqueios corretos (inputs/decisions).
- TUI refletindo estados e permitindo decisões/input.
- Handoff exportável e re-importável (contexto preservado).
- Diagramas gerados para macro e subprocessos.
- Symbiotas carregados e invocados onde definidos (pelo menos mock/echo).

## 14. Riscos e Mitigações
- **Dependência de LLMs externos**: fallback para HIL; mensagens de erro claras.
- **Estrutura inconsistente em processos novos**: schema + `validate_process.py`.
- **Perda de estado**: persistência em YAML e handoff; evitar manipulação direta fora da CLI/TUI.
- **Desorganização de artefatos**: enforcement via `PROJECT_LAYOUT.md` e validação de inputs/outputs.

## 15. Anexos/Referências
- `README.md`, `AGENTS.md`
- `processes/forgeprocess/PROCESS.yml` e subprocessos (`mdd/`, `bdd/`, `execution/`, `delivery/`)
- `docs/layout/PROJECT_LAYOUT.md`
- `docs/SESSION_STATES.md`
- `esquemas/process.schema.json`
- `prompts/handoff.md`, `prompts/handon.md`, `prompts/process_to_yaml.md`
