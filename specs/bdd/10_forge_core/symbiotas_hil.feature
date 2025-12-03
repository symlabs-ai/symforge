# language: pt
# 10_forge_core/symbiotas_hil.feature
# Symbiotas 24x7 guiando execução com checkpoints HIL

@sdk @hil @ci-fast
Funcionalidade: Conduzir execução com symbiotas e checkpoints HIL
  Para manter controle humano nos pontos críticos
  Como facilitador ou PO
  Quero que symbiotas executem 24x7 mas peçam minha aprovação nos checkpoints

  Contexto:
    Dado que há um passo marcado como HIL no processo
    E o symbiota responsável está configurado

  Cenário: Registrar decisão HIL e liberar o passo
    Quando o symbiota apresenta a pergunta do checkpoint
    E eu respondo com uma decisão via "symforge decide"
    Então a sessão sai de AWAITING_DECISION
    E o fluxo prossegue para o próximo passo
    E a decisão fica registrada com ator e timestamp

  Cenário: Symbiota falha e cai para intervenção humana
    Dado que o symbiota não consegue processar o prompt ou provider falha
    Quando executo o passo marcado como HIL
    Então recebo mensagem de fallback para intervenção humana
    E posso registrar manualmente a decisão para seguir o fluxo
