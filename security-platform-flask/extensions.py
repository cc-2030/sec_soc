# extensions.py
# Flask 扩展初始化
# Requirements: 4.1, 4.2, 5.1, 1.6, 6.1, 9.5, 17.1

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger

# 初始化 SQLAlchemy ORM
# Requirement 4.1: THE Database_Layer SHALL 使用 SQLAlchemy ORM 定义所有数据模型
db = SQLAlchemy()

# 初始化 Flask-Migrate (Alembic)
# Requirement 5.1: THE Migration_Tool SHALL 使用 Flask-Migrate (Alembic) 管理数据库迁移
migrate = Migrate()

# 初始化 Flask-Login
# Requirement 1.6: THE Authentication_System SHALL 使用 bcrypt 算法存储密码哈希
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'

# 初始化 Flask-Bcrypt
bcrypt = Bcrypt()

# 初始化 Flask-SocketIO
# Requirement 6.1: THE WebSocket_Server SHALL 使用 Flask-SocketIO 实现实时通信
# 使用 threading 模式以兼容更多 Python 版本
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# 初始化 Flask-Limiter
# Requirement 9.5: THE AI_Service SHALL 实现速率限制
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Swagger 配置
# Requirement 17.1: 使用 flasgger 生成 OpenAPI/Swagger 文档
# Requirement 17.3: 在 /api/docs 路径提供交互式 API 文档界面
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "安全运营平台 API",
        "description": "Flask 安全运营平台 (SOC/SOAR) API 文档",
        "version": "1.0.0",
        "contact": {
            "name": "Security Team"
        }
    },
    "securityDefinitions": {
        "session": {
            "type": "apiKey",
            "name": "session",
            "in": "cookie",
            "description": "Flask-Login 会话认证"
        }
    },
    "security": [{"session": []}],
    "tags": [
        {"name": "认证", "description": "用户认证相关接口"},
        {"name": "用户管理", "description": "用户管理接口（仅管理员）"},
        {"name": "资产管理", "description": "资产管理接口"},
        {"name": "漏洞管理", "description": "漏洞管理接口"},
        {"name": "事件响应", "description": "安全事件响应接口"},
        {"name": "威胁情报", "description": "威胁情报接口"},
        {"name": "合规管理", "description": "合规检查接口"},
        {"name": "报表", "description": "报表生成接口"},
        {"name": "审计日志", "description": "审计日志查询接口"},
        {"name": "设置", "description": "系统设置接口（仅管理员）"},
        {"name": "仪表盘", "description": "仪表盘数据接口"},
        {"name": "AI分析", "description": "AI 智能分析接口"}
    ]
}

swagger = Swagger(config=swagger_config, template=swagger_template)
