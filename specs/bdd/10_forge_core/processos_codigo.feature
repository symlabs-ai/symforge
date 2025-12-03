# language: pt
# 10_forge_core/processos_codigo.feature
# Execução versionada de processos como código com rollback seguro

@sdk @ci-fast
Funcionalidade: Executar processo descrito em linguagem natural com rollback seguro
  Para orquestrar qualquer processo (produto, editorial, operações) sem gambiarras
  Como facilitador ou tech lead
  Quero iniciar sessões versionadas, validar artefatos e ter rollback seguro

  Contexto:
    Dado que existe um processo descrito em Markdown/YAML com artefatos obrigatórios
    E o arquivo passou por validação de schema

  Cenário: Iniciar sessão a partir de processo em linguagem natural
    Quando executo "symforge start"
    Então vejo a sessão criada com o fluxo carregado
    E a CLI lista os artefatos obrigatórios para o primeiro passo

  Cenário: Bloquear execução quando artefato obrigatório falta
    Dado que falta um artefato obrigatório para o passo atual
    Quando executo "symforge start"
    Então a sessão fica em AWAITING_INPUT com a lista do que falta
    E a execução só prossegue após o artefato ser criado e "symforge resume" ser usado

  Cenário: Rollback seguro de um passo versionado
    Dado que a sessão avançou e registrou versionamento por passo
    Quando executo "symforge reset <passo>"
    Então o estado retorna ao passo anterior sem perder rastros
    E o histórico mantém o registro do reset

  Cenário: Negar rollback fora de escopo
    Dado que o passo solicitado para reset não possui versão registrada
    Quando executo "symforge reset <passo>"
    Então recebo uma mensagem de erro clara
    E a sessão permanece íntegra e continua no estado anterior
