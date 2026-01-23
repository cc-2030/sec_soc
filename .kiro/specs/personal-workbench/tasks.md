# Implementation Plan: Personal Workbench

## Overview

基于 Python 和 Tkinter 实现个人工作台应用，采用分层架构（数据模型层、业务逻辑层、数据持久化层、UI层）。使用 pytest 进行单元测试，hypothesis 进行属性测试。

## Tasks

- [x] 1. 项目结构和基础设置
  - [x] 1.1 创建项目目录结构
    - 创建 `src/` 目录包含 `models/`, `managers/`, `storage/`, `ui/` 子目录
    - 创建 `tests/` 目录包含对应的测试子目录
    - 创建 `requirements.txt` 包含依赖 (hypothesis, pytest, pytest-cov)
    - _Requirements: 5.1_

- [x] 2. 数据模型层实现
  - [x] 2.1 实现 Task 数据模型
    - 创建 `src/models/task.py`
    - 实现 Task dataclass，包含 id, title, description, due_date, completed, created_at, completed_at 字段
    - 实现 `to_dict()` 和 `from_dict()` 序列化方法
    - 实现 `is_overdue()` 方法判断任务是否过期
    - _Requirements: 1.1, 1.2, 1.3, 3.5, 4.5_
  
  - [ ]* 2.2 编写 Task 序列化往返属性测试
    - **Property 11: Task Serialization Round-Trip**
    - **Validates: Requirements 4.5**
  
  - [x] 2.3 实现 Link 数据模型
    - 创建 `src/models/link.py`
    - 实现 Link dataclass，包含 id, name, url, created_at 字段
    - 实现 `to_dict()` 和 `from_dict()` 序列化方法
    - _Requirements: 2.1, 4.6_
  
  - [ ]* 2.4 编写 Link 序列化往返属性测试
    - **Property 12: Link Serialization Round-Trip**
    - **Validates: Requirements 4.6**

- [x] 3. 数据持久化层实现
  - [x] 3.1 实现 Storage 存储模块
    - 创建 `src/storage/storage.py`
    - 实现 JSON 文件读写功能
    - 实现 `load()`, `save()`, `get_tasks()`, `save_tasks()`, `get_links()`, `save_links()` 方法
    - 处理文件不存在和 JSON 解析错误的情况
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 3.2 编写数据持久化一致性属性测试
    - **Property 13: Data Persistence Consistency**
    - **Validates: Requirements 4.2, 4.4**

- [x] 4. Checkpoint - 数据层验证
  - 确保所有数据模型和存储测试通过，如有问题请询问用户。

- [-] 5. 业务逻辑层实现 - TaskManager
  - [x] 5.1 实现 TaskManager 任务管理器
    - 创建 `src/managers/task_manager.py`
    - 实现 `create_task()` 方法，验证标题非空
    - 实现 `update_task()`, `delete_task()`, `complete_task()` 方法
    - 实现 `get_all_tasks()`, `get_pending_tasks()`, `get_completed_tasks()`, `get_overdue_tasks()` 查询方法
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [ ]* 5.2 编写任务创建增加列表属性测试
    - **Property 1: Task Creation Adds to List**
    - **Validates: Requirements 1.1**
  
  - [ ]* 5.3 编写任务完成状态更新属性测试
    - **Property 2: Task Completion Updates State**
    - **Validates: Requirements 1.3**
  
  - [ ]* 5.4 编写任务删除移除列表属性测试
    - **Property 3: Task Deletion Removes from List**
    - **Validates: Requirements 1.5**
  
  - [ ]* 5.5 编写空标题拒绝属性测试
    - **Property 4: Empty Title Rejection**
    - **Validates: Requirements 1.6**
  
  - [ ]* 5.6 编写过期任务识别属性测试
    - **Property 10: Overdue Task Identification**
    - **Validates: Requirements 3.5**

- [-] 6. 业务逻辑层实现 - LinkManager
  - [x] 6.1 实现 LinkManager 链接管理器
    - 创建 `src/managers/link_manager.py`
    - 实现 `add_link()` 方法，验证名称非空和 URL 格式
    - 实现 `update_link()`, `delete_link()` 方法
    - 实现 `get_all_links()` 查询方法
    - 实现 `open_link()` 方法调用默认浏览器
    - 实现静态方法 `validate_url()` 验证 URL 格式
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 6.2 编写链接添加存储属性测试
    - **Property 5: Link Addition Stores in Collection**
    - **Validates: Requirements 2.1**
  
  - [ ]* 6.3 编写链接删除移除属性测试
    - **Property 6: Link Deletion Removes from Collection**
    - **Validates: Requirements 2.4**
  
  - [ ]* 6.4 编写无效 URL 拒绝属性测试
    - **Property 7: Invalid URL Rejection**
    - **Validates: Requirements 2.5**
  
  - [ ]* 6.5 编写空链接名称拒绝属性测试
    - **Property 8: Empty Link Name Rejection**
    - **Validates: Requirements 2.6**

- [-] 7. 业务逻辑层实现 - StatisticsModule
  - [x] 7.1 实现 StatisticsModule 统计模块
    - 创建 `src/managers/statistics_module.py`
    - 实现 `get_total_count()`, `get_completed_count()`, `get_pending_count()`, `get_overdue_count()` 方法
    - 实现 `get_completion_percentage()` 方法，处理除零情况
    - 实现 `get_statistics_summary()` 返回统计摘要字典
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 7.2 编写统计计算正确性属性测试
    - **Property 9: Statistics Calculation Correctness**
    - **Validates: Requirements 3.1, 3.2**

- [x] 8. Checkpoint - 业务逻辑层验证
  - 确保所有业务逻辑测试通过，如有问题请询问用户。

- [-] 9. UI 层实现
  - [x] 9.1 实现主窗口框架
    - 创建 `src/ui/main_window.py`
    - 实现 MainWindow 类，设置窗口标题、大小和简约风格
    - 创建菜单栏和主布局框架
    - 实现 `run()` 方法启动应用
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [x] 9.2 实现任务面板
    - 创建 `src/ui/task_panel.py`
    - 实现任务列表显示，按状态分组（待完成、已完成）
    - 实现添加任务对话框
    - 实现编辑、删除、完成任务的交互
    - 高亮显示过期任务
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 3.4, 3.5, 5.3_
  
  - [ ] 9.3 实现链接面板
    - 创建 `src/ui/link_panel.py`
    - 实现链接列表显示
    - 实现添加链接对话框
    - 实现编辑、删除链接的交互
    - 实现点击链接打开浏览器
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.3_
  
  - [x] 9.4 实现统计面板
    - 创建 `src/ui/stats_panel.py`
    - 显示任务总数、已完成数、完成百分比
    - 显示过期任务数量
    - 实现实时更新统计信息
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 5.3_

- [x] 10. 集成和入口点
  - [x] 10.1 创建应用入口点
    - 创建 `src/main.py`
    - 初始化 Storage, TaskManager, LinkManager, StatisticsModule
    - 创建 MainWindow 并注入依赖
    - 启动应用主循环
    - _Requirements: 4.1, 5.1_
  
  - [x] 10.2 创建模块 __init__.py 文件
    - 创建各目录的 `__init__.py` 文件导出公共接口
    - _Requirements: 5.1_

- [x] 11. Final Checkpoint - 完整功能验证
  - 确保所有测试通过，应用可正常启动运行，如有问题请询问用户。

## Notes

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 开发
- 每个任务都引用了具体的需求条款以确保可追溯性
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
- 使用 hypothesis 库进行属性测试，每个属性测试至少运行 100 次迭代
