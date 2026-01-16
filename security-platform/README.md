# 安全运营平台

集成 AI 分析的企业级安全运营平台。

## 功能模块

- **仪表盘** - 安全态势总览、实时告警、威胁趋势
- **安全工具** - 漏洞扫描、端口扫描、恶意软件检测等
- **日志分析** - 多源日志采集、过滤、查询
- **安全运营** - MTTR/MTTD 指标、资产状态、补丁管理
- **AI 分析** - 智能威胁检测、日志分析、安全建议

## 快速启动

```bash
# 后端
cd backend
npm install
cp .env.example .env  # 配置 OPENAI_API_KEY (可选)
npm run dev

# 前端 (新终端)
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## AI 功能

配置 `OPENAI_API_KEY` 环境变量启用完整 AI 分析能力，未配置时使用模拟数据。

## 技术栈

- 前端: React 18 + TypeScript + Vite + Recharts
- 后端: Node.js + Express + TypeScript
- AI: OpenAI GPT-4
