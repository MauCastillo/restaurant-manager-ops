from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.user import User


class AuthServicePort(ABC):
    """Primary inbound port for security user account management and authentication."""

    @abstractmethod
    def register_user(self, username: str, email: str, password: str, role: str = "operator") -> User:
        """Register a new system user with hashed password."""
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials and return User if valid."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        pass

    @abstractmethod
    def list_users(self) -> List[User]:
        """List all registered system users."""
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """Remove a system user account."""
        pass
