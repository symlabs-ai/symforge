# 10_forge_core/init_processos.feature
# Inicializar e validar processos técnicos ou não técnicos

@core @ci-fast
FUNCIONALIDADE: Inicializar projeto com processos técnicos ou não técnicos
  PARA começar rápido em qualquer domínio
  COMO usuário que não quer montar estrutura manualmente
  QUERO rodar init, validar o processo e ter estrutura pronta

  CONTEXTO:
    DADO que escolho um processo disponível na biblioteca (ex.: ForgeProcess, BookForge, OpsForge)

  CENÁRIO: Inicializar projeto e criar estrutura-alvo
    QUANDO executo "symforge init -p bookforge meu_projeto"
    ENTÃO as pastas/arquivos requeridos são criados
    E o processo copiado fica pronto para uso no projeto

  CENÁRIO: Validar PROCESS.yml e templates após init
    DADO que o projeto foi inicializado
    QUANDO executo "symforge validate process/PROCESS.yml --recursive"
    ENTÃO a validação passa e lista fases/artefatos esperados

  CENÁRIO: Reportar erro de schema ao validar processo
    DADO que editei o PROCESS.yml removendo uma fase obrigatória
    QUANDO executo "symforge validate process/PROCESS.yml"
    ENTÃO recebo erro apontando o campo faltante e sugestão de correção
