# Tripy-Web

## PT0 简介

Tripy-Web 是一个基于 FastAPI 的简单博客与小游戏演示项目，适合课程实验和前后端分离开发入门。

## PT1 服务支持

### 环境要求

- Python 3.13.5
- FastAPI 0.115.13
- Uvicorn 0.34.3

### 安装依赖

在终端执行：

```bash
pip install "fastapi[standard]"
pip install uvicorn
pip install python-jose
# 如需数据库支持再安装
# pip install sqlalchemy
```
###启动服务
打开终端，切换到项目根目录（如 d:\pycode\Tripy-Web）：
cd d:\pycode\Tripy-Web
启动 FastAPI 服务：
uvicorn main:app --reload
访问接口文档：

http://127.0.0.1:8000/docs

访问前端页面（静态文件）：

http://127.0.0.1:8000/static/index.html
PT2 测试
主页访问：http://127.0.0.1:8000/static/index.html
博客管理：http://127.0.0.1:8000/static/blog_frontend.html
冲浪小游戏：http://127.0.0.1:8000/static/surf_combined.html
登录/注册：http://127.0.0.1:8000/static/login.html
如有问题请在 issues 区反馈。