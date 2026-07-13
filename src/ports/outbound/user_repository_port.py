from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.user import User


class UserRepositoryPort(ABC):
    """Outbound port interface for User persistence."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Create or update a User entity."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find a User by ID."""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Find a User by unique username."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a User by unique email."""
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        """List all registered system users."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a User by ID."""
        pass
