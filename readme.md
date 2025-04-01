# qtask - 任务跟踪系统

#### 介绍
基于Streamlit开发的轻量级任务管理系统，适合小团队协作使用。主要功能包括：
- 用户登录验证
- 任务创建、编辑和状态管理
- 任务分组显示
- 图片和附件上传
- 任务截止日期提醒

#### 软件架构
- 前端：Streamlit框架
- 后端：SQLite数据库
- 文件存储：本地uploads目录
- 主要模块：
  - 用户认证模块
  - 任务管理模块
  - 文件上传模块
  - 界面展示模块

#### 安装教程

1. 安装Python 3.7+
2. 安装依赖库：
```bash
pip install streamlit sqlite3

安装教程1. 安装Python 3.7+2. 安装依赖库：```bashpip install streamlit sqlite3
克隆仓库或下载代码：
bash
运行
git clone https://your-repository-url.git
初始化数据库：
bash
运行
streamlit run app.py
(首次运行会自动创建数据库)

使用说明
登录系统

首次使用需手动在数据库中添加用户
用户名不区分大小写，自动去除前后空格
任务管理

新建任务：点击"➕New"按钮
编辑任务：点击任务卡片中的"Change Task"按钮
关闭任务：点击任务卡片中的"Close Task"按钮
查看已完成任务：点击"✅Closed"按钮
任务分组

任务可按自定义分组显示
分组在config.py中配置
文件上传

支持图片(png/jpg/jpeg)上传
支持附件(pdf/docx/xlsx)上传
文件存储在uploads目录
截止日期提醒

7天内到期：🔥 图标标记
7-14天到期：⏰ 图标标记
配置说明
编辑config.py文件可配置：

任务分组选项
图片显示尺寸
其他界面参数
数据库结构
sql

-- 任务表CREATE TABLE tasks (    id INTEGER PRIMARY KEY AUTOINCREMENT,    name TEXT NOT NULL,    due_date TEXT,    details TEXT,    picture BLOB,    attachment TEXT,    remark TEXT DEFAULT 'open',    category TEXT);-- 用户表CREATE TABLE users (    id INTEGER PRIMARY KEY AUTOINCREMENT,    username TEXT UNIQUE NOT NULL,    password TEXT NOT NULL);
参与贡献
Fork 本仓库
新建 Feat_xxx 分支
提交代码
新建 Pull Request
注意事项
生产环境建议加密用户密码
定期备份uploads目录和database.db文件
移动端适配已优化，但建议在PC端获得最佳体验