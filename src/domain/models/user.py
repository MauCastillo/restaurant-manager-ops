from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Security User Account entity representing operators/admins of the system."""
    username: str
    email: str
    password_hash: str
    role: str = "operator"  # 'admin' or 'operator'
    is_active: bool = True
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role.lower() == "admin"

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
