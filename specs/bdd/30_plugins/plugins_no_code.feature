# 30_plugins/plugins_no_code.feature
# Plugins no-code para envios e exports

@plugins @ci-int
FUNCIONALIDADE: Instalar e usar plugins no-code de envio/export
  PARA enviar e transformar artefatos sem programar
  COMO usuário de negócio ou facilitador
  QUERO instalar plugins, listar permissões e executar envios/exports

  CONTEXTO:
    DADO que tenho um processo em execução com artefatos gerados

  CENÁRIO: Instalar e listar plugin no-code
    QUANDO adiciono o plugin "send_email" ao projeto
    E executo "symforge plugin list"
    ENTÃO vejo o plugin instalado com tipo "send" e permissões declaradas

  CENÁRIO: Enviar artefato por e-mail usando plugin
    DADO que o plugin "send_email" está instalado
    E defini destinatário e assunto
    QUANDO executo o envio com o artefato atual
    ENTÃO o log registra sucesso e o destinatário recebe a mensagem

  CENÁRIO: Exportar arquivo para CSV via plugin
    DADO que o plugin "export_csv" está instalado
    QUANDO executo o export do artefato Markdown
    ENTÃO o arquivo CSV é gerado no path configurado
    E a CLI confirma o sucesso

  CENÁRIO: Recusar plugin com manifesto inválido
    DADO que um plugin não declara permissões ou tem manifesto incorreto
    QUANDO tento instalá-lo
    ENTÃO o Symforge bloqueia a instalação com mensagem clara de erro
