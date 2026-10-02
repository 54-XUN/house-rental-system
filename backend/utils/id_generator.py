import threading
from sqlalchemy import func
from models import db
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型

# 编号生成互斥锁，防止并发下产生重复编号
_编号锁 = threading.Lock()


def 生成房源编号() -> str:
    """
    生成房源编号 FY00001 格式（线程安全）

    返回: 格式化的房源编号字符串
    """
    with _编号锁:
        try:
            最大id = db.session.query(func.max(房源模型.id)).scalar()
            if not 最大id:
                return 'FY00001'
            return f'FY{最大id + 1:05d}'
        except Exception:
            return 'FY00001'


def 生成客户编号() -> str:
    """
    生成客户编号 F00001 格式（线程安全）

    返回: 格式化的客户编号字符串
    """
    with _编号锁:
        try:
            最大id = db.session.query(func.max(客户模型.id)).scalar()
            if not 最大id:
                return 'F00001'
            return f'F{最大id + 1:05d}'
        except Exception:
            return 'F00001'


def 生成合同编号() -> str:
    """
    生成合同编号 FYH0001 格式（线程安全）

    返回: 格式化的合同编号字符串
    """
    with _编号锁:
        try:
            最大id = db.session.query(func.max(合同模型.id)).scalar()
            if not 最大id:
                return 'FYH0001'
            return f'FYH{最大id + 1:04d}'
        except Exception:
            return 'FYH0001'
