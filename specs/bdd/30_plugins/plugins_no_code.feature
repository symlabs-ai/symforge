# language: pt
# 30_plugins/plugins_no_code.feature
# Plugins no-code para envios e exports

@plugins @ci-int
Funcionalidade: Instalar e usar plugins no-code de envio/export
  PARA enviar e transformar artefatos sem programar
  COMO usuário de negócio ou facilitador
  QUERO instalar plugins, listar permissões e executar envios/exports

  Contexto:
    Dado que tenho um processo em execução com artefatos gerados

  Cenário: Instalar e listar plugin no-code
    Quando adiciono o plugin "send_email" ao projeto
    E executo "symforge plugin list"
    Então vejo o plugin instalado com tipo "send" e permissões declaradas

  Cenário: Enviar artefato por e-mail usando plugin
    Dado que o plugin "send_email" está instalado
    E defini destinatário e assunto
    Quando executo o envio com o artefato atual
    Então o log registra sucesso e o destinatário recebe a mensagem

  Cenário: Exportar arquivo para CSV via plugin
    Dado que o plugin "export_csv" está instalado
    Quando executo o export do artefato Markdown
    Então o arquivo CSV é gerado no path configurado
    E a CLI confirma o sucesso

  Cenário: Recusar plugin com manifesto inválido
    Dado que um plugin não declara permissões ou tem manifesto incorreto
    Quando tento instalá-lo
    Então o Symforge bloqueia a instalação com mensagem clara de erro
