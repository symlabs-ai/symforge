# BDD Specs — Symforge

## Estrutura de Pastas
```
specs/bdd/
├── 10_forge_core/           # Núcleo (SDK/engine)
├── 30_plugins/              # Arquitetura de plugins
├── 50_observabilidade/      # Logs, métricas, handoff/diagramas
├── behavior_mapping.md      # Tracks → behaviors
```

## Convenção de Tags
- Domínio (obrigatório): `@sdk`, `@plugins`, `@observabilidade`
- CI (obrigatório): `@ci-fast`, `@ci-int`, `@e2e`
- Capacidades opcionais: `@hil`, `@fallback`, `@observabilidade`
- Categorias opcionais: `@erro`, `@seguranca`, `@performance`

## Execução Seletiva (exemplos)
- Rodar núcleo rápido: `@sdk and @ci-fast`
- Rodar plugins integrações: `@plugins and @ci-int`
- Rodar observabilidade: `@observabilidade`

## Artefatos de Referência
- Mapeamento: `specs/bdd/behavior_mapping.md`
- Templates: `process/bdd/templates/template_feature.md` (estrutura Gherkin)

## Próximos Passos
- Etapa 4: gerar `tracks.yml` com links Track → Feature.
- Etapa 5: gerar step skeletons e hooks para automação.
