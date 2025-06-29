# Tripy-Web

PT0 简介

Test items for the course

代码基于python 3.13.5 fastapi 0.115.13 unicorn 0.34.3

运行前需要安装fastapi&uvicorn 

PT1 服务支持

安装fastapi：终端：pip install "fastapi[standard]"

安装uvicorn：终端：pip install uvicorn

运行时先将终端定位到代码所在位置：使用命令：cd:\code\.vscode  #注意是你的电脑的代码所在文件夹路径

启动服务：uvicorn blog:app --reload

PT2 测试
- 主页访问：[http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)