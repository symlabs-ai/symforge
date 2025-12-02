Objetivo: gerar slides no Gamma a partir do script do pitch. Não usar tags HTML/XML. Respeitar títulos e bullets abaixo.

# Pitch de Valor — Symforge

Slide 1 — Propósito
- Motor universal e versionável que transforma qualquer processo (produto, editorial, operação, compliance, pesquisa, delivery, etc.) em código executável.
- Symbiotas + checkpoints HIL; orquestração via CLI/TUI; rastreabilidade completa em Git.

Slide 2 — Oportunidade de Mercado
- Processos críticos (técnicos ou de negócio) estão dispersos em wikis/planilhas/automação ad-hoc.
- Falta governança e rastros confiáveis cross-domain; IA e fluxos programáveis exigem colagem manual.
- Risco de inconsistência e revalidação cara a cada mudança.

Slide 3 — Solução e Diferencial
- Processos como código (YAML/Markdown) com templates oficiais para múltiplos domínios.
- Runtime CLI/TUI guia sessões, valida artefatos, gera diagramas e handoffs versionados.
- Symbiotas com front-matter; auto-commit configurável; plugins (send/export/hook/generate) para enviar/transformar artefatos e gerar conteúdos.
- Proteção de loops/inputs para execuções seguras em qualquer processo.
- Benefícios para usuários:
  1) Processos em linguagem natural, sem notações complexas.  
  2) Voltar atrás com rollback seguro a cada passo versionado.  
  3) Symbiotas 24x7 (agentes que aprendem) que só pedem aprovação nos pontos críticos.  
  4) Plugins sem código para e-mail/WhatsApp/exportações, com BYO e marketplace.  
  5) Diagramas automáticos sempre atualizados.  
  6) Composição fácil de novos processos em qualquer área.

Slide 4 — Modelo de Negócio
- Versão free para estudantes e micro (até 10 usuários).
- Assinatura por workspace/projeto com limites de processos/sessões.
- Add-ons para geração de artefatos (ex.: Gamma) e suporte premium.
- Planos para bibliotecas privadas e governança reforçada; BYO plugins e marketplace curado.

Slide 5 — Roadmap e Validação
- V1: ForgeProcess + CLI básica (`init`, `validate`, `diagram`, `start`) com sessões versionadas.
- V2: Runtime completo com TUI opcional, proteção de loops/inputs e auto-commit por step/fase, cobrindo processos não técnicos.
- V3: Observabilidade, handoffs enriquecidos, plugins `produce`.
- V4: Ecossistema multi-processo (BookForge, BizForge, OpsForge...) e dashboard web opcional.
- Métrica inicial: 5 projetos em ≥3 domínios com ≥10 sessões cada; ≥80% das validações sem erro; handoff/handon reabertos; ≥1 geração de artefato via `produce`.

Slide 6 — Encerramento (CTA)
- Experimente `symforge init -p forgeprocess <nome>` ou carregue um processo não técnico (BookForge/OpsForge) e rode a primeira sessão.
- Convite para workspace piloto para medir governança, velocidade e rastreabilidade em qualquer processo.
