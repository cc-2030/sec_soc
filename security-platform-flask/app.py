from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from config import config
from extensions import db, migrate, login_manager, bcrypt, swagger, socketio, limiter
from datetime import datetime
import uuid
import random
import os

# 导入所有模型以便 Flask-Migrate 能够检测到它们
# Requirements: 4.3, 5.2
from models import (
    User, Role, user_roles,
    AuditLog,
    Asset,
    Vulnerability, asset_vulnerabilities,
    Incident, IncidentTimeline,
    IOC, ThreatFeed,
    ComplianceFramework, ComplianceCheck
)


def create_app(config_name=None):
    """应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'testing', 'production')
                    默认从环境变量 FLASK_ENV 获取，否则使用 'development'
    
    Returns:
        Flask 应用实例
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    # Requirement 4.1: THE Database_Layer SHALL 使用 SQLAlchemy ORM 定义所有数据模型
    # Requirement 5.1: THE Migration_Tool SHALL 使用 Flask-Migrate (Alembic) 管理数据库迁移
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Requirement 1.6: THE Authentication_System SHALL 使用 bcrypt 算法存储密码哈希
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Requirement 17.1: 初始化 Swagger API 文档
    swagger.init_app(app)
    
    # Requirement 6.1: 初始化 Flask-SocketIO
    socketio.init_app(app)
    
    # Requirement 9.5: 初始化速率限制
    limiter.init_app(app)
    
    # 配置 user_loader 回调
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # 初始化 CORS
    CORS(app)
    
    # 注册中间件
    # Requirement 14.4: 请求追踪 ID
    from middleware.request_id import register_request_id_middleware
    register_request_id_middleware(app)
    
    # Requirement 15.1: 全局错误处理
    from middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册页面路由
    register_page_routes(app)
    
    # 注册 API 路由
    register_api_routes(app)
    
    # 注册 WebSocket 事件处理
    # Requirement 6.1: WebSocket 实时通信
    register_socket_events(app)
    
    # 确保 instance 目录存在（用于 SQLite 数据库）
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Requirement 4.3: WHEN 应用启动时 THEN THE Database_Layer SHALL 自动创建所有必要的数据库表
    # 注意：使用 Flask-Migrate 管理数据库迁移时，不再需要 db.create_all()
    # 表的创建通过 flask db upgrade 命令完成
    # with app.app_context():
    #     db.create_all()
    
    return app


def register_blueprints(app):
    """注册所有蓝图"""
    from routes.auth import auth_bp
    from routes.settings import settings_bp
    from routes.assets import assets_bp
    from routes.vulnerabilities import vulns_bp
    from routes.incidents import incidents_bp
    from routes.threat_intel import threat_intel_bp
    from routes.compliance import compliance_bp
    from routes.reports import reports_bp
    
    # 认证蓝图（无前缀）
    app.register_blueprint(auth_bp)
    
    # API 蓝图
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(assets_bp, url_prefix='/api/assets')
    app.register_blueprint(vulns_bp, url_prefix='/api/vulnerabilities')
    app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
    app.register_blueprint(threat_intel_bp, url_prefix='/api/threat-intel')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')


def register_page_routes(app):
    """注册页面路由
    
    Requirement 1.1: THE Authentication_System SHALL 要求用户登录后才能访问系统
    """
    from flask_login import login_required
    
    @app.route('/')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/tools')
    @login_required
    def tools_page():
        return render_template('tools.html')

    @app.route('/logs')
    @login_required
    def logs_page():
        return render_template('logs.html')

    @app.route('/operations')
    @login_required
    def operations_page():
        return render_template('operations.html')

    @app.route('/ai')
    @login_required
    def ai_page():
        return render_template('ai.html')

    @app.route('/settings')
    @login_required
    def settings_page():
        return render_template('settings.html')

    @app.route('/assets')
    @login_required
    def assets_page():
        return render_template('assets.html')

    @app.route('/vulnerabilities')
    @login_required
    def vulnerabilities_page():
        return render_template('vulnerabilities.html')

    @app.route('/incidents')
    @login_required
    def incidents_page():
        return render_template('incidents.html')

    @app.route('/threat-intel')
    @login_required
    def threat_intel_page():
        return render_template('threat_intel.html')

    @app.route('/compliance')
    @login_required
    def compliance_page():
        return render_template('compliance.html')

    @app.route('/reports')
    @login_required
    def reports_page():
        return render_template('reports.html')


def register_socket_events(app):
    """注册 WebSocket 事件处理
    
    Requirement 6.1: THE WebSocket_Server SHALL 使用 Flask-SocketIO 实现实时通信
    """
    from sockets.alerts import register_alert_events
    register_alert_events(socketio)


def register_api_routes(app):
    """注册 API 路由"""
    from middleware.response import api_response, not_found
    from flask_login import login_required
    from models import Asset, Vulnerability, Incident
    
    # 模拟数据（后续将迁移到数据库）
    security_logs = [
        {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), 'level': 'warning', 'source': 'firewall', 'message': '检测到异常流量', 'ip': '192.168.1.100'},
        {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), 'level': 'error', 'source': 'ids', 'message': 'SQL注入攻击尝试', 'ip': '10.0.0.55'},
        {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), 'level': 'critical', 'source': 'waf', 'message': 'XSS攻击被拦截', 'ip': '172.16.0.88'},
        {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), 'level': 'info', 'source': 'auth', 'message': '管理员登录成功', 'ip': '192.168.1.1'},
        {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), 'level': 'warning', 'source': 'ids', 'message': '端口扫描检测', 'ip': '10.0.0.99'},
    ]

    security_tools = [
        {'id': 'vuln-scanner', 'name': '漏洞扫描器', 'category': 'scanning', 'description': '自动扫描系统漏洞', 'status': 'active'},
        {'id': 'port-scanner', 'name': '端口扫描', 'category': 'scanning', 'description': '扫描开放端口', 'status': 'active'},
        {'id': 'malware-detector', 'name': '恶意软件检测', 'category': 'detection', 'description': '检测恶意文件和行为', 'status': 'active'},
        {'id': 'traffic-analyzer', 'name': '流量分析', 'category': 'monitoring', 'description': '实时网络流量分析', 'status': 'active'},
        {'id': 'log-collector', 'name': '日志采集器', 'category': 'collection', 'description': '多源日志统一采集', 'status': 'active'},
        {'id': 'threat-intel', 'name': '威胁情报', 'category': 'intelligence', 'description': '威胁情报订阅和查询', 'status': 'active'},
    ]

    @app.route('/api/dashboard/overview')
    @login_required
    def get_overview():
        """获取仪表盘概览数据（从数据库聚合）"""
        total_assets = Asset.query.count()
        active_incidents = Incident.query.filter(Incident.status != 'closed').count()
        open_vulns = Vulnerability.query.filter(Vulnerability.status == 'open').count()
        
        # 计算安全评分（简化算法）
        critical_vulns = Vulnerability.query.filter_by(severity='critical', status='open').count()
        high_vulns = Vulnerability.query.filter_by(severity='high', status='open').count()
        security_score = max(0, 100 - critical_vulns * 10 - high_vulns * 5 - active_incidents * 3)
        
        return api_response({
            'security_score': min(100, security_score),
            'active_threats': active_incidents,
            'open_vulnerabilities': open_vulns,
            'total_assets': total_assets,
            'trends': {'threats': [5, 8, 3, 7, 4, 6, 3], 'incidents': [2, 1, 4, 2, 3, 1, 2]}
        })

    @app.route('/api/dashboard/alerts')
    @login_required
    def get_alerts():
        """获取最新告警"""
        incidents = Incident.query.filter(
            Incident.status != 'closed'
        ).order_by(Incident.created_at.desc()).limit(5).all()
        
        return api_response([{
            'id': i.id,
            'severity': i.severity,
            'title': i.title,
            'time': i.created_at.isoformat() if i.created_at else None,
            'status': i.status
        } for i in incidents])

    @app.route('/api/dashboard/assets')
    @login_required
    def get_dashboard_assets():
        """获取资产统计"""
        from sqlalchemy import func
        
        stats = db.session.query(
            Asset.type,
            func.count(Asset.id).label('total'),
            func.sum(db.case((Asset.status == 'online', 1), else_=0)).label('healthy'),
            func.sum(db.case((Asset.risk_score > 60, 1), else_=0)).label('warning'),
            func.sum(db.case((Asset.risk_score > 80, 1), else_=0)).label('critical')
        ).group_by(Asset.type).all()
        
        result = {}
        for type_, total, healthy, warning, critical in stats:
            result[type_] = {
                'total': total or 0,
                'healthy': healthy or 0,
                'warning': warning or 0,
                'critical': critical or 0
            }
        
        return api_response(result)

    @app.route('/api/dashboard/operations')
    @login_required
    def get_operations():
        """获取运营指标"""
        return api_response({
            'mttr': 45,
            'mttd': 12,
            'incidents_this_month': Incident.query.count(),
            'compliance_score': 92,
            'patch_status': {
                'up_to_date': Asset.query.filter_by(patch_pending=False).count(),
                'pending': Asset.query.filter_by(patch_pending=True).count(),
                'critical': 4
            }
        })

    @app.route('/api/logs')
    @login_required
    def get_logs():
        level = request.args.get('level')
        source = request.args.get('source')
        logs = security_logs.copy()
        if level:
            logs = [l for l in logs if l['level'] == level]
        if source:
            logs = [l for l in logs if l['source'] == source]
        return api_response(logs)

    @app.route('/api/logs', methods=['POST'])
    @login_required
    def add_log():
        data = request.json
        log = {'id': str(uuid.uuid4()), 'timestamp': datetime.now().isoformat(), **data}
        security_logs.insert(0, log)
        return api_response(log, '日志添加成功', 201)

    @app.route('/api/logs/stats')
    @login_required
    def get_log_stats():
        stats = {'total': len(security_logs), 'by_level': {}, 'by_source': {}}
        for log in security_logs:
            stats['by_level'][log['level']] = stats['by_level'].get(log['level'], 0) + 1
            stats['by_source'][log['source']] = stats['by_source'].get(log['source'], 0) + 1
        return api_response(stats)

    @app.route('/api/tools')
    @login_required
    def get_tools():
        return api_response(security_tools)

    @app.route('/api/tools/<tool_id>/run', methods=['POST'])
    @login_required
    def run_tool(tool_id):
        tool = next((t for t in security_tools if t['id'] == tool_id), None)
        if not tool:
            return not_found('工具不存在')
        return api_response({
            'tool_id': tool_id,
            'status': 'completed',
            'start_time': datetime.now().isoformat(),
            'results': {'findings': random.randint(0, 10), 'scanned': random.randint(100, 1000)}
        }, '工具执行完成')

    @app.route('/api/ai/analyze-logs', methods=['POST'])
    @login_required
    @limiter.limit("10 per minute")
    def analyze_logs():
        """AI 日志分析
        
        Requirement 9.2: THE AI_Service SHALL 分析安全日志
        Requirement 9.5: THE AI_Service SHALL 实现速率限制
        """
        from services.ai_service import AIService, AIServiceError
        
        data = request.get_json() or {}
        logs = data.get('logs', security_logs[:10])  # 默认使用最近10条日志
        use_ai = data.get('use_ai', False)  # 是否使用真实 AI
        
        if use_ai:
            try:
                ai_service = AIService()
                result = ai_service.analyze_logs(logs)
                return api_response(result)
            except AIServiceError as e:
                return api_response(None, str(e), 500)
            except ValueError as e:
                return api_response(None, str(e), 400)
        
        # 模拟 AI 分析结果（无 API Key 时）
        return api_response({
            'summary': '检测到潜在安全威胁',
            'risk_level': 'medium',
            'findings': [
                {'type': 'SQL注入', 'severity': 'high', 'count': 1, 'recommendation': '加强输入验证，使用参数化查询'},
                {'type': '异常流量', 'severity': 'medium', 'count': 3, 'recommendation': '检查防火墙规则，考虑限流'},
                {'type': 'XSS攻击', 'severity': 'high', 'count': 1, 'recommendation': '启用CSP策略，过滤用户输入'},
            ],
            'patterns': ['多次失败登录尝试', '非工作时间访问', '异常数据传输'],
            'recommendations': ['启用双因素认证', '审查访问控制策略', '增加日志监控频率', '更新WAF规则']
        })

    @app.route('/api/ai/analyze-logs/stream')
    @login_required
    @limiter.limit("10 per minute")
    def analyze_logs_stream():
        """AI 日志分析（流式响应）
        
        Requirement 9.3: THE AI_Service SHALL 支持流式响应
        """
        from flask import Response
        from services.ai_service import AIService, AIServiceError
        
        def generate():
            try:
                ai_service = AIService()
                logs = security_logs[:10]
                for chunk in ai_service.analyze_logs(logs, stream=True):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except AIServiceError as e:
                yield f"data: [ERROR] {str(e)}\n\n"
            except ValueError as e:
                yield f"data: [ERROR] {str(e)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')

    @app.route('/api/ai/detect-threats', methods=['POST'])
    @login_required
    @limiter.limit("10 per minute")
    def detect_threats():
        """AI 威胁检测
        
        Requirement 10.1: THE AI_Service SHALL 检测潜在威胁
        Requirement 10.5: THE AI_Service SHALL 支持自定义提示词
        """
        from services.ai_service import AIService, AIServiceError
        
        data = request.get_json() or {}
        use_ai = data.get('use_ai', False)
        
        if use_ai:
            try:
                ai_service = AIService()
                result = ai_service.detect_threats(data)
                return api_response(result)
            except AIServiceError as e:
                return api_response(None, str(e), 500)
            except ValueError as e:
                return api_response(None, str(e), 400)
        
        # 模拟威胁检测结果
        return api_response({
            'threats': [
                {'id': 't1', 'type': '暴力破解', 'confidence': 0.85, 'source': '10.0.0.55', 'target': 'auth-service', 'recommendation': '封禁IP，加强认证'},
                {'id': 't2', 'type': '数据泄露', 'confidence': 0.72, 'source': '192.168.1.100', 'target': 'database', 'recommendation': '检查数据访问日志'},
                {'id': 't3', 'type': '横向移动', 'confidence': 0.68, 'source': '172.16.0.88', 'target': 'internal-network', 'recommendation': '隔离受影响主机'},
            ],
            'overall_risk': 'medium'
        })

    @app.route('/api/ai/recommendations')
    def get_recommendations():
        return jsonify({'recommendations': [
            {'priority': 'high', 'category': 'access_control', 'title': '启用多因素认证', 'description': '为所有管理员账户启用MFA'},
            {'priority': 'high', 'category': 'patching', 'title': '紧急补丁更新', 'description': '4个系统存在高危漏洞需立即修复'},
            {'priority': 'medium', 'category': 'network', 'title': '更新防火墙规则', 'description': '限制非必要端口的外部访问'},
            {'priority': 'low', 'category': 'monitoring', 'title': '增加日志保留期', 'description': '将日志保留期从7天延长至30天'},
        ]})


# 创建应用实例（用于直接运行和 Flask CLI）
app = create_app()


if __name__ == '__main__':
    # 使用 socketio.run() 替代 app.run() 以支持 WebSocket
    # Requirement 6.1: WebSocket 实时通信
    socketio.run(app, debug=True, port=5000)
