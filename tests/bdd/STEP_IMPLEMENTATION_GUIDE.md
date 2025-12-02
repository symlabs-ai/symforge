# Guia de implementação dos steps BDD (contrato, sem código agora)

## test_processos_codigo_steps.py
- Preparar processo válido em Markdown/YAML e rodar validação de schema.
- Executar `symforge start` e verificar: sessão criada, flow carregado, artefatos obrigatórios listados.
- Simular falta de artefato: esperar AWAITING_INPUT, exigir `symforge resume` após criação.
- Avançar passos com versionamento e testar `symforge reset <passo>` (rollback mantém rastro).
- Negar rollback fora de escopo: erro claro e sessão íntegra.

## test_symbiotas_hil_steps.py
- Configurar passo marcado como HIL e symbiota disponível.
- Executar checkpoint: `symforge decide` registra decisão, sai de AWAITING_DECISION, avança fluxo com ator/timestamp.
- Falha de symbiota/provider: emitir fallback e permitir decisão manual.

## test_plugins_no_code_steps.py
- Contexto: processo em execução com artefatos gerados.
- Instalar plugin send_email; `symforge plugin list` mostra tipo/permissões.
- Enviar artefato via plugin (e-mail/WhatsApp): log de sucesso e entrega simulada/mocked.
- Exportar Markdown → CSV (plugin export); confirmar arquivo no path e sucesso na CLI.
- Manifesto inválido: instalação bloqueada com erro descritivo.

## test_init_processos_steps.py
- Rodar `symforge init -p <processo>` (ex.: bookforge) e verificar estrutura-alvo criada.
- Validar `process/PROCESS.yml --recursive` e listar fases/artefatos esperados.
- Processo inválido (fase removida): erro de schema apontando campo faltante.

## test_rastreabilidade_handoff_steps.py
- Sessão com decisões/notas registradas (fixtures).
- Gerar diagrama: `symforge diagram ...` cria Mermaid sem divergências e salva no path.
- Exportar handoff: contém estado, decisões, notas, próximos passos; arquivo salvo no diretório esperado.
- PROCESS com nó inválido: comando de diagrama falha apontando nó divergente e não gera arquivo.
