# Implementation Plan: Security Platform Optimization

## Overview

本实现计划将安全运营平台优化分为六个阶段，每个阶段可独立部署和测试。采用渐进式实现策略，确保每个阶段完成后平台都能正常运行。

**实现顺序**：
1. 数据库持久化（基础设施）
2. 用户认证与权限管理（安全基础）
3. API 规范化（接口标准化）
4. 实时告警推送（实时通信）
5. AI 分析增强（智能功能）
6. 前端代码重构（用户体验）

**当前状态**：项目使用内存数据和 JSON 文件存储，无认证、无数据库、无 WebSocket。所有任务均未开始。

## Tasks

- [x] 1. 数据库持久化基础设施
  - [x] 1.1 配置 SQLAlchemy 和 Flask-Migrate
    - 更新 requirements.txt 添加依赖：flask-sqlalchemy, flask-migrate
    - 创建 extensions.py 初始化 db 和 migrate
    - 更新 config.py 添加数据库配置（SQLite 开发/PostgreSQL 生产）
    - 更新 app.py 注册扩展并初始化数据库
    - _Requirements: 4.1, 4.2, 5.1_

  - [x] 1.2 创建核心数据模型
    - 创建 models/__init__.py 导出所有模型
    - 创建 models/user.py（User, Role, user_roles 关联表）
    - 创建 models/audit.py（AuditLog）
    - 创建 models/asset.py（Asset）
    - 创建 models/vulnerability.py（Vulnerability, asset_vulnerabilities）
    - 创建 models/incident.py（Incident, IncidentTimeline）
    - 创建 models/threat_intel.py（IOC, ThreatFeed）
    - 创建 models/compliance.py（ComplianceFramework, ComplianceCheck）
    - _Requirements: 4.4, 4.5_

  - [ ]* 1.3 编写数据模型属性测试
    - 创建 tests/conftest.py 配置 pytest 和 hypothesis
    - 创建 tests/test_models.py
    - **Property 1: Password Hash Security**
    - **Validates: Requirements 1.6**

  - [x] 1.4 创建初始数据库迁移
    - 运行 flask db init 初始化迁移目录
    - 运行 flask db migrate 生成初始迁移
    - 运行 flask db upgrade 创建表
    - _Requirements: 4.3, 5.2_

  - [x] 1.5 创建数据导入迁移脚本
    - 创建 seed_data.py 脚本将现有内存数据导入数据库
    - 导入默认角色（admin, analyst, viewer）及权限
    - 导入示例资产、漏洞、事件、威胁情报数据
    - 创建默认管理员用户
    - _Requirements: 5.5_

- [x] 2. Checkpoint - 数据库基础设施验证
  - 运行 flask db upgrade 确保所有数据库表正确创建
  - 运行 python seed_data.py 确保数据迁移脚本正常运行
  - 运行 pytest tests/test_models.py 确保所有测试通过
  - 如有问题请询问用户

- [x] 3. 用户认证模块
  - [x] 3.1 配置 Flask-Login 和 Bcrypt
    - 更新 requirements.txt 添加依赖：flask-login, flask-bcrypt
    - 在 extensions.py 初始化 login_manager 和 bcrypt
    - 配置 login_manager（login_view='auth.login', session_protection='strong'）
    - 在 User 模型实现 UserMixin 和 get_id() 方法
    - 实现 user_loader 回调函数
    - _Requirements: 1.6_

  - [x] 3.2 实现认证服务
    - 创建 services/__init__.py
    - 创建 services/auth_service.py
    - 实现 AuthService.authenticate(username, password) 方法
    - 实现 AuthService.hash_password(password) 方法
    - 实现 AuthService.verify_password(password, hash) 方法
    - 实现 AuthService.create_user(username, email, password, roles) 方法
    - _Requirements: 1.2, 1.3, 1.6_

  - [ ]* 3.3 编写认证服务属性测试
    - 创建 tests/test_auth.py
    - **Property 2: Authentication Redirect**
    - **Property 3: Valid Credentials Create Session**
    - **Property 4: Invalid Credentials Rejection**
    - **Property 5: Logout Session Destruction**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [x] 3.4 创建认证路由和登录页面
    - 创建 routes/auth.py 蓝图
    - 实现 GET/POST /login 路由（表单登录）
    - 实现 GET /logout 路由
    - 实现 GET /api/auth/me 路由（返回当前用户信息）
    - 创建 templates/auth/login.html 登录页面
    - 在 app.py 注册认证蓝图
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 3.5 添加登录保护到现有路由
    - 为所有页面路由添加 @login_required 装饰器
    - 为所有 API 路由添加认证检查
    - 更新 base.html 显示当前用户名和登出按钮
    - 配置会话超时时间
    - _Requirements: 1.1, 1.5_

- [x] 4. RBAC 权限控制模块
  - [x] 4.1 实现 RBAC 中间件
    - 创建 middleware/__init__.py
    - 创建 middleware/rbac.py
    - 实现 require_role(*roles) 装饰器
    - 实现 require_permission(permission) 装饰器
    - 在 User 模型实现 has_role(), has_any_role(), has_permission() 方法
    - 定义 ROLES 常量（admin, analyst, viewer 及其权限）
    - _Requirements: 2.1, 2.2, 2.4_

  - [ ]* 4.2 编写 RBAC 属性测试
    - 创建 tests/test_rbac.py
    - **Property 6: RBAC Permission Enforcement**
    - **Property 7: Role Assignment Persistence**
    - **Property 8: Permission Update Immediacy**
    - **Validates: Requirements 2.2, 2.3, 2.5**

  - [x] 4.3 应用权限控制到 API 端点
    - 为 routes/settings.py 所有端点添加 @require_role('admin') 装饰器
    - 为写操作 API（POST/PATCH/DELETE）添加 @require_role('analyst', 'admin') 装饰器
    - 为只读 API（GET）添加 @require_role('viewer', 'analyst', 'admin') 装饰器
    - _Requirements: 2.2, 2.4_

  - [x] 4.4 创建用户管理 API
    - 在 routes/auth.py 添加用户管理端点
    - 实现 GET /api/users 列表（admin only）
    - 实现 POST /api/users 创建用户（admin only）
    - 实现 PATCH /api/users/<id> 更新用户角色（admin only）
    - 实现 DELETE /api/users/<id> 删除用户（admin only）
    - _Requirements: 2.3_

- [x] 5. 审计日志模块
  - [x] 5.1 实现审计服务
    - 创建 services/audit_service.py
    - 实现 AuditService.log() 静态方法（记录审计日志到数据库）
    - 实现 audit_action(action_type, resource_type) 装饰器
    - 实现 AuditService.query() 查询方法（支持过滤和分页）
    - _Requirements: 3.1, 3.2, 3.4_

  - [ ]* 5.2 编写审计日志属性测试
    - 创建 tests/test_audit.py
    - **Property 9: Audit Log Completeness**
    - **Property 10: Authentication Event Logging**
    - **Property 11: Audit Log Query Filtering**
    - **Property 12: Audit Log Immutability**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

  - [x] 5.3 应用审计装饰器到 API 端点
    - 为 routes/assets.py 所有 POST/PATCH/DELETE 端点添加 @audit_action 装饰器
    - 为 routes/vulnerabilities.py 所有写操作添加审计
    - 为 routes/incidents.py 所有写操作添加审计
    - 为 routes/threat_intel.py 所有写操作添加审计
    - 为 routes/settings.py 所有写操作添加审计
    - 在 routes/auth.py 登录/登出时记录认证事件
    - _Requirements: 3.1, 3.3_

  - [x] 5.4 创建审计日志查询 API
    - 在 routes/auth.py 或新建 routes/audit.py 添加审计日志端点
    - 实现 GET /api/audit-logs 查询接口（admin only）
    - 支持 start_time, end_time, user_id, action_type 过滤参数
    - 支持分页（page, page_size）
    - _Requirements: 3.4, 3.5_

- [x] 6. Checkpoint - 认证和权限验证
  - 测试登录/登出功能（使用默认管理员账户）
  - 测试 RBAC 权限控制（不同角色访问不同端点）
  - 测试审计日志记录（执行操作后查询审计日志）
  - 运行 pytest tests/ 确保所有测试通过
  - 如有问题请询问用户

- [x] 7. API 规范化 - 响应格式
  - [x] 7.1 创建统一响应工具
    - 创建 middleware/response.py
    - 实现 api_response(data, message, status_code) 函数
    - 实现 paginated_response(items, total, page, page_size) 函数
    - 实现 error_response(code, message, status_code) 函数
    - _Requirements: 14.1, 14.2, 14.3_

  - [x] 7.2 实现全局错误处理
    - 创建 middleware/error_handler.py
    - 实现 register_error_handlers(app) 函数
    - 处理 ValidationError（400）, 401, 403, 404, 500 错误
    - 在 app.py 调用 register_error_handlers(app)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [x] 7.3 添加请求追踪 ID
    - 创建 middleware/request_id.py
    - 实现 @app.before_request 生成 UUID 追踪 ID（存入 g.request_id）
    - 实现 @app.after_request 在响应头添加 X-Request-ID
    - 在 app.py 注册中间件
    - _Requirements: 14.4_

  - [ ]* 7.4 编写 API 响应格式属性测试
    - 创建 tests/test_api_format.py
    - **Property 22: API Success Response Format**
    - **Property 23: API Error Response Format**
    - **Property 24: API Pagination Format**
    - **Property 25: API Request Trace ID**
    - **Property 26: HTTP Status Code Correctness**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 15.2-15.6**

- [x] 8. API 规范化 - 请求验证
  - [x] 8.1 创建请求验证模式
    - 更新 requirements.txt 添加依赖：marshmallow
    - 创建 schemas/__init__.py
    - 创建 schemas/common.py（PaginationSchema, IDSchema, validate_request 装饰器）
    - 创建 schemas/auth.py（LoginSchema, UserCreateSchema, UserUpdateSchema）
    - 创建 schemas/asset.py（AssetCreateSchema, AssetUpdateSchema）
    - 创建 schemas/vulnerability.py（VulnerabilityCreateSchema, VulnerabilityUpdateSchema）
    - 创建 schemas/incident.py（IncidentCreateSchema, IncidentUpdateSchema）
    - _Requirements: 16.1, 16.3_

  - [x] 8.2 实现验证装饰器和输入清理
    - 在 schemas/common.py 实现 validate_request(schema_class) 装饰器
    - 实现 sanitize_input() 函数（HTML 转义、SQL 注入防护）
    - 实现 UUID 格式验证字段
    - _Requirements: 16.2, 16.4, 16.5_

  - [ ]* 8.3 编写请求验证属性测试
    - 创建 tests/test_validation.py
    - **Property 27: Validation Error Details**
    - **Property 28: Input Sanitization**
    - **Property 29: ID Format Validation**
    - **Validates: Requirements 16.2, 16.4, 16.5**

  - [x] 8.4 应用验证到现有 API 端点
    - 更新 routes/assets.py 为 POST 端点添加 @validate_request(AssetCreateSchema)
    - 更新 routes/vulnerabilities.py 添加验证装饰器
    - 更新 routes/incidents.py 添加验证装饰器
    - 更新 routes/threat_intel.py 添加验证装饰器
    - 更新 routes/settings.py 添加验证装饰器
    - _Requirements: 16.3_

- [x] 9. API 规范化 - 文档生成
  - [x] 9.1 配置 Swagger 文档
    - 更新 requirements.txt 添加依赖：flasgger
    - 在 extensions.py 初始化 Swagger
    - 配置 Swagger UI 路径为 /api/docs
    - 在 app.py 注册 Swagger
    - _Requirements: 17.1, 17.3_

  - [x] 9.2 为 API 端点添加文档注释
    - 为 routes/auth.py 所有端点添加 Swagger docstring
    - 为 routes/assets.py 所有端点添加 Swagger docstring
    - 为 routes/vulnerabilities.py 所有端点添加 Swagger docstring
    - 为 routes/incidents.py 所有端点添加 Swagger docstring
    - 为 routes/threat_intel.py 所有端点添加 Swagger docstring
    - 为 routes/compliance.py 所有端点添加 Swagger docstring
    - 为 routes/reports.py 所有端点添加 Swagger docstring
    - _Requirements: 17.2, 17.4_

- [x] 10. 迁移现有 API 到新格式
  - [x] 10.1 更新资产管理 API
    - 更新 routes/assets.py 使用 api_response/paginated_response
    - 将内存数据改为数据库查询（使用 Asset 模型）
    - 添加分页支持（page, page_size 参数）
    - _Requirements: 14.5_

  - [x] 10.2 更新漏洞管理 API
    - 更新 routes/vulnerabilities.py 使用新响应格式
    - 将内存数据改为数据库查询（使用 Vulnerability 模型）
    - 添加分页支持
    - _Requirements: 14.5_

  - [x] 10.3 更新事件响应 API
    - 更新 routes/incidents.py 使用新响应格式
    - 将内存数据改为数据库查询（使用 Incident, IncidentTimeline 模型）
    - 添加分页支持
    - _Requirements: 14.5_

  - [x] 10.4 更新威胁情报 API
    - 更新 routes/threat_intel.py 使用新响应格式
    - 将内存数据改为数据库查询（使用 IOC, ThreatFeed 模型）
    - 添加分页支持
    - _Requirements: 14.5_

  - [x] 10.5 更新合规和报表 API
    - 更新 routes/compliance.py 使用新响应格式
    - 更新 routes/reports.py 使用新响应格式
    - 将内存数据改为数据库查询
    - 添加分页支持
    - _Requirements: 14.5_

  - [x] 10.6 更新仪表盘和设置 API
    - 更新 app.py 中的仪表盘 API 使用新响应格式
    - 更新 routes/settings.py 使用新响应格式
    - 仪表盘数据从数据库聚合查询
    - _Requirements: 14.5_

- [x] 11. Checkpoint - API 规范化验证
  - 访问 /api/docs 确保 Swagger 文档可访问
  - 测试 API 返回统一格式（success, data, error）
  - 测试请求验证（提交无效数据应返回 400）
  - 测试分页功能（page, page_size 参数）
  - 运行 pytest tests/ 确保所有测试通过
  - 如有问题请询问用户

- [x] 12. WebSocket 实时通信
  - [x] 12.1 配置 Flask-SocketIO
    - 更新 requirements.txt 添加依赖：flask-socketio, python-socketio, eventlet
    - 在 extensions.py 初始化 socketio
    - 更新 app.py 使用 socketio.run() 替代 app.run()
    - _Requirements: 6.1_

  - [x] 12.2 实现 WebSocket 认证
    - 创建 sockets/__init__.py
    - 创建 sockets/alerts.py
    - 实现 @socketio.on('connect') 验证 Flask-Login 会话
    - 实现连接拒绝逻辑（未认证返回 False）
    - _Requirements: 6.2_

  - [ ]* 12.3 编写 WebSocket 认证属性测试
    - 创建 tests/test_websocket.py
    - **Property 13: WebSocket Authentication**
    - **Validates: Requirements 6.2**

  - [x] 12.4 实现告警推送服务
    - 实现 @socketio.on('subscribe_alerts') 订阅处理
    - 实现 push_alert(alert, severity) 函数
    - 实现按严重级别的房间管理（alerts_critical, alerts_high, alerts_all）
    - _Requirements: 6.3, 6.4_

  - [ ]* 12.5 编写告警推送属性测试
    - **Property 14: Alert Broadcasting**
    - **Property 15: Alert Subscription Filtering**
    - **Validates: Requirements 6.3, 6.4**

  - [x] 12.6 实现仪表盘实时更新
    - 实现 @socketio.on('subscribe_dashboard') 订阅处理
    - 实现 push_dashboard_update(data) 函数
    - 在数据变更时触发推送（资产、漏洞、事件变更）
    - _Requirements: 7.1, 7.2_

  - [ ]* 12.7 编写仪表盘更新属性测试
    - **Property 16: Dashboard Update Broadcasting**
    - **Validates: Requirements 7.2**

- [x] 13. 前端 WebSocket 集成
  - [x] 13.1 创建 WebSocket 客户端模块
    - 创建 static/js/modules/ 目录
    - 创建 static/js/modules/websocket.js
    - 实现 WebSocketClient 类（使用 socket.io-client）
    - 实现自动重连逻辑（最多 5 次，指数退避）
    - 实现事件订阅机制（on, off, emit）
    - _Requirements: 6.5_

  - [x] 13.2 集成浏览器通知
    - 创建 static/js/modules/notification.js
    - 实现 NotificationManager 类
    - 实现浏览器通知权限请求（Notification.requestPermission）
    - 实现桌面通知发送（new Notification）
    - 实现点击通知跳转到告警详情
    - _Requirements: 8.1, 8.2, 8.4_

  - [ ]* 13.3 编写浏览器通知属性测试
    - 创建 tests/frontend/test_notification.js（使用 Jest + fast-check）
    - **Property 18: Browser Notification for Critical Alerts**
    - **Validates: Requirements 8.2**

  - [x] 13.4 更新仪表盘页面
    - 更新 templates/dashboard.html 引入 socket.io 客户端
    - 集成 WebSocket 连接和订阅
    - 实现实时数据更新（平滑更新图表和数值）
    - 实现告警通知显示
    - 实现轮询回退机制（WebSocket 不可用时）
    - _Requirements: 7.1, 7.3, 7.4, 7.5_

- [x] 14. Checkpoint - 实时通信验证
  - 打开仪表盘页面确保 WebSocket 连接正常
  - 创建新告警确保实时推送到页面
  - 确保仪表盘数据实时更新
  - 测试浏览器通知（高危告警）
  - 运行 pytest tests/ 确保所有测试通过
  - 如有问题请询问用户

- [x] 15. AI 分析增强
  - [x] 15.1 实现 AI 服务核心
    - 创建 services/ai_service.py
    - 实现 AIService 类
    - 实现 _get_client() 方法初始化 OpenAI 客户端
    - 实现 _sanitize_data(data) 方法脱敏敏感字段
    - _Requirements: 9.1, 9.6_

  - [ ]* 15.2 编写 AI 数据脱敏属性测试
    - 创建 tests/test_ai.py
    - **Property 17: AI Data Sanitization**
    - **Validates: Requirements 9.6**

  - [x] 15.3 实现日志分析功能
    - 实现 analyze_logs(logs, stream=False) 方法
    - 实现 _build_log_analysis_prompt(logs) 构建提示词
    - 实现 _stream_completion(prompt) 流式响应
    - 实现 _get_completion(prompt) 普通响应
    - _Requirements: 9.2, 9.3_

  - [x] 15.4 实现威胁检测功能
    - 实现 detect_threats(data) 方法
    - 实现 _build_threat_detection_prompt(data) 构建提示词
    - 返回格式：threats 列表（含 confidence, recommendation）+ overall_risk
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ]* 15.5 编写威胁检测属性测试
    - **Property 20: Threat Detection Response Completeness**
    - **Property 21: Threat Detection Risk Rating**
    - **Validates: Requirements 10.2, 10.3, 10.4**

  - [x] 15.6 实现错误处理和速率限制
    - 更新 requirements.txt 添加依赖：flask-limiter
    - 实现 API 调用错误处理（try/except OpenAI 异常）
    - 实现速率限制装饰器（如 10 次/分钟）
    - 实现错误日志记录
    - _Requirements: 9.4, 9.5_

  - [ ]* 15.7 编写 AI 错误处理属性测试
    - **Property 18: AI Error Handling**
    - **Property 19: AI Rate Limiting**
    - **Validates: Requirements 9.4, 9.5**

  - [x] 15.8 更新 AI 分析 API 端点
    - 更新 app.py 中 /api/ai/analyze-logs 使用 AIService
    - 更新 /api/ai/detect-threats 使用 AIService
    - 添加流式响应端点 GET /api/ai/analyze-logs/stream（使用 SSE）
    - 支持自定义提示词参数（custom_prompt）
    - _Requirements: 9.2, 9.3, 10.5_

  - [x] 15.9 更新 AI 分析页面
    - 更新 templates/ai.html 支持流式响应显示（EventSource）
    - 添加加载状态指示（spinner）
    - 添加错误处理显示（友好错误消息）
    - _Requirements: 9.3_

- [x] 16. Checkpoint - AI 功能验证
  - 配置 OPENAI_API_KEY 环境变量
  - 测试 AI 日志分析功能
  - 测试 AI 威胁检测功能
  - 测试流式响应显示
  - 测试错误处理和速率限制
  - 运行 pytest tests/test_ai.py 确保所有测试通过
  - 如有问题请询问用户

- [x] 17. 前端代码重构 - 模块化
  - [x] 17.1 创建前端构建配置
    - 在 security-platform-flask 目录运行 npm init -y
    - 运行 npm install esbuild --save-dev
    - 创建 build.js 构建脚本（打包 ES6 模块）
    - 配置模块打包输出到 static/dist/
    - 更新 .gitignore 忽略 node_modules
    - _Requirements: 11.5_

  - [x] 17.2 创建 API 客户端模块
    - 创建 static/js/modules/api.js
    - 实现 ApiClient 类（baseUrl, request, get, post, patch, delete）
    - 实现 ApiError 类（code, message, status）
    - 处理统一响应格式（success, data, error）
    - _Requirements: 11.3_

  - [x] 17.3 创建通知模块
    - 更新 static/js/modules/notification.js
    - 实现页面内通知（success, error, warning, info 方法）
    - 实现通知容器和自动消失
    - 整合浏览器桌面通知功能
    - _Requirements: 11.3, 12.5_

  - [x] 17.4 创建工具函数模块
    - 创建 static/js/modules/utils.js
    - 实现 formatTime(isoString) 时间格式化
    - 实现 formatNumber(num) 数字格式化（千分位）
    - 实现 debounce(fn, delay) 防抖函数
    - 实现 throttle(fn, delay) 节流函数
    - _Requirements: 11.3_

- [x] 18. 前端代码重构 - 通用组件
  - [x] 18.1 创建数据表格组件
    - 创建 static/js/modules/components/ 目录
    - 创建 static/js/modules/components/data-table.js
    - 实现 DataTable 类（container, columns, data, options）
    - 支持排序功能（点击列头排序）
    - 支持筛选功能（搜索框）
    - 支持分页功能（页码、每页条数）
    - 支持自定义列渲染（render 函数）
    - _Requirements: 12.1, 12.2_

  - [x] 18.2 创建模态框组件
    - 创建 static/js/modules/components/modal.js
    - 实现 Modal 类（title, content, buttons）
    - 支持确认对话框（confirm 静态方法）
    - 支持表单对话框（form 静态方法）
    - 支持关闭回调
    - _Requirements: 12.1, 12.3_

  - [x] 18.3 创建加载指示器组件
    - 创建 static/js/modules/components/loading.js
    - 实现 Loading 类
    - 实现全局加载遮罩（show, hide 方法）
    - 实现按钮加载状态（setLoading 方法）
    - _Requirements: 12.1, 12.4_

  - [x] 18.4 更新样式文件
    - 更新 static/style.css 添加通知样式（.notification, .notification-success 等）
    - 添加模态框样式（.modal, .modal-overlay, .modal-content）
    - 添加加载指示器样式（.loading-overlay, .spinner）
    - 添加数据表格样式（.data-table, .sortable, .pagination）
    - _Requirements: 12.5_

- [x] 19. 前端代码重构 - 错误处理
  - [x] 19.1 实现全局错误处理
    - 创建 static/js/modules/error-handler.js
    - 实现 window.onerror 处理（捕获未处理异常）
    - 实现 window.onunhandledrejection 处理（捕获 Promise 拒绝）
    - 实现错误类型映射（NETWORK_ERROR, UNAUTHORIZED, FORBIDDEN 等）
    - 根据错误类型显示不同提示
    - _Requirements: 13.1, 13.2, 13.4_

  - [ ]* 19.2 编写前端错误处理属性测试
    - 创建 tests/frontend/test_error_handler.js
    - **Property 30: Frontend Error Type Differentiation**
    - **Validates: Requirements 13.4**

  - [x] 19.3 实现离线检测
    - 在 error-handler.js 添加离线检测
    - 实现 navigator.onLine 监听（online/offline 事件）
    - 实现离线状态提示（显示离线横幅）
    - _Requirements: 13.3_

  - [x] 19.4 实现错误日志记录
    - 在 error-handler.js 添加控制台日志
    - 记录错误详情（message, source, lineno）
    - 记录堆栈信息（error.stack）
    - 记录时间戳
    - _Requirements: 13.5_

- [x] 20. 前端代码重构 - 页面模块化
  - [x] 20.1 重构仪表盘页面
    - 创建 static/js/pages/ 目录
    - 创建 static/js/pages/dashboard.js
    - 使用 ApiClient 获取数据
    - 使用 Loading 组件显示加载状态
    - 集成 WebSocket 实时更新
    - _Requirements: 11.4_

  - [x] 20.2 重构资产管理页面
    - 创建 static/js/pages/assets.js
    - 使用 DataTable 组件显示资产列表
    - 使用 Modal 组件实现添加/编辑资产
    - 使用 ApiClient 进行 CRUD 操作
    - _Requirements: 11.4_

  - [x] 20.3 重构漏洞管理页面
    - 创建 static/js/pages/vulnerabilities.js
    - 使用 DataTable 组件显示漏洞列表
    - 使用 Modal 组件实现漏洞详情/状态更新
    - _Requirements: 11.4_

  - [x] 20.4 重构事件响应页面
    - 创建 static/js/pages/incidents.js
    - 使用 DataTable 组件显示事件列表
    - 使用 Modal 组件实现事件详情/时间线
    - _Requirements: 11.4_

  - [x] 20.5 重构其他页面
    - 创建 static/js/pages/threat-intel.js（威胁情报）
    - 创建 static/js/pages/compliance.js（合规管理）
    - 创建 static/js/pages/reports.js（报表）
    - 创建 static/js/pages/settings.js（设置）
    - 创建 static/js/pages/ai.js（AI 分析）
    - _Requirements: 11.4_

  - [x] 20.6 创建主入口文件
    - 创建 static/js/main.js 主入口
    - 初始化全局错误处理（ErrorHandler.init）
    - 初始化通知系统（NotificationManager.init）
    - 初始化 WebSocket 连接（WebSocketClient.connect）
    - 根据页面 data-page 属性加载对应模块
    - _Requirements: 11.1, 11.2_

  - [x] 20.7 更新模板文件
    - 更新 templates/base.html 引用打包后的 JS（static/dist/main.js）
    - 为各页面 body 添加 data-page 属性
    - 更新各页面模板移除内联 JS
    - _Requirements: 11.1_

- [x] 21. Final Checkpoint - 完整功能验证
  - 运行 npm run build 确保前端构建正常
  - 运行 flask run 启动应用
  - 测试登录/登出功能
  - 测试各页面功能（资产、漏洞、事件、威胁情报、合规、报表）
  - 测试 WebSocket 实时更新
  - 测试 AI 分析功能
  - 运行 pytest tests/ 确保所有测试通过
  - 如有问题请询问用户

## Notes

- 任务标记 `*` 的为可选属性测试任务，可跳过以加快 MVP 开发
- 每个 Checkpoint 后应确保平台可正常运行
- 数据库迁移应在开发环境充分测试后再应用到生产
- AI 功能需要配置有效的 OPENAI_API_KEY 环境变量
- 前端构建需要 Node.js 环境（建议 v18+）
- 默认管理员账户：admin / admin123（首次运行 seed_data.py 创建）
- 测试框架：pytest + hypothesis（后端），Jest + fast-check（前端）
