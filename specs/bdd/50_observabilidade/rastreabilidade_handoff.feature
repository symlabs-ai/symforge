# language: pt
# 50_observabilidade/rastreabilidade_handoff.feature
# Diagramas e handoff com rastreabilidade completa

@observabilidade @ci-int
Funcionalidade: Gerar diagramas e handoff com rastros completos
  PARA comunicar o fluxo e decisões de forma auditável
  COMO facilitador ou auditor
  QUERO diagramas alinhados ao processo e handoff com histórico/decisões

  Contexto:
    Dado que existe uma sessão em execução com decisões e notas registradas

  Cenário: Gerar diagrama consistente com o PROCESS
    Quando executo "symforge diagram process/PROCESS.yml -t flowchart"
    Então é gerado um diagrama Mermaid sem divergências de nós ou artefatos
    E a saída é salva no path configurado

  Cenário: Exportar handoff com histórico completo
    Quando executo "symforge handoff"
    Então o handoff contém estado atual, decisões, notas e próximos passos
    E o arquivo é salvo no diretório de saída configurado

  Cenário: Alertar inconsistência ao gerar diagrama
    Dado que o PROCESS contém um nó inválido
    Quando executo o comando de diagrama
    Então recebo erro apontando o nó divergente
    E o diagrama não é gerado até corrigir o processo
