import subprocess, os, sys, shutil, datetime

项目根目录 = os.path.dirname(os.path.abspath(__file__))
输出目录 = os.path.join(项目根目录, 'package')
日志文件 = os.path.join(输出目录, 'build_log.txt')

os.makedirs(输出目录, exist_ok=True)

# 清理
for d in ['dist', 'build']:
    p = os.path.join(输出目录, d)
    if os.path.exists(p):
        shutil.rmtree(p)

# 删除旧spec
spec = os.path.join(输出目录, '房屋出租管理系统.spec')
if os.path.exists(spec):
    os.remove(spec)

图标 = os.path.join(项目根目录, 'icon.ico')
图标参数 = f'--icon={图标}' if os.path.exists(图标) else ''

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--windowed', '--onefile', '--clean',
    '--name', '房屋出租管理系统',
    f'--distpath={os.path.join(输出目录, "dist")}',
    f'--workpath={os.path.join(输出目录, "build")}',
    f'--specpath={输出目录}',
    图标参数,
    f'--add-data={os.path.join(项目根目录, "frontend", "dist")};frontend\\dist',
    f'--add-data={os.path.join(项目根目录, "backend", "models")};backend\\models',
    f'--add-data={os.path.join(项目根目录, "backend", "routes")};backend\\routes',
    f'--add-data={os.path.join(项目根目录, "backend", "utils")};backend\\utils',
    f'--add-data={os.path.join(项目根目录, "backend", "config.py")};backend',
    f'--add-data={os.path.join(项目根目录, "backend", "app.py")};backend',
    '--hidden-import=webview', '--hidden-import=flask',
    '--hidden-import=flask_cors', '--hidden-import=flask_sqlalchemy',
    '--hidden-import=openpyxl', '--hidden-import=sqlalchemy',
    '--hidden-import=screeninfo',
    '--hidden-import=werkzeug', '--hidden-import=jinja2', '--hidden-import=markupsafe',
    '--collect-all', 'webview', '--collect-all', 'flask',
    '--noconfirm',
    os.path.join(项目根目录, '启动脚本.py')
]

with open(日志文件, 'w', encoding='utf-8') as f:
    f.write(f'开始时间: {datetime.datetime.now()}\n')
    f.write(f'命令: {" ".join(cmd)}\n\n')

    result = subprocess.run(cmd, cwd=项目根目录, stdout=f, stderr=subprocess.STDOUT)

    f.write(f'\n退出码: {result.returncode}\n')
    f.write(f'结束时间: {datetime.datetime.now()}\n')

# 检查结果
exe路径 = os.path.join(输出目录, 'dist', '房屋出租管理系统.exe')
if os.path.exists(exe路径):
    size_mb = os.path.getsize(exe路径) / (1024 * 1024)
    with open(日志文件, 'a', encoding='utf-8') as f:
        f.write(f'\n=== 打包成功 ===\n')
        f.write(f'文件: {exe路径}\n')
        f.write(f'大小: {size_mb:.2f} MB\n')
    print(f'OK {size_mb:.2f}MB')
else:
    with open(日志文件, 'a', encoding='utf-8') as f:
        f.write('\n=== 打包失败 ===\n')
    print('FAIL')
