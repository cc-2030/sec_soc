# 安全运营平台 (Flask)

基于 Flask 的企业级安全运营平台 (SOC/SOAR)，集成 AI 分析能力。

## 功能模块

### 态势感知
- **安全态势** - 安全评分、威胁趋势、实时告警、资产状态
- **日志分析** - 多源日志采集、过滤、统计、关联分析
- **AI 分析** - 智能威胁检测、日志模式识别、安全建议

### 资产与漏洞
- **资产管理** - IT 资产台账、风险评分、标签分类、批量导入
- **漏洞管理** - 漏洞全生命周期、CVSS 评分、修复跟踪、MTTR 统计

### 威胁与响应
- **事件响应 (SOAR)** - 安全事件管理、自动化剧本、响应编排
- **威胁情报** - IOC 管理、情报订阅、威胁查询、命中告警

### 合规与报表
- **合规管理** - 等保2.0、ISO27001、PCI-DSS、GDPR 检查
- **报表中心** - 日报/周报/月报、管理层报告、自定义报表

### 系统管理
- **安全工具** - 漏洞扫描、端口扫描、恶意软件检测等
- **系统配置** - 日志源接入(SLS/ES/Kafka)、告警规则、AI 配置

## 快速启动

```bash
cd security-platform-flask

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (可选)
copy .env.example .env

# 启动
python app.py
```

访问 http://localhost:5000

## 项目结构

```
security-platform-flask/
├── app.py              # Flask 主应用
├── config.py           # 配置文件
├── requirements.txt    # Python 依赖
├── templates/          # Jinja2 模板
│   ├── base.html
│   ├── dashboard.html
│   ├── tools.html
│   ├── logs.html
│   ├── operations.html
│   └── ai.html
└── static/
    ├── style.css
    └── app.js
```

## AI 功能

配置 `OPENAI_API_KEY` 环境变量可启用完整 AI 分析，未配置时使用模拟数据演示。
