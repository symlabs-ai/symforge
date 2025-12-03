# Sprint 2 - Planning

**Project**: Symforge
**Sprint Number**: 2
**Sprint Duration**: 2025-12-02 - 2025-12-16 (2 semanas)
**Planning Date**: 2025-12-02
**Team**: Agent Coders (Claude Code primary)
**Stakeholder**: Palhano

---

## Sprint Overview

### Sprint Goals

**Primary Goal**: Completar stretch goals da Sprint 1 (Plugins e Observabilidade) e melhorar cobertura de testes.

**Secondary Goals**:
- Criar ADR-010 para pré-validação de stakeholder
- Adotar commits granulares por feature
- Aumentar cobertura de CLI para >= 80%

**Success Criteria**:
- [ ] Plugins no-code funcionais (send/export/hook/generate)
- [ ] Comandos diagram e handoff implementados
- [ ] Cobertura global >= 85%
- [ ] ADR-010 documentado

---

## Capacity Planning

### Velocity Baseline

**Sprint 1 Velocity**: 23 pts/sessão (outlier - arquitetura pronta)
**Adjusted Velocity**: 8-10 pts/sessão (estimativa conservadora)

### Capacity Calculation

**Sessions Available**: 4 sessões
**Projected Capacity**: 4 sessões × 8 pts/sessão = **32 story points**
**Buffer**: ±20% para unknowns
**Final Capacity Range**: 26-38 story points

---

## Features Selected

### Committed Features

| Feature ID | Feature Name | Story Points | Priority | Track |
|------------|--------------|--------------|----------|-------|
| F05 | Plugins no-code (send/export/hook/generate) | 8 pts | HIGH | value_plugins_no_code |
| F06 | Observabilidade (diagrama/handoff) | 5 pts | HIGH | value_observabilidade_handoff |
| F07 | Aumentar cobertura CLI | 3 pts | HIGH | QUALITY |
| F08 | ADR-010 Pre-Stakeholder Validation | 2 pts | MEDIUM | PROCESS |
| **Total Committed** | | **18 pts** | | |

### Stretch Goals

| Feature ID | Feature Name | Story Points | Priority | Track |
|------------|--------------|--------------|----------|-------|
| F09 | Templates review/retro em /process | 2 pts | LOW | PROCESS |
| F10 | Testes e2e com click.testing | 5 pts | LOW | QUALITY |

---

## Dependencies & Prerequisites

### Technical Dependencies

- [x] **Sprint 1 Completa**: Core SDK funcional
- [x] **PluginManager**: Já implementado com 28 testes
- [x] **ObservabilityUseCases**: Já implementado

### Process Dependencies

- [x] **Handoff Sprint 1**: Documentado em docs/handoff_sprint1.md
- [x] **ADR-001 Aceito**: Runtime e plugins definidos

---

## Risks & Mitigation

### Risk 1: Complexidade de Plugins

- **Probability**: Medium
- **Impact**: Medium
- **Description**: Plugins podem ter edge cases de permissões
- **Mitigation**: TDD estrito, testar cenários BDD existentes
- **Contingency**: Simplificar permissões para MVP

### Risk 2: Mermaid Diagram Generation

- **Probability**: Low
- **Impact**: Low
- **Description**: Parsing de PROCESS.yml pode ter casos especiais
- **Mitigation**: Validar schema antes de gerar
- **Contingency**: Diagrama básico sem validação completa

**Overall Risk Level**: Low-Medium
**Confidence Level**: High

---

## Definition of Done

### Feature-Level DoD

Uma feature é DONE quando:

- [x] Cenários BDD passando
- [x] Testes unitários TDD cobrindo casos de borda
- [x] Coverage >= 80% para o módulo
- [x] Lint e type check limpos
- [x] Clean Architecture mantida
- [x] Demo funcional via CLI
- [x] Commit granular criado

### Sprint-Level DoD

- [ ] 100% das features committed implementadas
- [ ] Todos cenários BDD passando
- [ ] Coverage >= 85% global
- [ ] forge_coder review >= 8/10
- [ ] Jorge review >= 8/10
- [ ] Documentação atualizada

---

## Feature Breakdown

### F05: Plugins no-code (8 pts)

**Track**: value_plugins_no_code
**BDD**: `specs/bdd/30_plugins/plugins_no_code.feature`

**Acceptance Criteria**:
- [ ] `symforge plugin add <repo>` instala plugin
- [ ] `symforge plugin list` mostra plugins com tipos e permissões
- [ ] `symforge plugin send <id> <payload>` executa envio
- [ ] `symforge plugin export <id> <input>` executa export
- [ ] `symforge plugin hook <id> <context>` executa hook
- [ ] `symforge plugin generate <id> <payload>` executa geração
- [ ] Bloqueia manifesto inválido
- [ ] Bloqueia network em modo offline

**TDD Tasks**:
- [ ] Test: add instala plugin em plugins/
- [ ] Test: list retorna plugins com metadata
- [ ] Test: send executa plugin tipo send
- [ ] Test: export executa plugin tipo export
- [ ] Test: hook executa plugin tipo hook
- [ ] Test: generate executa plugin tipo generate
- [ ] Test: manifesto inválido levanta InvalidManifestError
- [ ] Test: network offline levanta NetworkPermissionDeniedError

---

### F06: Observabilidade (5 pts)

**Track**: value_observabilidade_handoff
**BDD**: `specs/bdd/50_observabilidade/rastreabilidade_handoff.feature`

**Acceptance Criteria**:
- [ ] `symforge diagram <process.yml> -t flowchart` gera Mermaid
- [ ] `symforge handoff` exporta estado + decisões + notas
- [ ] Erro claro para nó inválido no processo

**TDD Tasks**:
- [ ] Test: diagram gera output Mermaid válido
- [ ] Test: diagram detecta nó inválido
- [ ] Test: handoff inclui estado atual
- [ ] Test: handoff inclui decisões
- [ ] Test: handoff inclui próximos passos

---

### F07: Aumentar Cobertura CLI (3 pts)

**Track**: QUALITY

**Acceptance Criteria**:
- [ ] `plugins_cli.py` >= 80% (atual: 61%)
- [ ] `cli.py` >= 80% (atual: 68%)

**TDD Tasks**:
- [ ] Test: plugin add com repo válido
- [ ] Test: plugin add com repo inválido
- [ ] Test: plugin send com payload
- [ ] Test: plugin export com input/output
- [ ] Test: comandos CLI principais com click.testing

---

### F08: ADR-010 Pre-Stakeholder Validation (2 pts)

**Track**: PROCESS

**Acceptance Criteria**:
- [ ] ADR-010 documentado em specs/adr/
- [ ] Checklist de pré-validação definido
- [ ] Processo de smoke test antes de demo

**Tasks**:
- [ ] Escrever ADR-010 com contexto e decisão
- [ ] Definir checklist (testes, lint, demo)
- [ ] Integrar ao REVIEW_PROCESS.md

---

## Sprint Timeline

| Date | Milestone | Owner |
|------|-----------|-------|
| 2025-12-02 | Sprint 2 Planning Complete | Team |
| 2025-12-09 | Mid-Sprint Checkpoint | Team |
| 2025-12-13 | Feature Freeze | Team |
| 2025-12-14 | forge_coder review (Day 1) | forge_coder |
| 2025-12-15 | Jorge review (Day 2) | Jorge the Forge |
| 2025-12-16 | Sprint Review & Retro (Day 3) | Stakeholder |

---

## Sign-Off

### Team Commitment

**Team Commits To**:
- Entregar 18 story points (features committed)
- Seguir TDD estrito (Red-Green-Refactor)
- Commits granulares por feature
- Manter Clean Architecture

### Stakeholder Approval

- [ ] Sprint goals claros e valiosos
- [ ] Features alinhadas com prioridades
- [ ] Capacity estimation razoável
- [ ] Riscos entendidos e aceitáveis

**Aprovado Por**: _______________
**Data**: 2025-12-02

---

## References

- **Handoff Sprint 1**: `docs/handoff_sprint1.md`
- **Tracks**: `specs/bdd/tracks.yml`
- **Features BDD**: `specs/bdd/30_plugins/`, `specs/bdd/50_observabilidade/`
- **ADR-001**: Runtime + YAML+Git + Plugins
- **ForgeProcess**: `process/delivery/PROCESS.md`
