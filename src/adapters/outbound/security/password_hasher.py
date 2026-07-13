from werkzeug.security import generate_password_hash, check_password_hash


class PasswordHasher:
    """Outbound adapter for secure password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using PBKDF2/scrypt via Werkzeug."""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verify a plain text password against a stored password hash."""
        return check_password_hash(password_hash, password)
