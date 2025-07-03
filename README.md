# Tripy-Web

## PT0 简介

Tripy-Web 是一个基于 FastAPI 的简单博客与小游戏演示项目，适合课程实验和前后端分离开发入门。
### 开发环境

- Python 3.13.5
- Node.js >= 18.x（当前 v22.17.0）
- npm >= 9.x（当前 v10.9.2）
- 推荐使用 PowerShell 或 Bash 等支持脚本执行的终端


## PT1 启动
### git库克隆
```bash
git clone https://github.com/shxYue/Tripy-Web.git
```
#如果弹出输入用户名和密码的提示，请输入你的 GitHub 用户名和密码（或使用个人访问令牌）。
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 安装依赖

在项目根目录下执行：

```powershell
# 创建并激活虚拟环境
# 临时放开执行策略
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass（如遇到授权失败）
# 激活新虚拟环境
.\venv\Scripts\activate
# !!一定要确认是开发版本（3.13.5）（python --version）
py -3.13 -m venv venv
#or
python -m venv venv
# Windows PowerShell 下激活
.\venv\Scripts\activate
# Linux/macOS 下激活
source venv/bin/activate

# 使用 requirements.txt 安装所有依赖
pip install -r requirements.txt
#（若网络受限，可加镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果想单独安装，也可执行：

```bash
pip install "fastapi[standard]" uvicorn python-jose sqlalchemy "passlib[bcrypt]"
```

### 启动服务
打开终端，切换到项目根目录
cd d:\pycode\Tripy-Web

# 推荐方式：使用脚本启动，会自动读取 `.env` 端口
```powershell
venv\Scripts\activate
python main.py
```

# 如果仍想使用 uvicorn CLI（需手动指定端口）
```powershell
venv\Scripts\activate
uvicorn main:app --reload --port $Env:TUNNEL_PORT
```

访问接口文档：

http://127.0.0.1:8000/docs

访问前端页面（静态文件）：

http://127.0.0.1:8000/static/pages/index.html
PT2 测试
主页访问：http://127.0.0.1:8000/static/pages/index.html
博客管理：http://127.0.0.1:8000/static/pages/blog_frontend.html
恐龙游戏：http://127.0.0.1:8000/static/pages/dino_game.html
登录/注册：http://127.0.0.1:8000/static/pages/login.html
如有问题请在 issues 区反馈。
### 主要文件夹结构说明

```
Tripy-Web/
├── main.py                # FastAPI 主入口
├── blog.py                # 博客相关后端逻辑
├── db.py                  # 数据库相关操作
├── models.py              # 数据模型定义
├── static/                # 前端静态资源（HTML/CSS/JS）
│   ├── index.html         # 主页
│   ├── blog_frontend.html # 博客前端页面
│   ├── surf_combined.html # 冲浪小游戏页面
│   └── ...
├── __pycache__/           # Python 编译缓存
├── 测试/                  # 测试相关文件
├── README.md              # 项目说明文档
└── ...
```

- 后端代码集中在根目录及 app/ 子目录（如有）。
- 静态资源统一放在 static/ 文件夹，便于前后端分离。
- 推荐使用虚拟环境（如 venv）管理依赖，避免全局污染。
- 代码和文档建议定期同步至远程仓库（如 GitHub）。

如有问题请在 issues 区反馈。

---
