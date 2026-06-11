import logging
from datetime import datetime, timedelta
from models.setting import 设置模型

# 配置日志系统（O-07优化）
logger = logging.getLogger(__name__)


def 计算房源状态(到期日期字符串: str) -> str:
    """
    根据到期日期计算房源状态
    
    规则：
    - 如果到期日为空 → 空闲
    - 如果到期日已过（<=今天）→ 已租
    - 如果到期日在未来但 <= 今天+提前天数 → 即将到期
    - 如果到期日在今天+提前天数之后 → 已租
    
    参数:
        到期日期字符串: 到期日期，格式 YYYY-MM-DD
    返回:
        状态字符串: "空闲"/"已租"/"即将到期"
    """
    if not 到期日期字符串:
        return '空闲'
    
    try:
        到期日 = datetime.strptime(到期日期字符串, '%Y-%m-%d')
        今天 = datetime.now()
        
        # 获取即将到期的天数设置（W-04优化：减少数据库查询）
        提前天数 = 获取即将到期天数()
        
        # 计算即将到期的截止日期
        即将到期截止日 = 今天 + timedelta(days=提前天数)
        
        if 到期日 <= 今天:
            return '已租'
        elif 到期日 <= 即将到期截止日:
            return '即将到期'
        else:
            return '已租'
            
    except (ValueError, TypeError) as e:
        logger.warning(f"解析到期日期失败: {到期日期字符串}, 错误: {e}")
        return '空闲'


# W-04优化：缓存expiring_days到模块级变量
_缓存即将到期天数: int = 30
_缓存时间戳: float = 0


def 获取即将到期天数() -> int:
    """
    获取即将到期的天数设置（带5分钟缓存）
    
    返回:
        天数整数，默认30天
    """
    global _缓存即将到期天数, _缓存时间戳
    
    当前时间戳 = datetime.now().timestamp()
    
    # 缓存5分钟
    if 当前时间戳 - _缓存时间戳 < 300 and _缓存即将到期天数 > 0:
        return _缓存即将到期天数
    
    try:
        设置项 = 设置模型.query.filter_by(key='expiring_days').first()
        if 设置项 and 设置项.value:
            _缓存即将到期天数 = int(设置项.value)
        else:
            _缓存即将到期天数 = 30
        _缓存时间戳 = 当前时间戳
        return _缓存即将到期天数
    except Exception:
        return 30


def 更新所有房源状态() -> None:
    """更新所有已租/即将到期房源的状态"""
    from models.house import 房源模型
    from models import db
    
    try:
        已租房源列表 = 房源模型.query.filter(
            房源模型.status.in_(['已租', '即将到期'])
        ).all()
        
        for 房源 in 已租房源列表:
            if 房源.expire_date:
                房源.status = 计算房源状态(房源.expire_date)
        
        db.session.commit()
    except Exception as e:
        logger.error(f"更新房源状态失败: {e}")
        db.session.rollback()


def 构建响应(代码: int, 数据, 消息: str = "成功") -> dict:
    """
    构建标准API响应格式（S-03优化：统一格式）
    
    参数:
        代码: HTTP状态码 (200/400/404/500)
        数据: 响应数据（任意类型）
        消息: 响应消息
    返回:
        标准字典格式
    """
    return {
        'code': 代码,
        'data': 数据,
        'msg': 消息
    }


def 构建错误响应(错误对象: Exception, 操作名称: str = "操作") -> dict:
    """
    构建安全的错误响应（S-03核心修复）
    
    不泄露内部错误细节给前端，仅记录到日志
    
    参数:
        错误对象: Python异常实例
        操作名称: 正在执行的操作描述
    返回:
        标准错误响应字典（不含堆栈信息）
    """
    错误类型 = type(错误对象).__name__
    logger.error(f"{操作名称}失败: [{错误类型}] {str(错误对象)}")
    
    # 根据异常类型返回通用消息
    if isinstance(错误对象, ValueError):
        用户消息 = "数据格式错误，请检查输入"
    elif isinstance(错误对象, KeyError):
        用户消息 = "缺少必要的数据字段"
    else:
        用户消息 = f"{操作名称}失败，请稍后重试"
    
    return 构建响应(500, None, 用户消息)
