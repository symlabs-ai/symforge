# ADR-001 — Runtime CLI, Persistência YAML + Git e Plugins no-code (ForgeBase)

## Status
Proposto (MVP)

## Contexto
- Stack: Python 3.12, CLI-first (sem TUI/HTTP no MVP), modo offline por padrão.
- ForgeBase define camadas Clean/Hex: domain → application → infrastructure → adapters.
- Persistência atual é local em YAML; rastreabilidade crítica pede auto-commit Git por step/fase.
- Plugins no-code serão instalados via repositório Git e rodarão offline a partir de arquivos `.py` locais.
- Observabilidade e exceções devem seguir ForgeBase (log/métricas/erros específicos).

## Decisão
1) Arquitetura em camadas (ForgeBase)
- CLI (adapter Rich) → Application/UseCases → Ports → Adapters/Plugins → Infrastructure (FS/Git).
- Domínio permanece puro (sem I/O); Adapters só via Ports; infra encapsula FS/YAML/Git.

2) Persistência e rastreabilidade
- Sessões/estados em `.symforge/sessions/<id>/` (YAML).
- Auto-commit Git opcional por step/fase; inclui sessões, configs e código alterado no ciclo.

3) Plugins no-code (instalação e execução)
- Instalação: `symforge plugin add <git-url>` copia repositório para `plugins/<id>/`.
- Manifesto obrigatório em `plugins/<id>/plugin.yml`:
  - `id`, `name`, `version`, `type: send|export|hook|generate`
  - `entrypoint`: `module:function` (callable Python no plugin)
  - `permissions`: `network` (default false), `fs` (paths permitidos), `env` (variáveis permitidas)
  - `inputs`/`outputs`: descrição/schema simples (ex.: formato, mime, paths)
- Execução: módulo carregado/importado via adapter de plugin; modo offline (network false) por padrão; respeita permissões do manifesto.

4) Observabilidade
- UseCases e Adapters instrumentados com logging/métricas ForgeBase; Rich só para UX da CLI.
- Exceções de domínio/específicas (sem Exception genérico).

5) CLI-first
- Validar usecases/plug-ins via CLI; nada de HTTP/TUI antes de cobrir BDD/CLI.

### Diagrama textual (fluxo runtime)
```
CLI (Rich) ──> Application (UseCases) ──> Ports ──> Adapters
                                           ├─ Plugins (send/export/hook/generate)
                                           └─ Infra (FS YAML + Git auto-commit)
```

## Consequências
- Separação clara de camadas; facilita testes/BDD e evita acoplamento.
- Plugins operam offline com contrato explícito (manifesto/permissões); fácil distribuir via Git.
- Auto-commit por step melhora rastreabilidade, mas exige cuidado com secrets (gitignore/filters).
- CLI-first mantém ciclo rápido; TUI/HTTP entram depois.
- Necessário criar adapters/repositórios para FS/YAML/Git e gerenciador de plugins conforme o manifesto.
