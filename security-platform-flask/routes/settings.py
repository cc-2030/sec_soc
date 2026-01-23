from flask import Blueprint, jsonify, request
from middleware.rbac import require_role
from services.audit_service import audit_action
import uuid
import json
import os

settings_bp = Blueprint('settings', __name__)

# 数据存储路径
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(filename, default=[]):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_data(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== 日志源配置 ====================
# Requirement 2.2: THE RBAC_System SHALL 根据用户角色限制功能访问
@settings_bp.route('/log-sources', methods=['GET'])
@require_role('admin')
def get_log_sources():
    return jsonify(load_data('log_sources.json', []))

@settings_bp.route('/log-sources', methods=['POST'])
@require_role('admin')
@audit_action('create', 'log_source')
def add_log_source():
    data = request.json
    sources = load_data('log_sources.json', [])
    source = {
        'id': str(uuid.uuid4()),
        'name': data.get('name'),
        'type': data.get('type'),
        'enabled': data.get('enabled', True),
        'interval': int(data.get('interval', 60)),
        'created_at': __import__('datetime').datetime.now().isoformat(),
        # 根据类型保存不同字段
        **{k: v for k, v in data.items() if k not in ['name', 'type', 'enabled', 'interval']}
    }
    sources.append(source)
    save_data('log_sources.json', sources)
    return jsonify(source), 201

@settings_bp.route('/log-sources/<source_id>', methods=['PATCH'])
@require_role('admin')
@audit_action('update', 'log_source')
def update_log_source(source_id):
    sources = load_data('log_sources.json', [])
    for s in sources:
        if s['id'] == source_id:
            s.update(request.json)
            save_data('log_sources.json', sources)
            return jsonify(s)
    return jsonify({'error': '日志源不存在'}), 404

@settings_bp.route('/log-sources/<source_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'log_source')
def delete_log_source(source_id):
    sources = load_data('log_sources.json', [])
    sources = [s for s in sources if s['id'] != source_id]
    save_data('log_sources.json', sources)
    return jsonify({'success': True})

@settings_bp.route('/log-sources/<source_id>/test', methods=['POST'])
@require_role('admin')
def test_log_source(source_id):
    sources = load_data('log_sources.json', [])
    source = next((s for s in sources if s['id'] == source_id), None)
    if not source:
        return jsonify({'success': False, 'error': '日志源不存在'}), 404
    
    # 模拟测试连接
    # 实际实现需要根据类型进行真实连接测试
    import random
    success = random.random() > 0.2  # 80% 成功率模拟
    return jsonify({
        'success': success,
        'error': None if success else '连接超时',
        'latency': random.randint(50, 200) if success else None
    })

# ==================== 告警规则 ====================
@settings_bp.route('/alert-rules', methods=['GET'])
@require_role('admin')
def get_alert_rules():
    return jsonify(load_data('alert_rules.json', []))

@settings_bp.route('/alert-rules', methods=['POST'])
@require_role('admin')
@audit_action('create', 'alert_rule')
def add_alert_rule():
    data = request.json
    rules = load_data('alert_rules.json', [])
    rule = {
        'id': str(uuid.uuid4()),
        'name': data.get('name'),
        'log_source': data.get('log_source'),
        'pattern': data.get('pattern'),
        'severity': data.get('severity', 'medium'),
        'threshold': int(data.get('threshold', 5)),
        'notify_email': data.get('notify_email', False),
        'notify_webhook': data.get('notify_webhook', False),
        'notify_sms': data.get('notify_sms', False),
        'enabled': True,
        'created_at': __import__('datetime').datetime.now().isoformat()
    }
    rules.append(rule)
    save_data('alert_rules.json', rules)
    return jsonify(rule), 201

@settings_bp.route('/alert-rules/<rule_id>', methods=['PATCH'])
@require_role('admin')
@audit_action('update', 'alert_rule')
def update_alert_rule(rule_id):
    rules = load_data('alert_rules.json', [])
    for r in rules:
        if r['id'] == rule_id:
            r.update(request.json)
            save_data('alert_rules.json', rules)
            return jsonify(r)
    return jsonify({'error': '规则不存在'}), 404

@settings_bp.route('/alert-rules/<rule_id>', methods=['DELETE'])
@require_role('admin')
@audit_action('delete', 'alert_rule')
def delete_alert_rule(rule_id):
    rules = load_data('alert_rules.json', [])
    rules = [r for r in rules if r['id'] != rule_id]
    save_data('alert_rules.json', rules)
    return jsonify({'success': True})

# ==================== 系统配置 ====================
@settings_bp.route('/config', methods=['GET'])
@require_role('admin')
def get_config():
    return jsonify(load_data('config.json', {
        'ai': {'provider': 'openai', 'model': 'gpt-4', 'auto_analyze': True, 'analyze_frequency': '5min'},
        'notify': {'smtp_host': '', 'smtp_port': 587, 'webhook_url': ''},
        'retention': {'log_retention': 30, 'alert_retention': 90}
    }))

@settings_bp.route('/config/ai', methods=['POST'])
@require_role('admin')
@audit_action('update', 'config')
def save_ai_config():
    config = load_data('config.json', {})
    config['ai'] = request.json
    save_data('config.json', config)
    return jsonify({'success': True})

@settings_bp.route('/config/notify', methods=['POST'])
@require_role('admin')
@audit_action('update', 'config')
def save_notify_config():
    config = load_data('config.json', {})
    config['notify'] = request.json
    save_data('config.json', config)
    return jsonify({'success': True})

@settings_bp.route('/config/retention', methods=['POST'])
@require_role('admin')
@audit_action('update', 'config')
def save_retention_config():
    config = load_data('config.json', {})
    config['retention'] = request.json
    save_data('config.json', config)
    return jsonify({'success': True})
