# ADR-010 — Pre-Stakeholder Validation Checklist

## Status
Aceito

## Contexto

Durante a Sprint 1, identificamos a necessidade de um processo formal de validação antes de apresentar incrementos ao stakeholder. Sem esse processo:

- Há risco de apresentar features com bugs ou incompletas
- Demos podem falhar durante a apresentação
- Stakeholder pode perder confiança no time
- Retrabalho e frustração aumentam

O processo de Review & Feedback do ForgeProcess define 3 dias:
1. **Dia 1**: bill-review (técnico)
2. **Dia 2**: Jorge the Forge (processo)
3. **Dia 3**: Stakeholder Review

Este ADR formaliza um checklist de pré-validação a ser executado **antes** da apresentação ao stakeholder (entre Dia 2 e Dia 3).

## Decisão

### 1. Pre-Stakeholder Validation Checklist

Antes de apresentar ao stakeholder, o time deve verificar:

#### 1.1 Qualidade Técnica
- [ ] Todos os testes passando (`pytest tests/`)
- [ ] Cobertura >= 80% (`pytest --cov`)
- [ ] Lint limpo (`ruff check src/ tests/`)
- [ ] Type check limpo (`mypy src/`)
- [ ] Nenhum TODO crítico no código

#### 1.2 Features Funcionais
- [ ] Cada feature committed funciona via CLI
- [ ] Demo script preparado para cada feature
- [ ] Smoke test executado em ambiente limpo
- [ ] Edge cases conhecidos documentados

#### 1.3 Documentação
- [ ] README atualizado (se necessário)
- [ ] Handoff da sprint escrito
- [ ] ADRs relevantes atualizados
- [ ] Changelog/release notes preparados

#### 1.4 Reviews Completados
- [ ] forge_coder review >= 8/10
- [ ] Jorge process review aprovado
- [ ] Issues de review corrigidos

### 2. Smoke Test Protocol

Antes da demo, executar em ambiente limpo:

```bash
# 1. Setup limpo
rm -rf /tmp/demo_workspace
mkdir /tmp/demo_workspace && cd /tmp/demo_workspace

# 2. Testar comandos core
symforge init -p forgeprocess demo_project
symforge validate demo_project/process/PROCESS.yml
symforge start --process demo --workspace .
symforge status <session_id>

# 3. Testar plugins (se aplicável)
symforge plugin list
symforge plugin add <test_plugin_path>

# 4. Verificar outputs
ls -la .symforge/sessions/
```

### 3. Demo Script Template

Cada feature deve ter um demo script documentado:

```markdown
## Demo: [Feature Name]

### Setup
1. Comandos de preparação

### Demonstração
1. Passo a passo da demo
2. O que mostrar ao stakeholder
3. Pontos importantes a destacar

### Rollback (se der errado)
1. Como recuperar se a demo falhar
```

### 4. Integração ao Workflow

O checklist deve ser executado:
- Após o Jorge process review (Dia 2)
- Antes da Sprint Review (Dia 3)
- Por qualquer membro do time
- Com resultados documentados em `progress.md`

## Consequências

### Positivas
- Reduz risco de demos falharem
- Aumenta confiança do stakeholder
- Cria padrão repetível de qualidade
- Documenta o que foi validado

### Negativas
- Adiciona tempo ao processo (estimativa: 30-60 min)
- Requer disciplina do time
- Pode atrasar apresentação se issues forem encontrados

### Mitigação
- Automatizar partes do checklist via CI/CD
- Criar script `symforge validate-release` futuro
- Integrar checklist ao `progress.md` template

## Alternativas Consideradas

### 1. Checklist informal
- **Rejeitado**: Não garante consistência entre sprints

### 2. Validação apenas técnica
- **Rejeitado**: Ignora aspectos de UX e demo

### 3. Automação completa
- **Adiado**: Requer investimento em tooling; checklist manual é suficiente para MVP

## Referências

- `process/delivery/review/REVIEW_PROCESS.md`
- Jorge the Forge process review (Sprint 1)
- ForgeProcess delivery guidelines
