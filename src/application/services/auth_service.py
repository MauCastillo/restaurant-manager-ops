from typing import List, Optional
from src.domain.models.user import User
from src.domain.exceptions import DuplicateEntityException, AuthenticationException, EntityNotFoundException
from src.ports.inbound.auth_service_port import AuthServicePort
from src.ports.outbound.user_repository_port import UserRepositoryPort
from src.adapters.outbound.security.password_hasher import PasswordHasher


class AuthService(AuthServicePort):
    """Implementation of AuthServicePort for managing security user accounts."""

    def __init__(self, user_repo: UserRepositoryPort, hasher: PasswordHasher):
        self.user_repo = user_repo
        self.hasher = hasher

    def register_user(self, username: str, email: str, password: str, role: str = "operator") -> User:
        existing = self.user_repo.find_by_username(username)
        if existing:
            raise DuplicateEntityException(f"El usuario '{username}' ya existe.")
        existing_email = self.user_repo.find_by_email(email)
        if existing_email:
            raise DuplicateEntityException(f"El correo '{email}' ya está registrado.")

        hashed = self.hasher.hash_password(password)
        new_user = User(
            username=username.strip(),
            email=email.strip().lower(),
            password_hash=hashed,
            role=role.strip().lower()
        )
        return self.user_repo.save(new_user)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.find_by_username(username.strip())
        if not user or not user.is_active:
            raise AuthenticationException("Credenciales inválidas o usuario inactivo.")
        if not self.hasher.verify_password(user.password_hash, password):
            raise AuthenticationException("Credenciales inválidas.")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.find_by_id(user_id)

    def list_users(self) -> List[User]:
        return self.user_repo.list_all()

    def delete_user(self, user_id: int) -> bool:
        if not self.user_repo.find_by_id(user_id):
            raise EntityNotFoundException(f"No se encontró el usuario con ID {user_id}.")
        return self.user_repo.delete(user_id)
