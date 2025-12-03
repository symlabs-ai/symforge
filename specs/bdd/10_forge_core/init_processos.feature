# language: pt
# 10_forge_core/init_processos.feature
# Inicializar e validar processos técnicos ou não técnicos

@sdk @ci-fast
Funcionalidade: Inicializar projeto com processos técnicos ou não técnicos
  Para começar rápido em qualquer domínio
  Como usuário que não quer montar estrutura manualmente
  Quero rodar init, validar o processo e ter estrutura pronta

  Contexto:
    Dado que escolho um processo disponível na biblioteca (ex.: ForgeProcess, BookForge, OpsForge)

  Cenário: Inicializar projeto e criar estrutura-alvo
    Quando executo "symforge init -p bookforge meu_projeto"
    Então as pastas/arquivos requeridos são criados
    E o processo copiado fica pronto para uso no projeto

  Cenário: Validar PROCESS.yml e templates após init
    Dado o projeto foi inicializado
    Quando executo "symforge validate process/PROCESS.yml --recursive"
    Então a validação passa e lista fases/artefatos esperados

  Cenário: Reportar erro de schema ao validar processo
    Dado editei o PROCESS.yml removendo uma fase obrigatória
    Quando executo "symforge validate process/PROCESS.yml"
    Então recebo erro apontando o campo faltante e sugestão de correção
