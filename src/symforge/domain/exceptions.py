"""
Exceções de domínio específicas para o Symforge.

Seguindo ForgeBase Rules: nunca usar Exception genérico.
Cada exceção representa uma violação específica de regra de negócio.
"""


class DomainException(Exception):
    """Base para todas as exceções de domínio."""

    pass


class StepNotFoundError(DomainException):
    """Passo não encontrado no histórico da sessão."""

    def __init__(self, step_id: str):
        self.step_id = step_id
        super().__init__(f"Passo '{step_id}' sem versionamento para reset")


class NoPendingDecisionError(DomainException):
    """Nenhuma decisão pendente para registrar."""

    def __init__(self):
        super().__init__("Sem decisão pendente")


class SessionNotFoundError(DomainException):
    """Sessão não encontrada no repositório."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Sessão '{session_id}' não encontrada")


class InvalidManifestError(DomainException):
    """Manifesto de plugin inválido."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Manifesto inválido: {reason}")


class PluginNotFoundError(DomainException):
    """Plugin não instalado."""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        super().__init__(f"Plugin '{plugin_id}' não instalado")


class PluginTypeError(DomainException):
    """Tipo de plugin incompatível com a operação."""

    def __init__(self, plugin_id: str, expected_type: str, actual_type: str):
        self.plugin_id = plugin_id
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"Plugin '{plugin_id}' é do tipo '{actual_type}', esperado '{expected_type}'"
        )


class NetworkPermissionDeniedError(DomainException):
    """Permissão de rede negada em modo offline."""

    def __init__(self):
        super().__init__("Permissão de network não é permitida em modo offline")
