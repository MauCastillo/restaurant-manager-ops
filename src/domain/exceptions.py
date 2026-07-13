"""Domain layer exceptions following Clean Architecture principles."""

class DomainException(Exception):
    """Base exception for domain-level errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found in the repository."""
    pass


class DuplicateEntityException(DomainException):
    """Raised when trying to create an entity that already exists (e.g., duplicate cedula or username)."""
    pass


class AuthenticationException(DomainException):
    """Raised when user authentication fails."""
    pass


class AuthorizationException(DomainException):
    """Raised when an authenticated user lacks permissions for an operation."""
    pass


class InvalidEntityStateException(DomainException):
    """Raised when an entity transitions to or is initialized with an invalid state."""
    pass
