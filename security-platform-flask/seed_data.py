#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导入脚本
将示例数据导入数据库，包括默认角色、管理员用户和示例数据

Requirements: 5.5

使用方法:
    python seed_data.py
"""

from app import create_app
from extensions import db
from models import (
    User, Role,
    Asset,
    Vulnerability,
    Incident, IncidentTimeline,
    IOC, ThreatFeed,
    ComplianceFramework, ComplianceCheck
)
from datetime import datetime, timedelta, timezone
from flask_bcrypt import Bcrypt
import uuid


def create_roles():
    """创建默认角色"""
    roles_data = [
        {
            'name': 'admin',
            'description': '系统管理员，拥有所有权限',
            'permissions': ['*']
        },
        {
            'name': 'analyst',
            'description': '安全分析师，可查看和编辑安全数据',
            'permissions': [
                'assets:read', 'assets:write',
                'vulnerabilities:read', 'vulnerabilities:write',
                'incidents:read', 'incidents:write',
                'threat_intel:read', 'threat_intel:write',
                'compliance:read',
                'reports:read', 'reports:generate',
                'ai:analyze'
            ]
        },
        {
            'name': 'viewer',
            'description': '只读用户，只能查看数据',
            'permissions': [
                'assets:read',
                'vulnerabilities:read',
                'incidents:read',
                'threat_intel:read',
                'compliance:read',
                'reports:read'
            ]
        }
    ]
    
    roles = {}
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
            print(f"  创建角色: {role_data['name']}")
        else:
            print(f"  角色已存在: {role_data['name']}")
        roles[role_data['name']] = role
    
    db.session.commit()
    return roles


def create_admin_user(roles, bcrypt):
    """创建默认管理员用户"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            is_active=True
        )
        admin.roles.append(roles['admin'])
        db.session.add(admin)
        db.session.commit()
        print("  创建管理员用户: admin / admin123")
    else:
        print("  管理员用户已存在: admin")
    return admin


def create_sample_assets():
    """创建示例资产数据"""
    assets_data = [
        {'name': 'Web服务器-01', 'type': 'server', 'ip': '192.168.1.10', 'os': 'Ubuntu 22.04', 'owner': '运维团队', 'department': 'IT', 'criticality': 'high', 'status': 'active', 'risk_score': 35},
        {'name': 'Web服务器-02', 'type': 'server', 'ip': '192.168.1.11', 'os': 'Ubuntu 22.04', 'owner': '运维团队', 'department': 'IT', 'criticality': 'high', 'status': 'active', 'risk_score': 28},
        {'name': '数据库服务器', 'type': 'server', 'ip': '192.168.1.20', 'os': 'CentOS 8', 'owner': 'DBA团队', 'department': 'IT', 'criticality': 'critical', 'status': 'active', 'risk_score': 45},
        {'name': '邮件服务器', 'type': 'server', 'ip': '192.168.1.30', 'os': 'Windows Server 2019', 'owner': '运维团队', 'department': 'IT', 'criticality': 'high', 'status': 'active', 'risk_score': 52},
        {'name': '防火墙-主', 'type': 'network', 'ip': '192.168.1.1', 'os': 'FortiOS 7.0', 'owner': '网络团队', 'department': 'IT', 'criticality': 'critical', 'status': 'active', 'risk_score': 15},
        {'name': '核心交换机', 'type': 'network', 'ip': '192.168.1.2', 'os': 'Cisco IOS', 'owner': '网络团队', 'department': 'IT', 'criticality': 'critical', 'status': 'active', 'risk_score': 20},
        {'name': '开发工作站-01', 'type': 'endpoint', 'ip': '192.168.2.101', 'os': 'Windows 11', 'owner': '张三', 'department': '研发', 'criticality': 'medium', 'status': 'active', 'risk_score': 38},
        {'name': '开发工作站-02', 'type': 'endpoint', 'ip': '192.168.2.102', 'os': 'macOS Ventura', 'owner': '李四', 'department': '研发', 'criticality': 'medium', 'status': 'active', 'risk_score': 25},
        {'name': 'Jenkins CI服务器', 'type': 'server', 'ip': '192.168.1.50', 'os': 'Ubuntu 20.04', 'owner': 'DevOps团队', 'department': '研发', 'criticality': 'high', 'status': 'active', 'risk_score': 42},
        {'name': 'GitLab服务器', 'type': 'server', 'ip': '192.168.1.51', 'os': 'Ubuntu 22.04', 'owner': 'DevOps团队', 'department': '研发', 'criticality': 'critical', 'status': 'active', 'risk_score': 30},
    ]
    
    for asset_data in assets_data:
        asset = Asset.query.filter_by(name=asset_data['name']).first()
        if not asset:
            asset = Asset(**asset_data, compliant=True, patch_pending=False, last_scan=datetime.now(timezone.utc))
            db.session.add(asset)
            print(f"  创建资产: {asset_data['name']}")
    
    db.session.commit()


def create_sample_vulnerabilities():
    """创建示例漏洞数据"""
    vulns_data = [
        {'cve_id': 'CVE-2024-0001', 'title': 'Apache Log4j 远程代码执行漏洞', 'severity': 'critical', 'cvss_score': 10.0, 'status': 'open', 'description': 'Apache Log4j2 存在远程代码执行漏洞，攻击者可通过构造恶意请求执行任意代码。', 'remediation': '升级 Log4j 到 2.17.1 或更高版本'},
        {'cve_id': 'CVE-2024-0002', 'title': 'OpenSSL 缓冲区溢出漏洞', 'severity': 'high', 'cvss_score': 8.1, 'status': 'in_progress', 'description': 'OpenSSL 存在缓冲区溢出漏洞，可能导致拒绝服务或代码执行。', 'remediation': '升级 OpenSSL 到最新版本'},
        {'cve_id': 'CVE-2024-0003', 'title': 'Windows SMB 远程代码执行', 'severity': 'critical', 'cvss_score': 9.8, 'status': 'open', 'description': 'Windows SMB 协议存在远程代码执行漏洞。', 'remediation': '安装最新 Windows 安全更新'},
        {'cve_id': 'CVE-2024-0004', 'title': 'MySQL 权限提升漏洞', 'severity': 'high', 'cvss_score': 7.5, 'status': 'fixed', 'description': 'MySQL 存在权限提升漏洞，低权限用户可获取管理员权限。', 'remediation': '升级 MySQL 到最新版本'},
        {'cve_id': 'CVE-2024-0005', 'title': 'Nginx 信息泄露漏洞', 'severity': 'medium', 'cvss_score': 5.3, 'status': 'open', 'description': 'Nginx 配置不当可能导致敏感信息泄露。', 'remediation': '检查并修复 Nginx 配置'},
        {'cve_id': 'CVE-2024-0006', 'title': 'SSH 弱密码策略', 'severity': 'medium', 'cvss_score': 6.5, 'status': 'in_progress', 'description': '部分服务器 SSH 使用弱密码，存在暴力破解风险。', 'remediation': '强制使用密钥认证，禁用密码登录'},
        {'cve_id': 'CVE-2024-0007', 'title': 'Docker 容器逃逸漏洞', 'severity': 'high', 'cvss_score': 8.8, 'status': 'open', 'description': 'Docker 存在容器逃逸漏洞，攻击者可突破容器隔离。', 'remediation': '升级 Docker 到最新版本'},
    ]
    
    for vuln_data in vulns_data:
        vuln = Vulnerability.query.filter_by(cve_id=vuln_data['cve_id']).first()
        if not vuln:
            vuln = Vulnerability(**vuln_data, discovered_at=datetime.now(timezone.utc) - timedelta(days=7))
            db.session.add(vuln)
            print(f"  创建漏洞: {vuln_data['cve_id']}")
    
    db.session.commit()


def create_sample_incidents():
    """创建示例安全事件数据"""
    incidents_data = [
        {'title': '检测到勒索软件活动', 'type': 'malware', 'severity': 'critical', 'status': 'investigating', 'description': '在多台终端检测到可疑加密行为，疑似勒索软件感染。'},
        {'title': 'DDoS 攻击尝试', 'type': 'dos', 'severity': 'high', 'status': 'mitigated', 'description': '外部 IP 对 Web 服务器发起大量请求，已触发 WAF 防护。'},
        {'title': '异常登录行为', 'type': 'unauthorized_access', 'severity': 'medium', 'status': 'resolved', 'description': '检测到来自异常地理位置的管理员账户登录。'},
        {'title': 'SQL 注入攻击', 'type': 'injection', 'severity': 'high', 'status': 'investigating', 'description': 'WAF 检测到针对用户登录接口的 SQL 注入尝试。'},
        {'title': '数据外泄告警', 'type': 'data_breach', 'severity': 'critical', 'status': 'open', 'description': '检测到大量数据通过非常规端口外传。'},
    ]
    
    for incident_data in incidents_data:
        incident = Incident.query.filter_by(title=incident_data['title']).first()
        if not incident:
            incident = Incident(**incident_data)
            db.session.add(incident)
            db.session.flush()
            
            # 添加时间线
            timeline = IncidentTimeline(
                incident_id=incident.id,
                type='status_change',
                action='事件创建',
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(timeline)
            print(f"  创建事件: {incident_data['title']}")
    
    db.session.commit()


def create_sample_threat_intel():
    """创建示例威胁情报数据"""
    # 威胁源
    feeds_data = [
        {'name': 'AlienVault OTX', 'type': 'commercial', 'url': 'https://otx.alienvault.com', 'enabled': True, 'ioc_count': 15000},
        {'name': 'Abuse.ch', 'type': 'open_source', 'url': 'https://abuse.ch', 'enabled': True, 'ioc_count': 8500},
        {'name': 'VirusTotal', 'type': 'commercial', 'url': 'https://virustotal.com', 'enabled': True, 'ioc_count': 25000},
        {'name': 'MISP Community', 'type': 'community', 'url': 'https://misp-project.org', 'enabled': True, 'ioc_count': 12000},
    ]
    
    for feed_data in feeds_data:
        feed = ThreatFeed.query.filter_by(name=feed_data['name']).first()
        if not feed:
            feed = ThreatFeed(**feed_data, last_update=datetime.now(timezone.utc))
            db.session.add(feed)
            print(f"  创建威胁源: {feed_data['name']}")
    
    # IOC 指标
    iocs_data = [
        {'type': 'ip', 'value': '185.220.101.1', 'threat_type': 'C2 Server', 'confidence': 95, 'source': 'AlienVault OTX'},
        {'type': 'ip', 'value': '45.33.32.156', 'threat_type': 'Malware Distribution', 'confidence': 88, 'source': 'Abuse.ch'},
        {'type': 'domain', 'value': 'malicious-domain.com', 'threat_type': 'Phishing', 'confidence': 92, 'source': 'VirusTotal'},
        {'type': 'domain', 'value': 'evil-c2.net', 'threat_type': 'C2 Server', 'confidence': 97, 'source': 'MISP Community'},
        {'type': 'hash', 'value': 'a1b2c3d4e5f6789012345678901234567890abcd', 'threat_type': 'Ransomware', 'confidence': 99, 'source': 'VirusTotal'},
        {'type': 'hash', 'value': 'deadbeef12345678901234567890123456789012', 'threat_type': 'Trojan', 'confidence': 85, 'source': 'Abuse.ch'},
        {'type': 'url', 'value': 'http://phishing-site.com/login', 'threat_type': 'Phishing', 'confidence': 90, 'source': 'AlienVault OTX'},
    ]
    
    for ioc_data in iocs_data:
        ioc = IOC.query.filter_by(value=ioc_data['value']).first()
        if not ioc:
            ioc = IOC(**ioc_data, first_seen=datetime.now(timezone.utc) - timedelta(days=30), last_seen=datetime.now(timezone.utc))
            db.session.add(ioc)
            print(f"  创建 IOC: {ioc_data['type']} - {ioc_data['value'][:30]}...")
    
    db.session.commit()


def create_sample_compliance():
    """创建示例合规数据"""
    frameworks_data = [
        {'name': '等保2.0 三级', 'description': '网络安全等级保护2.0 三级要求', 'total_controls': 75},
        {'name': 'ISO 27001', 'description': '信息安全管理体系国际标准', 'total_controls': 114},
        {'name': 'PCI DSS', 'description': '支付卡行业数据安全标准', 'total_controls': 12},
    ]
    
    for fw_data in frameworks_data:
        framework = ComplianceFramework.query.filter_by(name=fw_data['name']).first()
        if not framework:
            framework = ComplianceFramework(**fw_data)
            db.session.add(framework)
            db.session.flush()
            
            # 添加一些检查项
            checks = [
                {'control_id': f'{framework.name[:3]}-001', 'title': '访问控制策略', 'status': 'compliant'},
                {'control_id': f'{framework.name[:3]}-002', 'title': '身份认证机制', 'status': 'compliant'},
                {'control_id': f'{framework.name[:3]}-003', 'title': '数据加密要求', 'status': 'non_compliant'},
                {'control_id': f'{framework.name[:3]}-004', 'title': '日志审计要求', 'status': 'partial'},
                {'control_id': f'{framework.name[:3]}-005', 'title': '安全培训要求', 'status': 'compliant'},
            ]
            
            for check_data in checks:
                check = ComplianceCheck(
                    framework_id=framework.id,
                    **check_data,
                    description=f'{check_data["title"]}的详细描述',
                    last_check=datetime.now(timezone.utc)
                )
                db.session.add(check)
            
            print(f"  创建合规框架: {fw_data['name']}")
    
    db.session.commit()


def seed_all():
    """执行所有数据导入"""
    print("\n" + "=" * 50)
    print("开始导入示例数据...")
    print("=" * 50)
    
    app = create_app()
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        print("\n[1/7] 创建默认角色...")
        roles = create_roles()
        
        print("\n[2/7] 创建管理员用户...")
        create_admin_user(roles, bcrypt)
        
        print("\n[3/7] 创建示例资产...")
        create_sample_assets()
        
        print("\n[4/7] 创建示例漏洞...")
        create_sample_vulnerabilities()
        
        print("\n[5/7] 创建示例安全事件...")
        create_sample_incidents()
        
        print("\n[6/7] 创建示例威胁情报...")
        create_sample_threat_intel()
        
        print("\n[7/7] 创建示例合规数据...")
        create_sample_compliance()
        
        print("\n" + "=" * 50)
        print("数据导入完成！")
        print("=" * 50)
        print("\n默认管理员账户:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n")


if __name__ == '__main__':
    seed_all()
