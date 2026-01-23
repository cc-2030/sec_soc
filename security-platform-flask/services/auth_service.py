# services/auth_service.py
# 认证服务
# Requirements: 1.2, 1.3, 1.6

from extensions import db, bcrypt
from models import User, Role
from datetime import datetime, timezone
from typing import Optional, List


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """验证用户凭据
        
        Args:
            username: 用户名
            password: 明文密码
            
        Returns:
            验证成功返回 User 对象，失败返回 None
            
        Requirement 1.2: THE Authentication_System SHALL 验证用户凭据
        """
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and AuthService.verify_password(password, user.password_hash):
            # 更新最后登录时间
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            bcrypt 哈希字符串
            
        Requirement 1.6: THE Authentication_System SHALL 使用 bcrypt 算法存储密码哈希
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """验证密码
        
        Args:
            password: 明文密码
            password_hash: 存储的哈希值
            
        Returns:
            密码匹配返回 True，否则返回 False
        """
        return bcrypt.check_password_hash(password_hash, password)

    
    @staticmethod
    def create_user(username: str, email: str, password: str, 
                    role_names: List[str] = None) -> User:
        """创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 明文密码
            role_names: 角色名称列表，默认为 ['viewer']
            
        Returns:
            创建的 User 对象
            
        Raises:
            ValueError: 用户名或邮箱已存在
            
        Requirement 1.3: THE Authentication_System SHALL 支持用户创建
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError(f'用户名 {username} 已存在')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError(f'邮箱 {email} 已被使用')
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=AuthService.hash_password(password),
            is_active=True
        )
        
        # 分配角色
        if role_names is None:
            role_names = ['viewer']
        
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def update_password(user: User, new_password: str) -> None:
        """更新用户密码
        
        Args:
            user: User 对象
            new_password: 新密码
        """
        user.password_hash = AuthService.hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    @staticmethod
    def deactivate_user(user: User) -> None:
        """停用用户账户
        
        Args:
            user: User 对象
        """
        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    @staticmethod
    def activate_user(user: User) -> None:
        """激活用户账户
        
        Args:
            user: User 对象
        """
        user.is_active = True
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
