"""
通用验证和转换工具函数（统一来源，消除helpers.py与excel_import.py的重复）
"""
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def 解析日期(日期值) -> str | None:
    """
    解析日期值为 YYYY-MM-DD 格式字符串

    参数:
        日期值: datetime对象或字符串
    返回:
        格式化后的日期字符串，解析失败返回None
    """
    if 日期值 is None:
        return None

    try:
        if isinstance(日期值, datetime):
            return 日期值.strftime('%Y-%m-%d')

        if isinstance(日期值, str):
            日期值 = 日期值.strip()
            if not 日期值:
                return None

            for 格式 in ('%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日'):
                try:
                    dt = datetime.strptime(日期值, 格式)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        return str(日期值) if 日期值 else None

    except Exception as e:
        logger.warning(f"日期解析异常: {日期值}, 错误: {e}")
        return None


def 解析面积(面积值) -> float | None:
    """
    解析面积值，去除 m² 后缀并转为浮点数

    参数:
        面积值: 数值或字符串
    返回:
        浮点数，解析失败返回None
    """
    if 面积值 is None:
        return None

    try:
        面积字符串 = str(面积值).strip()
        面积字符串 = re.sub(r'[m㎡²]\s*2?', '', 面积字符串).strip()

        if not 面积字符串:
            return None

        return float(面积字符串)

    except (ValueError, TypeError) as e:
        logger.warning(f"面积解析失败: {面积值}, 错误: {e}")
        return None


def 解析标签(标签值) -> str | None:
    """将竖线分隔的标签转换为逗号分隔"""
    if 标签值 is None:
        return None

    标签字符串 = str(标签值).strip()
    if not 标签字符串:
        return None

    if '|' in 标签字符串:
        标签字符串 = 标签字符串.replace('|', ',')

    return 标签字符串


def 安全转整数(值, 默认值: int = None) -> int | None:
    """安全转换为整数"""
    if 值 is None:
        return 默认值
    try:
        return int(值)
    except (ValueError, TypeError):
        return 默认值


def 安全转浮点(值, 默认值: float = None) -> float | None:
    """安全转换为浮点数"""
    if 值 is None:
        return 默认值
    try:
        return float(值)
    except (ValueError, TypeError):
        return 默认值


def 脱敏敏感信息(原始值: str, 显示前: int = 3, 显示后: int = 4) -> str:
    """
    敏感信息脱敏：138****1234

    参数:
        原始值: 原始敏感字符串
        显示前: 前面保留的字符数
        显示后: 后面保留的字符数
    返回:
        脱敏后的字符串
    """
    if not 原始值 or len(原始值) <= 显示前 + 显示后:
        return '****'
    return f'{原始值[:显示前]}{"*" * (len(原始值) - 显示前 - 显示后)}{原始值[-显示后:]}'
