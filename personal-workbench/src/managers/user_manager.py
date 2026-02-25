"""User manager for handling user operations."""
from datetime import datetime, timedelta
from typing import Optional, Dict
import random

from ..models.user import User
from ..storage.storage import Storage


class UserManager:
    """Manages user CRUD operations and authentication."""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self._users: dict[str, User] = {}
        self._load_users()
        # 验证码存储，实际生产环境应使用Redis
        self._verification_codes: Dict[str, Dict] = {}
    
    def _load_users(self) -> None:
        """Load users from storage."""
        user_dicts = self.storage.get_users()
        self._users = {u["id"]: User.from_dict(u) for u in user_dicts}
    
    def _save_users(self) -> None:
        """Save users to storage."""
        user_dicts = [u.to_dict() for u in self._users.values()]
        self.storage.save_users(user_dicts)
    
    def create_user(self, username: str, email: str, password: str, phone_number: str = "", is_admin: bool = False) -> User:
        """Create a new user with validation."""
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Check if username already exists
        if self.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        # Check if email already exists (if provided)
        if email and self.get_user_by_email(email):
            raise ValueError("Email already exists")
        
        # Check if phone number already exists (if provided)
        if phone_number and self.get_user_by_phone(phone_number):
            raise ValueError("Phone number already exists")
        
        user = User(
            username=username.strip(),
            email=email.strip() if email else "",
            phone_number=phone_number.strip() if phone_number else "",
            is_admin=is_admin,
            created_at=datetime.now()
        )
        user.set_password(password)
        
        self._users[user.id] = user
        self._save_users()
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password."""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            user.last_login = datetime.now()
            self._save_users()
            return user
        return None
    
    def authenticate_user_by_phone(self, phone_number: str, code: str) -> Optional[User]:
        """Authenticate user by phone number and verification code."""
        # Validate verification code
        if not self._verify_code(phone_number, code):
            return None
        
        # Check if user exists
        user = self.get_user_by_phone(phone_number)
        
        # If user doesn't exist, create one automatically
        if not user:
            # Generate username from phone number
            username = f"user_{phone_number[-4:]}"
            # Generate random password
            password = str(random.randint(100000, 999999))
            user = self.create_user(
                username=username,
                email="",
                password=password,
                phone_number=phone_number
            )
        
        # Update last login time
        user.last_login = datetime.now()
        self._save_users()
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        for user in self._users.values():
            if user.phone_number == phone_number:
                return user
        return None
    
    def get_all_users(self) -> list[User]:
        """Get all users."""
        return list(self._users.values())
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if "email" in kwargs:
            user.email = kwargs["email"].strip()
        
        if "phone_number" in kwargs:
            user.phone_number = kwargs["phone_number"].strip()
        
        if "password" in kwargs:
            password = kwargs["password"]
            if password and len(password) >= 6:
                user.set_password(password)
        
        self._save_users()
        return user
    
    def generate_verification_code(self, phone_number: str) -> str:
        """Generate and store verification code for phone number."""
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Store code with expiration time (5 minutes)
        self._verification_codes[phone_number] = {
            "code": code,
            "expires_at": datetime.now() + timedelta(minutes=5)
        }
        
        # For demo purposes, print the code to console
        print(f"Verification code for {phone_number}: {code}")
        
        return code
    
    def _verify_code(self, phone_number: str, code: str) -> bool:
        """Verify if the provided code is valid for the phone number."""
        if phone_number not in self._verification_codes:
            return False
        
        code_info = self._verification_codes[phone_number]
        if code_info["expires_at"] < datetime.now():
            # Remove expired code
            del self._verification_codes[phone_number]
            return False
        
        if code_info["code"] != code:
            return False
        
        # Code is valid, remove it after verification
        del self._verification_codes[phone_number]
        return True
    
    def create_admin_user(self, username: str, email: str, password: str, phone_number: str = "") -> User:
        """Create an admin user."""
        return self.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            is_admin=True
        )
