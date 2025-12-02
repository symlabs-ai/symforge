# 🌍 Visão do Produto — Symforge

## 1. Intenção Central
Ser o motor universal, versionável e extensível (plugins) que converte qualquer processo (produto, editorial, operações, compliance, pesquisa, delivery, etc.) em código executável, com symbiotas e checkpoints HIL, permitindo orquestração consistente via CLI/TUI e rastreabilidade completa em Git.

---

## 2. Problema de Mercado
Processos críticos — técnicos ou de negócio — estão espalhados entre wikis, planilhas e automações ad-hoc; falta uma forma única, versionada e auditável de definir, executar e evoluir esses fluxos (artefatos, sessões, prompts, handoffs), bem como estender integrações (envios/exports) sem colagens manuais.

---

## 3. Hipótese de Valor
Se oferecermos uma biblioteca de processos como código (YAML/Markdown) — para produto, editorial, operações, governança, etc. — mais um runtime (CLI/TUI) que guia sessões, valida artefatos, gera diagramas, registra decisões/hand-offs versionados e permite plugins de envio/transformação/hook, equipes conseguirão executar e evoluir seus fluxos com governança, reprodutibilidade e evidências de valor, apoiadas por LLMs que entendem linguagem natural.

---

## 4. Público-Alvo e Contexto
Gerentes de Processo, Product Owners, líderes de operações/compliance/qualidade, editores e facilitadores que precisam garantir handoffs confiáveis e governança em qualquer processo (produto, livro, operação, auditoria, pesquisa); equipes que querem testar processos especializados (ForgeProcess, BookForge, BizForge, OpsForge, etc.) sem construir infraestrutura própria.

---

## 5. Paisagem Competitiva
Ferramentas de BPMN/automação (Camunda, Airflow, Zapier/Make), wikis (Notion/Confluence) e copilotos de código (Copilot, Cursor) cobrem partes do problema, mas não integram processos como código cross-domain, symbiotas com front-matter, sessões versionadas e HIL explícito de ponta a ponta.

---

## 6. Diferencial Estratégico
Processos e sessões versionados em Git (auto-commit configurável); prompts com front-matter oficial; execução por fluxo com proteções de loop/inputs; symbiotas especializados; handoff/handon rastreáveis; arquitetura de plugins (send/export/hook/generate) para customizar envios e transformações; tudo operável via CLI/TUI e flexível o bastante para processos técnicos ou de negócio em linguagem natural.

---

## Benefícios-Chave para Usuários
1) Processos em linguagem natural: o fluxo é descrito como se fala com a equipe, sem notações complexas, e o Symforge traduz em execução organizada.  
2) Voltar atrás sem medo: cada passo fica versionado, com histórico de decisões e artefatos, permitindo rollback seguro e recuperação rápida.  
3) Symbiotas 24x7: agentes acompanham o processo o tempo todo, aprendem com o contexto e pedem aprovação apenas nos pontos críticos.  
4) Plugins sem código: integrações (e-mail, WhatsApp, exportações) são criadas ou ajustadas pelo usuário usando modelos simples, sem programar.  
5) Diagramas sob demanda: visões automáticas e sempre atualizadas facilitam entendimento, alinhamento e apresentação para stakeholders.  
6) Composição fácil de novos processos: em qualquer área, combinam-se blocos e templates em linguagem natural para criar e adaptar fluxos rápido, sem depender de ferramentas diferentes ou time técnico.

---

## 7. Métrica de Validação Inicial
5 projetos em ao menos 3 domínios distintos iniciados via `symforge init`, completando ≥10 sessões cada com ≥80% das validações de processo sem erro, handoff/handon reabertos com sucesso e pelo menos 1 geração de artefato via `produce`.

---

## 8. Horizonte de Desenvolvimento
- V1 (imediato): Biblioteca ForgeProcess + CLI básica (`init`, `validate`, `diagram`, `start`) com registros versionados de sessões.
- V2 (próximo trimestre): Runtime completo, proteção de loops/inputs e auto-commit por step/fase, cobrindo também processos não técnicos (ex.: BookForge/OpsForge).
- V3 (seguinte): Observabilidade (logs, métricas), handoffs enriquecidos e arquitetura de plugins `produce` consolidada para múltiplos domínios.
- V4 (expansão): Ecossistema multi-processo (BookForge, BizForge, OpsForge...) e dashboard web opcional para visualização; TUI opcional.

---

## 9. Palavras-Chave e Conceitos
`processos como código`, `symbiotas`, `HIL`, `rastreabilidade`, `versionamento Git`, `CLI/TUI`, `diagramas Mermaid`, `plugins produce`, `handoff/handon`, `governança`, `cross-domain`

---

## 10. Tom Narrativo
Confiante, técnico e direto, com voz de engenharia que inspira ação prática e transparência; oferece controle sem burocracia e celebra experimentação guiada por evidências.
