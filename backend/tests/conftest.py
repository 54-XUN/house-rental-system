"""
测试配置：内存SQLite隔离，每个test function完全独立
"""
import os
import sys

# 确保backend目录在路径中（conftest.py 位于 backend/tests/，上一级即 backend/）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试前设置：使用内存数据库
os.environ['TESTING'] = '1'

import pytest
from app import 创建应用, _API令牌


@pytest.fixture(scope='function')
def 客户端():
    """
    每个测试函数独立的Flask客户端
    使用 :memory: SQLite，完全隔离
    """
    app = 创建应用()
    app.config['TESTING'] = True
    # 使用内存数据库，每个fixture创建全新的空库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        from models import db
        db.create_all()

        # 创建带Token头的测试客户端（绕过写操作鉴权）
        test_client = app.test_client()
        test_client.environ_base['HTTP_X_API_TOKEN'] = _API令牌

        yield test_client

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def 应用(客户端):
    """获取app对象（用于不需要HTTP请求的纯逻辑测试）"""
    return 客户端.application
