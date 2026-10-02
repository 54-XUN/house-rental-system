"""
出租屋管理系统 - 启动脚本（PyInstaller入口）
功能：启动Flask后端 + 用pywebview打开窗口（最大化显示，无黑屏/白屏闪烁）
"""
import os
import sys
import threading
import time
import traceback
import urllib.request
import webview
from screeninfo import get_monitors


def 获取项目根目录():
    """获取项目根目录（打包模式用 _MEIPASS，开发模式用本文件所在目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包模式：从临时解压目录读取嵌入的资源文件
        return sys._MEIPASS
    else:
        # 开发模式：启动脚本.py 位于项目根目录
        return os.path.dirname(os.path.abspath(__file__))


def 写入启动错误日志(异常对象):
    """把启动异常写到 exe 所在目录的 startup_error.log，方便用户排查"""
    try:
        if getattr(sys, 'frozen', False):
            日志目录 = os.path.dirname(sys.executable)
        else:
            日志目录 = os.path.dirname(os.path.abspath(__file__))
        日志路径 = os.path.join(日志目录, 'startup_error.log')
        with open(日志路径, 'w', encoding='utf-8') as f:
            f.write(f"启动失败: {type(异常对象).__name__}: {异常对象}\n\n")
            f.write(traceback.format_exc())
        return 日志路径
    except Exception:
        return None


def 启动flask后端():
    """在后台线程中启动Flask服务"""
    try:
        项目根目录 = 获取项目根目录()
        # 将后端目录加入Python路径
        后端目录 = os.path.join(项目根目录, 'backend')
        if 后端目录 not in sys.path:
            sys.path.insert(0, 后端目录)

        from app import 创建应用
        app = 创建应用()
        app.run(port=5000, use_reloader=False)
    except Exception as e:
        写入启动错误日志(e)
        raise


def 等待后端就绪(地址):
    """轮询 /api/health 接口直到 Flask 就绪，避免弹窗后白屏等待"""
    重试次数 = 0
    最大重试 = 60  # 最多等30秒
    while 重试次数 < 最大重试:
        try:
            req = urllib.request.Request(f'{地址}/api/health')
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        重试次数 += 1
        time.sleep(0.5)
    return False


def main():
    # 在后台线程启动Flask
    flask_thread = threading.Thread(target=启动flask后端, daemon=True)
    flask_thread.start()

    # 等待Flask就绪后再弹窗（解决黑屏/白屏闪烁问题）
    地址 = 'http://127.0.0.1:5000'
    print("等待后端服务启动...")
    if not 等待后端就绪(地址):
        print("错误：后端服务启动超时！")
        # 打包模式下自动打开错误日志
        if getattr(sys, 'frozen', False):
            日志路径 = os.path.join(os.path.dirname(sys.executable), 'startup_error.log')
            if os.path.exists(日志路径):
                try:
                    os.startfile(日志路径)  # 自动用记事本打开
                except Exception:
                    pass
        input("按回车键退出...")
        sys.exit(1)

    print("后端就绪，打开窗口...")

    # 用 screeninfo 获取主屏尺寸，实现最大化（保留任务栏，非全屏）
    屏幕 = get_monitors()[0]
    webview.create_window(
        title='房屋出租管理系统',
        url=地址,
        width=屏幕.width,
        height=屏幕.height,
        x=屏幕.x,
        y=屏幕.y,
        background_color='#FFFFFF',
        min_size=(960, 640),
    )
    webview.start()


if __name__ == '__main__':
    main()
