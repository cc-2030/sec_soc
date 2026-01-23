import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # SQLAlchemy 配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        """应用初始化钩子"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置
    Requirement 4.2: THE Database_Layer SHALL 支持 SQLite 用于开发环境
    """
    DEBUG = True
    # SQLite 数据库用于开发环境
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        f'sqlite:///{os.path.join(basedir, "instance", "security_platform_dev.db")}'
    )


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    # 使用内存 SQLite 数据库进行测试
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )


class ProductionConfig(Config):
    """生产环境配置
    Requirement 4.2: THE Database_Layer SHALL 支持 PostgreSQL 用于生产环境
    """
    DEBUG = False
    # PostgreSQL 数据库用于生产环境
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/security_platform'
    )
    
    @staticmethod
    def init_app(app):
        """生产环境初始化"""
        Config.init_app(app)
        # 可以在这里添加生产环境特定的配置
        # 例如：日志配置、错误报告等


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
