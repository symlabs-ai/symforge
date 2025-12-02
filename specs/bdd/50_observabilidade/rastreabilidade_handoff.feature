# 50_observabilidade/rastreabilidade_handoff.feature
# Diagramas e handoff com rastreabilidade completa

@observabilidade @ci-int
FUNCIONALIDADE: Gerar diagramas e handoff com rastros completos
  PARA comunicar o fluxo e decisões de forma auditável
  COMO facilitador ou auditor
  QUERO diagramas alinhados ao processo e handoff com histórico/decisões

  CONTEXTO:
    DADO que existe uma sessão em execução com decisões e notas registradas

  CENÁRIO: Gerar diagrama consistente com o PROCESS
    QUANDO executo "symforge diagram process/PROCESS.yml -t flowchart"
    ENTÃO é gerado um diagrama Mermaid sem divergências de nós ou artefatos
    E a saída é salva no path configurado

  CENÁRIO: Exportar handoff com histórico completo
    QUANDO executo "symforge handoff"
    ENTÃO o handoff contém estado atual, decisões, notas e próximos passos
    E o arquivo é salvo no diretório de saída configurado

  CENÁRIO: Alertar inconsistência ao gerar diagrama
    DADO que o PROCESS contém um nó inválido
    QUANDO executo o comando de diagrama
    ENTÃO recebo erro apontando o nó divergente
    E o diagrama não é gerado até corrigir o processo
