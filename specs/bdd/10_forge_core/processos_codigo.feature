# 10_forge_core/processos_codigo.feature
# Execução versionada de processos como código com rollback seguro

@core @ci-fast
FUNCIONALIDADE: Executar processo descrito em linguagem natural com rollback seguro
  PARA orquestrar qualquer processo (produto, editorial, operações) sem gambiarras
  COMO facilitador ou tech lead
  QUERO iniciar sessões versionadas, validar artefatos e ter rollback seguro

  CONTEXTO:
    DADO que existe um processo descrito em Markdown/YAML com artefatos obrigatórios
    E o arquivo passou por validação de schema

  CENÁRIO: Iniciar sessão a partir de processo em linguagem natural
    QUANDO executo "symforge start"
    ENTÃO vejo a sessão criada com o fluxo carregado
    E a CLI lista os artefatos obrigatórios para o primeiro passo

  CENÁRIO: Bloquear execução quando artefato obrigatório falta
    DADO que falta um artefato obrigatório para o passo atual
    QUANDO executo "symforge start"
    ENTÃO a sessão fica em AWAITING_INPUT com a lista do que falta
    E a execução só prossegue após o artefato ser criado e "symforge resume" ser usado

  CENÁRIO: Rollback seguro de um passo versionado
    DADO que a sessão avançou e registrou versionamento por passo
    QUANDO executo "symforge reset <passo>"
    ENTÃO o estado retorna ao passo anterior sem perder rastros
    E o histórico mantém o registro do reset

  CENÁRIO: Negar rollback fora de escopo
    DADO que o passo solicitado para reset não possui versão registrada
    QUANDO executo "symforge reset <passo>"
    ENTÃO recebo uma mensagem de erro clara
    E a sessão permanece íntegra e continua no estado anterior
