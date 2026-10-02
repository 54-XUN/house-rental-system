# 房屋出租管理系统

基于 Flask + Vue3 的房屋出租管理系统，前后端分离，可打包为单文件 EXE（pywebview 桌面窗口）。

## 技术栈

- 后端：Flask + SQLAlchemy（SQLite）
- 前端：Vue3 + Element Plus + ECharts
- 打包：PyInstaller

## 开发启动

```powershell
.venv\Scripts\python.exe 启动脚本.py
```

启动后自动打开桌面窗口，也可用浏览器访问 http://127.0.0.1:5000

## 运行测试

```powershell
.venv\Scripts\python.exe -m pytest backend/tests
```

## 打包 EXE

```powershell
.venv\Scripts\python.exe build.py
```

产物在 `package/dist/`。

## 项目结构

```
backend/          Flask 后端（API + 数据模型）
frontend/         Vue3 前端源码
docs/             开发规范
build.py          一键打包脚本（构建前端 + PyInstaller 打包）
build.spec        PyInstaller 配置
启动脚本.py        开发/打包通用入口
generate_data.py  生成测试数据
icon.ico          应用图标
```
