# -*- mode: python ; coding: utf-8 -*-
"""房屋出租管理系统 - PyInstaller 打包配置"""
import os
项目根 = os.path.abspath(SPECPATH)

a = Analysis(
    ['启动脚本.py'],
    pathex=[项目根],
    binaries=[],
    datas=[
        # 前端构建产物
        (os.path.join(项目根, 'frontend', 'dist'), 'frontend/dist'),
        # 后端模块
        (os.path.join(项目根, 'backend', 'models'), 'backend/models'),
        (os.path.join(项目根, 'backend', 'routes'), 'backend/routes'),
        (os.path.join(项目根, 'backend', 'utils'), 'backend/utils'),
        (os.path.join(项目根, 'backend', 'app.py'), 'backend'),
        (os.path.join(项目根, 'backend', 'config.py'), 'backend'),
    ],
    hiddenimports=[
        'flask', 'flask_cors', 'flask_sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'webview.platforms.winforms', 'webview.platforms.edgechromium',
        'webview.http', 'bottle',
        'clr_loader', 'pythonnet',
        'werkzeug', 'jinja2', 'markupsafe', 'screeninfo',
    ],
    hookspath=[],
    # 排除无用库，减小体积、降低杀软误报
    excludes=[
        'webview.platforms.gtk', 'webview.platforms.qt',
        'webview.platforms.cocoa', 'webview.platforms.android',
        'webview.platforms.mshtml', 'webview.platforms.cef',
        'pandas', 'numpy', 'scipy', 'matplotlib',
        'tkinter', 'ttkbootstrap',
    ],
    runtime_hooks=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='房屋出租管理系统',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,                # 无黑窗口
    icon=os.path.join(项目根, 'icon.ico'),
    disable_windowed_traceback=False,
)
