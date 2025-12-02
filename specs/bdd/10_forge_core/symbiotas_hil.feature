# 10_forge_core/symbiotas_hil.feature
# Symbiotas 24x7 guiando execução com checkpoints HIL

@core @hil @ci-fast
FUNCIONALIDADE: Conduzir execução com symbiotas e checkpoints HIL
  PARA manter controle humano nos pontos críticos
  COMO facilitador ou PO
  QUERO que symbiotas executem 24x7 mas peçam minha aprovação nos checkpoints

  CONTEXTO:
    DADO que há um passo marcado como HIL no processo
    E o symbiota responsável está configurado

  CENÁRIO: Registrar decisão HIL e liberar o passo
    QUANDO o symbiota apresenta a pergunta do checkpoint
    E eu respondo com uma decisão via "symforge decide"
    ENTÃO a sessão sai de AWAITING_DECISION
    E o fluxo prossegue para o próximo passo
    E a decisão fica registrada com ator e timestamp

  CENÁRIO: Symbiota falha e cai para intervenção humana
    DADO que o symbiota não consegue processar o prompt ou provider falha
    QUANDO executo o passo marcado como HIL
    ENTÃO recebo mensagem de fallback para intervenção humana
    E posso registrar manualmente a decisão para seguir o fluxo
