# Mapeamento de Comportamentos — Symforge

## ValueTrack: Processos como código cross-domain com rollback seguro

**Tipo:** VALUE
**Domínio:** 10_forge_core / 50_observabilidade

### Comportamentos Identificados
1. **Carregar processo descrito em linguagem natural/Markdown e iniciar sessão**
   - Ação: Usuário escreve processo (YAML/Markdown) e roda `symforge start`.
   - Resultado esperado: Sessão criada, passos carregados, artefatos esperados listados.
   - Critério: CLI/TUI mostra sessão ativa com flow carregado; artefatos obrigatórios exibidos.
   - Cenário BDD: Iniciar sessão a partir de processo descrito em linguagem natural.

2. **Executar fluxo com versionamento e rollback**
   - Ação: Avançar passos com registros automáticos (auto-commit opcional).
   - Resultado esperado: Cada passo gera rastro versionado; é possível voltar atrás.
   - Critério: Histórico e commit por passo/fase; `reset` retorna estado anterior sem perda de rastros.
   - Cenário BDD: Rollback seguro de passo/fase mantendo rastro.

### Casos de Erro
1. **Processo inválido ou artefato faltando**
   - Condição: YAML/Markdown fora do schema ou artefato obrigatório ausente.
   - Tratamento esperado: Bloqueio (AWAITING_INPUT) indicando o que falta.
   - Cenário BDD: Bloqueio por artefato obrigatório ausente.

2. **Rollback fora de escopo**
   - Condição: Tentar resetar passo não versionado.
   - Tratamento esperado: Erro claro sem corromper estado.
   - Cenário BDD: Negar rollback inválido mantendo integridade da sessão.

---

## ValueTrack: Execução guiada por symbiotas 24x7 com HIL

**Tipo:** SUPPORT
**Domínio:** 10_forge_core / 50_observabilidade

### Comportamentos Identificados
1. **Symbiota conduz passo e registra decisão HIL**
   - Ação: Symbiota pergunta, recebe resposta humana e registra decisão.
   - Resultado esperado: Decisão armazenada e passo prossegue só após aprovação.
   - Critério: `pending_decision` limpo; registro de ator/timestamp; avanço do fluxo.
   - Cenário BDD: Registrar decisão HIL e liberar passo.

2. **Symbiota opera em modo 24x7 com checkpoints**
   - Ação: Sessão continua com prompts automáticos e pausa em checkpoints HIL.
   - Resultado esperado: Passos automáticos executam; bloqueios só onde marcado HIL.
   - Critério: Estados PROCESSING/RUNNING alternam; HIL obriga intervenção.
   - Cenário BDD: Pausa em checkpoint HIL e retomada após aprovação.

### Casos de Erro
1. **Decisão não registrada**
   - Condição: Usuário não fornece `decide`.
   - Tratamento esperado: Sessão permanece em AWAITING_DECISION com instrução clara.
   - Cenário BDD: Manter bloqueio até decisão explícita.

2. **Prompt/symbiota indisponível**
   - Condição: Falha ao carregar prompt ou provider.
   - Tratamento esperado: Mensagem clara e opção de fallback HIL/manual.
   - Cenário BDD: Fallback para intervenção humana quando symbiota falha.

---

## ValueTrack: Plugins no-code para envios/exports (send/export/hook/generate)

**Tipo:** VALUE
**Domínio:** 30_plugins

### Comportamentos Identificados
1. **Instalar e listar plugin no-code**
   - Ação: Usuário adiciona plugin (ex.: send_email) e verifica instalação.
   - Resultado esperado: Plugin aparece em `plugin list` com manifesto válido.
   - Critério: CLI/TUI exibe plugin, tipo e permissões.
   - Cenário BDD: Instalar plugin no-code e listar manifesto.

2. **Enviar artefato via plugin de envio**
   - Ação: Executar envio (e-mail/WhatsApp) com payload simples.
   - Resultado esperado: Mensagem enviada; log registra status e destino.
   - Critério: Saída de sucesso e log do envio; erro claro se falhar.
   - Cenário BDD: Enviar artefato com plugin de envio.

3. **Exportar arquivo com plugin de transformação**
   - Ação: Converter Markdown/YAML para CSV/Excel com plugin de export.
   - Resultado esperado: Arquivo gerado no formato escolhido.
   - Critério: Saída presente no path definido; mensagem de sucesso.
   - Cenário BDD: Exportar artefato para CSV/Excel via plugin.

### Casos de Erro
1. **Permissão ou manifesto inválido**
   - Condição: Plugin sem permissões declaradas ou manifesto incorreto.
   - Tratamento esperado: Bloqueio de execução com erro descritivo.
   - Cenário BDD: Recusar plugin com manifesto/permissão inválida.

2. **Falha de rede/execução no plugin**
   - Condição: Timeout ou falha de dependência.
   - Tratamento esperado: Erro claro, sem corromper sessão; tentativa manual possível.
   - Cenário BDD: Tratar falha de plugin e manter sessão íntegra.

---

## ValueTrack: Biblioteca multi-processo e composição em linguagem natural

**Tipo:** SUPPORT
**Domínio:** 10_forge_core

### Comportamentos Identificados
1. **Inicializar projeto com processo técnico ou não técnico**
   - Ação: Rodar `symforge init -p <processo>` (ex.: ForgeProcess, BookForge, OpsForge).
   - Resultado esperado: Estrutura-alvo criada, processos copiados e prontos para uso.
   - Critério: Pastas/arquivos requeridos presentes; mensagem de sucesso.
   - Cenário BDD: Init de projeto com processo selecionado.

2. **Compor novo processo em linguagem natural reusando templates**
   - Ação: Criar/editar Markdown do processo com blocos/template e gerar YAML.
   - Resultado esperado: PROCESS.yml válido e sincronizado com Markdown.
   - Critério: Validação `symforge validate` passa; diagramas gerados.
   - Cenário BDD: Criar processo em linguagem natural e validar YAML.

### Casos de Erro
1. **Validação de processo falha**
   - Condição: PROCESS.yml fora do schema ou sem narrativa/fases.
   - Tratamento esperado: Erros apontam campo e correção.
   - Cenário BDD: Reportar erro de schema ao validar processo.

2. **Template inconsistente**
   - Condição: Blocos faltando ou mapeamento artefato incorreto.
   - Tratamento esperado: Mensagem de ajuste e bloqueio de geração.
   - Cenário BDD: Rejeitar template incompleto ou com artefatos inválidos.

---

## ValueTrack: Rastreabilidade, observabilidade e diagramas automáticos

**Tipo:** SUPPORT
**Domínio:** 50_observabilidade

### Comportamentos Identificados
1. **Gerar diagramas e inspeções a partir do processo**
   - Ação: Executar `symforge diagram` ou inspeção.
   - Resultado esperado: Diagramas Mermaid/summary alinhados ao fluxo atual.
   - Critério: Arquivos gerados, sem divergência de nós/artefatos.
   - Cenário BDD: Gerar diagrama atualizado do processo.

2. **Registrar histórico/decisões e exports de handoff**
   - Ação: Executar sessão; exportar handoff com histórico e decisões.
   - Resultado esperado: Handoff contém estado, decisões, próximos passos.
   - Critério: Arquivo de handoff presente e completo; decisions/notes salvos.
   - Cenário BDD: Exportar handoff com rastros completos.

### Casos de Erro
1. **Diagrama inconsistente com PROCESS**
   - Condição: Nó faltando ou tipo inválido.
   - Tratamento esperado: Erro apontando nó divergente.
   - Cenário BDD: Reportar divergência ao gerar diagrama.

2. **Handoff incompleto**
   - Condição: Faltam decisões/notas no export.
   - Tratamento esperado: Mensagem clara e instrução de completar sessão.
   - Cenário BDD: Alertar ausência de registros antes de exportar handoff.
