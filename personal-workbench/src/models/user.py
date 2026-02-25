"""User data model for personal workbench."""
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import hashlib


@dataclass
class User:
    """Represents a user with authentication capabilities."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    phone_number: str = ""
    password_hash: str = ""
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = None
    
    def set_password(self, password: str) -> None:
        """Set password hash from plain text password."""
        self.password_hash = self._hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash."""
        return self.password_hash == self._hash_password(password)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """Serialize user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone_number": self.phone_number,
            "password_hash": self.password_hash,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Deserialize user from dictionary."""
        return cls(
            id=data["id"],
            username=data["username"],
            email=data.get("email", ""),
            phone_number=data.get("phone_number", ""),
            password_hash=data.get("password_hash", ""),
            is_admin=data.get("is_admin", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None
        )
