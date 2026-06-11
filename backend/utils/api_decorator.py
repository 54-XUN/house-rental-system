"""
路由异常处理统一装饰器

用法:
    @api_handler("操作名称", 需要回滚=True)
    def 视图函数():
        # 直接写业务逻辑，无需try/except
        ...
"""
import logging
from functools import wraps
from flask import jsonify, Response
from werkzeug.exceptions import HTTPException
from models import db
from utils.helpers import 构建响应, 构建错误响应

logger = logging.getLogger(__name__)


def api_handler(操作名称: str, 需要回滚: bool = True):
    """
    统一异常处理装饰器

    参数:
        操作名称: 用于日志和错误消息的操作描述
        需要回滚: 写操作为True（失败时rollback），读操作为False
    """
    def 装饰器(视图函数):
        @wraps(视图函数)
        def wrapper(*args, **kwargs):
            try:
                return 视图函数(*args, **kwargs)
            except HTTPException:
                # 让Flask自己处理404/405等HTTP异常
                raise
            except Exception as e:
                if 需要回滚:
                    db.session.rollback()
                return jsonify(构建错误响应(e, 操作名称))
        return wrapper
    return 装饰器
