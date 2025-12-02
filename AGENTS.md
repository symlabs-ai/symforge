# AGENTS.md - Guia para Agentes de IA neste Projeto

Este projeto utiliza o **ForgeProcess** - uma metodologia estruturada para desenvolvimento de software
gerenciada pelo **Symforge**.

---

## 1. Entendendo o Contexto

### O que é ForgeProcess?

ForgeProcess é um processo de desenvolvimento que combina:
- **MDD** (Market Driven Development) - da hipótese de mercado ao MVP aprovado
- **BDD** (Behavior Driven Development) - do valor aos comportamentos testáveis
- **Execution** - do roadmap ao código testado
- **Delivery** - do código ao produto em produção

### Symforge como Motor de Execução

O projeto é executado via comandos `symforge`:
```bash
symforge status      # Ver estado atual da execução
symforge resume      # Continuar execução
symforge decide      # Registrar decisões HIL
symforge goto        # Reposicionar execução (soft reset)
symforge reset       # Reverter para checkpoint anterior (git reset)
```

---

## 2. Estrutura do Projeto

```text
./
├── .symforge/              # Configuração e estado do Symforge
│   ├── config.yml          # Configuração do projeto
│   └── sessions/           # Estado das sessões de execução
│
├── process/                # Definição do processo (ForgeProcess)
│   ├── PROCESS.yml         # Definição formal do processo
│   ├── mdd/                # Market Driven Development
│   ├── bdd/                # Behavior Driven Development
│   ├── execution/          # Roadmap Planning + TDD
│   ├── delivery/           # Sprint + Review
│   └── symbiotes/          # Agentes especializados do processo
│
├── specs/                  # Especificações geradas
│   ├── mdd/                # Artefatos MDD (visão, hipótese, MVP)
│   └── bdd/                # Features Gherkin, mapeamentos
│
├── project/                # Documentação do projeto
│   └── architecture/       # Decisões arquiteturais (ADRs)
│
├── src/                    # Código fonte
├── tests/                  # Testes
└── docs/                   # Documentação final
```

---

## 3. Regras de Atuação

### 3.1 Respeite o Estado da Sessão

Antes de agir, **sempre verifique** o estado atual:
```bash
symforge status
```

Isso mostra:
- Fase e etapa atual
- Decisões pendentes (HIL)
- Inputs faltantes
- Próximos passos

### 3.2 Siga o Fluxo do Processo

Não pule etapas. O processo tem uma ordem:
1. **MDD**: Hipótese -> Visão -> MVP -> Aprovação HIL
2. **BDD**: Mapeamento -> Features -> Validação HIL
3. **Execution**: Roadmap -> Implementação -> Testes
4. **Delivery**: Deploy -> Review -> Feedback

Se precisar voltar, use `symforge goto` ou `symforge reset`.

### 3.3 Pontos de Decisão Humana (HIL)

Alguns pontos **requerem decisão humana**:
- Aprovação de visão/MVP (MDD)
- Validação de features (BDD)
- Aprovação de roadmap (Execution)
- Aceite de entrega (Delivery)

Quando encontrar um HIL:
1. Apresente as opções claramente
2. Aguarde a decisão do usuário
3. Use `symforge decide <opção>` para registrar

### 3.4 Artefatos e Outputs

Cada etapa produz artefatos específicos:

| Fase | Artefatos Principais |
|------|---------------------|
| MDD | `specs/mdd/HYPOTHESIS.md`, `specs/mdd/VISION.md`, `specs/mdd/MVP.md` |
| BDD | `specs/bdd/*.feature`, `specs/bdd/MAPPING.md` |
| Execution | `project/architecture/`, `src/`, `tests/` |
| Delivery | `docs/`, releases, deploys |

**Sempre crie artefatos nos caminhos esperados** - o Symforge verifica a existência deles.

### 3.5 Checkpoints e Git

O Symforge faz **auto-commit** após cada etapa completada:
- Formato: `[symforge] Step completed: {etapa} - session {id}`
- Isso permite usar `symforge reset` para voltar a qualquer checkpoint

**Não faça commits manuais durante execução** - deixe o Symforge gerenciar.

---

## 4. Trabalhando com Symbiotas

Os symbiotas em `process/symbiotes/` são agentes especializados:

| Symbiota | Função |
|----------|--------|
| `mdd_coach` | Guia o ciclo MDD |
| `bdd_coach` | Guia o ciclo BDD |
| `test_writer` | Escreve testes a partir de features |
| `bill_review` | Revisor técnico de código/arquitetura |
| `jorge_forge` | Auditor de conformidade ao processo |

Quando o Symforge invocar um symbiota, siga as instruções do prompt correspondente.

---

## 5. Comandos Úteis

```bash
# Ver estado atual
symforge status
symforge status -v          # Verbose

# Continuar execução
symforge resume
symforge resume -i          # Modo interativo

# Decisões HIL
symforge decide approved                           # Aprovar
symforge decide rejected                           # Rejeitar
symforge decide needs_revision "motivo aqui"       # Pedir revisão com justificativa

# Notas e contexto
symforge note "mensagem"    # Adicionar nota à sessão
symforge handoff            # Gerar documento de handoff
```

**IMPORTANTE**: Comandos `goto` e `reset` só devem ser usados com solicitação explícita do usuário.

---

## 6. Quando Pedir Ajuda

Se encontrar:
- **Processo parado sem motivo claro**: `symforge status -v` para diagnóstico
- **Artefato faltando**: Verifique o path esperado em `process/PROCESS.yml`
- **Decisão pendente não aparece**: `symforge resume` para reprocessar

---

## 7. Filosofia

> "O processo guia, não aprisiona."

- ForgeProcess é uma estrutura, não uma camisa de força
- Decisões de negócio são humanas (HIL), não automatizáveis
- Cada etapa deve agregar valor visível
- Documentação é código - merece o mesmo cuidado
