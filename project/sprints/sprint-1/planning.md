# Sprint 1 - Planning

**Project**: Symforge
**Sprint Number**: 1
**Sprint Duration**: 2025-12-02 - 2025-12-16 (2 semanas)
**Planning Date**: 2025-12-02
**Team**: Agent Coders (Claude Code primary)
**Stakeholder**: Palhano

---

## Sprint Overview

### Sprint Goals

**Primary Goal**: Consolidar o core SDK do Symforge com CLI funcional, persistência YAML+Git e runtime completo.

**Secondary Goals**:
- Garantir testes TDD cobrindo todos os cenários BDD
- Implementar auto-commit Git por step

**Success Criteria**:
- [ ] CLI `symforge` funcional com comandos start/resume/reset/decide
- [ ] Persistência de sessões em YAML
- [ ] 18 cenários BDD passando + testes unitários TDD
- [ ] Coverage >= 80%

---

## Capacity Planning

### Velocity Baseline

**Primeira Sprint**: Sem baseline anterior
**Estimated Velocity**: 4-5 pts/sessão (estimativa conservadora)

### Capacity Calculation

**Sessions Available**: 6 sessões
- Frequência: 3 sessões/semana × 2 semanas = 6 sessões
- Duração: 2-3h por sessão

**Projected Capacity**: 6 sessões × 4 pts/sessão = **24 story points**

**Buffer**: ±20% para unknowns

**Final Capacity Range**: 20-28 story points

---

## Features Selected (from tracks.yml)

### Committed Features

| Feature ID | Feature Name | Story Points | Priority | Track |
|------------|--------------|--------------|----------|-------|
| F01 | Init processos (CLI + validação) | 5 pts | HIGH | value_init_multi_dominios |
| F02 | Processos como código (runtime) | 8 pts | HIGH | value_processos_codigo_rollback |
| F03 | Symbiotas HIL (checkpoints) | 5 pts | HIGH | value_symbiotas_hil |
| F04 | Persistência YAML+Git | 5 pts | HIGH | SUPPORT |
| **Total Committed** | | **23 pts** | | |

### Stretch Goals

| Feature ID | Feature Name | Story Points | Priority | Track |
|------------|--------------|--------------|----------|-------|
| F05 | Plugins no-code (send/export) | 8 pts | MEDIUM | value_plugins_no_code |
| F06 | Observabilidade (diagrama/handoff) | 5 pts | MEDIUM | value_observabilidade_handoff |

---

## Dependencies & Prerequisites

### Technical Dependencies

- [x] **Python 3.12**: Ambiente configurado em `.venv`
- [x] **pytest-bdd**: Instalado em requirements-dev.txt
- [x] **ruff/mypy**: Configurados para qualidade de código

### Process Dependencies

- [x] **Fase BDD Concluída**: 18 cenários executáveis passando
- [x] **ADR-001 Documentado**: Runtime status + YAML+Git storage

---

## Risks & Mitigation

### Risk 1: Complexidade da CLI

- **Probability**: Medium
- **Impact**: Medium
- **Description**: Wire da CLI com usecases pode ter edge cases
- **Mitigation**: TDD estrito, implementar comando por comando
- **Contingency**: Simplificar para MVP funcional

### Risk 2: Auto-commit Git

- **Probability**: Low
- **Impact**: Low
- **Description**: Integração Git pode falhar em alguns ambientes
- **Mitigation**: Testar em ambiente WSL2
- **Contingency**: Desativar auto-commit temporariamente

**Overall Risk Level**: Medium
**Confidence Level**: High

---

## Definition of Done

### Feature-Level DoD

Uma feature é DONE quando:

- [x] Cenários BDD passando
- [ ] Testes unitários TDD cobrindo casos de borda
- [ ] Coverage >= 80% para o módulo
- [ ] Lint e type check limpos
- [ ] Clean Architecture mantida
- [ ] Demo funcional via CLI

### Sprint-Level DoD

- [ ] 100% das features committed implementadas
- [ ] 18 cenários BDD + testes TDD passando
- [ ] Coverage >= 80% global
- [ ] bill-review >= 8/10
- [ ] Jorge review >= 8/10
- [ ] Documentação atualizada

---

## Sprint Timeline

| Date | Milestone | Owner |
|------|-----------|-------|
| 2025-12-02 | Sprint Planning Complete | Team |
| 2025-12-09 | Mid-Sprint Checkpoint | Team |
| 2025-12-13 | Feature Freeze | Team |
| 2025-12-14 | bill-review (Day 1) | bill-review |
| 2025-12-15 | Jorge review (Day 2) | Jorge the Forge |
| 2025-12-16 | Sprint Review & Retro (Day 3) | Stakeholder |

### Session Frequency

**Target**: 3 sessões/semana
**Duração**: 2-3h por sessão

---

## Feature Breakdown

### F01: Init processos (5 pts)

**Track**: value_init_multi_dominios
**BDD**: `specs/bdd/10_forge_core/init_processos.feature`

**Acceptance Criteria**:
- [ ] `symforge init -p <processo> <projeto>` cria estrutura
- [ ] `symforge validate` valida PROCESS.yml recursivamente
- [ ] Erro claro quando schema inválido

**TDD Tasks**:
- [ ] Test: init cria pastas obrigatórias
- [ ] Test: validate passa com schema válido
- [ ] Test: validate reporta campos faltantes

---

### F02: Processos como código (8 pts)

**Track**: value_processos_codigo_rollback
**BDD**: `specs/bdd/10_forge_core/processos_codigo.feature`

**Acceptance Criteria**:
- [ ] `symforge start` inicia sessão com fluxo carregado
- [ ] Bloqueia em AWAITING_INPUT quando artefato falta
- [ ] `symforge resume` retoma após artefato criado
- [ ] `symforge reset <passo>` faz rollback seguro
- [ ] Histórico preservado após reset

**TDD Tasks**:
- [ ] Test: start cria sessão com UUID
- [ ] Test: start detecta artefatos faltantes
- [ ] Test: resume só funciona após artefatos presentes
- [ ] Test: reset retorna ao passo anterior
- [ ] Test: reset inválido mantém sessão íntegra

---

### F03: Symbiotas HIL (5 pts)

**Track**: value_symbiotas_hil
**BDD**: `specs/bdd/10_forge_core/symbiotas_hil.feature`

**Acceptance Criteria**:
- [ ] Passo HIL coloca sessão em AWAITING_DECISION
- [ ] `symforge decide` registra decisão com ator/timestamp
- [ ] Fallback humano quando symbiota falha

**TDD Tasks**:
- [ ] Test: mark_decision registra decisão
- [ ] Test: sessão sai de AWAITING_DECISION após decide
- [ ] Test: decisão tem ator e timestamp

---

### F04: Persistência YAML+Git (5 pts)

**Track**: SUPPORT
**Tipo**: Infraestrutura

**Acceptance Criteria**:
- [ ] SessionRepository salva/carrega sessões em YAML
- [ ] Sessões ficam em `.symforge/sessions/`
- [ ] Auto-commit Git após cada transição de estado

**TDD Tasks**:
- [ ] Test: save persiste sessão em arquivo YAML
- [ ] Test: load recupera sessão com estado completo
- [ ] Test: histórico preservado entre save/load

---

## Sign-Off

### Team Commitment

**Team Commits To**:
- Entregar 23 story points (features committed)
- Seguir TDD estrito (Red-Green-Refactor)
- Manter Clean Architecture
- Completar artefatos de sprint

### Stakeholder Approval

- [ ] Sprint goals claros e valiosos
- [ ] Features alinhadas com prioridades
- [ ] Capacity estimation razoável
- [ ] Riscos entendidos e aceitáveis

**Aprovado Por**: _______________
**Data**: 2025-12-02

---

## References

- **Tracks**: `specs/bdd/tracks.yml`
- **Features BDD**: `specs/bdd/10_forge_core/`, `specs/bdd/30_plugins/`
- **Handoff BDD**: `docs/handoff_bdd.md`
- **ADR-001**: Runtime + YAML+Git storage
- **ForgeProcess**: `process/delivery/PROCESS.md`
