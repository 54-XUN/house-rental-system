import os
import sys


def 获取数据库目录() -> str:
    """获取数据库文件存放目录（兼容开发模式与 PyInstaller 打包模式）

    策略：
    - 开发模式：使用 backend/data/ 目录
    - 打包模式：使用 %APPDATA%/房屋出租管理系统/ 目录
      （避免 Program Files 等只读目录无法写入，
       且用户换电脑/重装系统不会丢失数据）
    """
    if getattr(sys, 'frozen', False):
        # 打包模式：放到用户 AppData 目录
        appdata = os.environ.get('APPDATA')
        if appdata:
            data_dir = os.path.join(appdata, '房屋出租管理系统')
        else:
            # 兜底：exe 所在目录
            data_dir = os.path.join(os.path.dirname(sys.executable), 'data')
    else:
        # 开发模式：backend/data 目录
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


basedir = 获取数据库目录()
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "house_rent.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
