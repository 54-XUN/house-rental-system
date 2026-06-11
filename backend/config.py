import os
import sys


def 获取数据库目录() -> str:
    """获取数据库文件存放目录"""
    if getattr(sys, 'frozen', False):
        # 打包模式：exe所在目录/data
        return os.path.join(os.path.dirname(sys.executable), 'data')
    else:
        # 开发模式：backend/data目录
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


basedir = 获取数据库目录()
os.makedirs(basedir, exist_ok=True)
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "house_rent.db")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
