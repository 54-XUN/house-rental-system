"""
房屋出租管理系统 - 一键打包脚本
用法：.venv\Scripts\python.exe build.py
"""
import os
import shutil
import subprocess
import sys

# 强制 UTF-8 输出（解决 PowerShell 沙箱 GBK 乱码）
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

项目根 = os.path.dirname(os.path.abspath(__file__))
前端目录 = os.path.join(项目根, 'frontend')
dist目录 = os.path.join(项目根, 'package', 'dist')
build目录 = os.path.join(项目根, 'package', 'build')


def 标题(文本):
    print('\n' + '=' * 60)
    print(f'  {文本}')
    print('=' * 60)


def 检查必要文件():
    """检查打包所需文件"""
    标题('检查必要文件')
    必要文件 = [
        ('启动脚本.py', '主入口'),
        ('backend/app.py', 'Flask 后端'),
        ('backend/config.py', '后端配置'),
        ('icon.ico', '应用图标'),
        ('build.spec', '打包配置'),
    ]
    全部存在 = True
    for 文件, 说明 in 必要文件:
        完整路径 = os.path.join(项目根, 文件)
        if os.path.exists(完整路径):
            print(f'  [OK] {说明}: {文件}')
        else:
            print(f'  [NO] 缺少 {说明}: {文件}')
            全部存在 = False
    return 全部存在


def 构建前端():
    """若 frontend/dist 不存在则构建前端"""
    标题('检查前端构建产物')
    dist_index = os.path.join(前端目录, 'dist', 'index.html')
    if os.path.exists(dist_index):
        print('  [OK] 前端已构建，跳过')
        return True

    print('  [...] 正在构建前端...')
    if not os.path.exists(os.path.join(前端目录, 'node_modules')):
        print('  [...] 正在安装前端依赖（首次较慢）...')
        结果 = subprocess.run(['npm', 'install'], cwd=前端目录)
        if 结果.returncode != 0:
            print('  [NO] npm install 失败')
            return False

    结果 = subprocess.run(['npm', 'run', 'build'], cwd=前端目录)
    if 结果.returncode != 0:
        print('  [NO] 前端构建失败')
        return False
    print('  [OK] 前端构建完成')
    return True


def 清理旧产物():
    """清理旧的打包产物"""
    标题('清理旧打包产物')
    for 目录 in (dist目录, build目录):
        if os.path.exists(目录):
            shutil.rmtree(目录)
            print(f'  [OK] 已清理: {os.path.relpath(目录, 项目根)}')


def 执行打包():
    """调用 PyInstaller 打包"""
    标题('执行 PyInstaller 打包')
    print('  [...] 打包中（首次约 2-3 分钟）...')
    结果 = subprocess.run(
        [
            sys.executable, '-m', 'PyInstaller',
            'build.spec',
            '--noconfirm', '--clean',
            f'--distpath={dist目录}',
            f'--workpath={build目录}',
        ],
        cwd=项目根,
    )
    return 结果.returncode == 0


def 验证结果():
    """验证 exe 是否生成"""
    标题('验证打包结果')
    exe路径 = os.path.join(dist目录, '房屋出租管理系统.exe')
    if os.path.exists(exe路径):
        大小mb = os.path.getsize(exe路径) / (1024 * 1024)
        print(f'  [OK] 打包成功！')
        print(f'  文件位置: {exe路径}')
        print(f'  文件大小: {大小mb:.2f} MB')
        print()
        print('  下一步：')
        print('  1. 双击 exe 本机测试')
        print('  2. 拷贝到别的电脑测试（建议虚拟机或别人电脑）')
        return True
    else:
        print(f'  [NO] 未找到生成的 exe: {exe路径}')
        return False


def main():
    print('房屋出租管理系统 - 打包工具 v1.0')
    if not 检查必要文件():
        return 1
    if not 构建前端():
        return 1
    清理旧产物()
    if not 执行打包():
        return 1
    验证结果()
    return 0


if __name__ == '__main__':
    rc = main()
    # 检测是否在交互式终端：非交互时直接退出，不阻塞
    try:
        if sys.stdin and sys.stdin.isatty():
            input('\n按回车键退出...')
    except Exception:
        pass
    sys.exit(rc)
