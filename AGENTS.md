# Symbiotas e Agents — Guia Rápido

## Referências Obrigatórias
- Guia de agentes do ForgeBase: `docs/guides/forgebase_guides/agentes-ia/` (início rápido, descoberta, ecossistema).
- Regras gerais do ForgeBase: Clean/Hex, CLI-first, modo offline, persistência YAML + auto-commit Git.

## Symbiotas de Código/Tests (TDD)
- Seguir camadas (domain → application → infrastructure → adapters) e usar ports/adapters; nada de I/O no domínio.
- Validar via CLI (sem HTTP/TUI no MVP); usar Rich apenas para UX no terminal.
- Respeitar manifesto/permissões de plugins; offline por padrão.
- Consultar: `docs/guides/forgebase_guides/agentes-ia/guia-completo.md` e prompts em `process/symbiotes/tdd_coder/` e `process/symbiotes/test_writer/`.

## Outros Symbiotas
- Para comportamento específico, consulte o prompt do symbiota correspondente em `process/symbiotes/<nome>/prompt.md` e aplique as regras gerais do ForgeBase quando atuarem no runtime ou nos processos.
