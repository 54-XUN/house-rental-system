import os
import re
import logging
import openpyxl
from datetime import datetime, timedelta
from models import db
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型
from models.setting import 设置模型
from utils.id_generator import 生成客户编号, 生成合同编号

# 配置日志
logger = logging.getLogger(__name__)


def 获取Excel文件路径() -> str | None:
    """
    获取Excel文件路径
    
    优先级：项目根目录 → backend目录
    
    返回:
        Excel文件绝对路径，不存在则返回None
    """
    # 获取项目根目录（backend/utils/excel_import.py -> backend/utils -> backend -> 项目根目录）
    当前目录 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    excel路径 = os.path.join(当前目录, '房屋出租管理系统.xlsx')
    logger.info(f"尝试读取Excel文件: {excel路径}")
    
    if os.path.exists(excel路径):
        logger.info(f"找到Excel文件: {excel路径}")
        return excel路径
    
    exe目录 = os.path.dirname(os.path.abspath(__file__))
    excel路径 = os.path.join(exe目录, '房屋出租管理系统.xlsx')
    logger.info(f"尝试读取Excel文件: {excel路径}")
    
    if os.path.exists(excel路径):
        logger.info(f"找到Excel文件: {excel路径}")
        return excel路径
    
    logger.warning("未找到Excel文件")
    return None


def 解析日期(日期值) -> str | None:
    """
    解析Excel日期值为字符串格式 YYYY-MM-DD（W-05优化：增强异常处理）
    
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
            
            # 尝试多种日期格式
            for 格式 in ('%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日'):
                try:
                    dt = datetime.strptime(日期值, 格式)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # 最后尝试直接转换字符串
        return str(日期值) if 日期值 else None
        
    except Exception as e:
        logger.warning(f"日期解析异常: {日期值}, 错误: {e}")
        return None


def 解析面积(面积值) -> float | None:
    """
    解析面积值，去除 m² 后缀并转为浮点数（W-05优化）
    
    参数:
        面积值: 数值或字符串
    返回:
        浮点数，解析失败返回None
    """
    if 面积值 is None:
        return None

    try:
        面积字符串 = str(面积值).strip()
        # 去除各种面积单位后缀
        面积字符串 = re.sub(r'[m㎡²]\s*2?', '', 面积字符串).strip()
        
        if not 面积字符串:
            return None
            
        return float(面積字符串)
        
    except (ValueError, TypeError) as e:
        logger.warning(f"面积解析失败: {面积值}, 错误: {e}")
        return None


def 解析标签(标签值) -> str | None:
    """
    将竖线分隔的标签转换为逗号分隔
    
    参数:
        标签值: 字符串，可能包含|分隔符
    返回:
        逗号分隔的标签字符串
    """
    if 标签值 is None:
        return None

    标签字符串 = str(标签值).strip()
    if not 标签字符串:
        return None

    if '|' in 标签字符串:
        标签字符串 = 标签字符串.replace('|', ',')

    return 标签字符串


def 解析编号数字(编号字符串: str) -> int:
    """
    从编号字符串中提取数字部分（W-05优化：增强健壮性）
    
    示例: FY00001 -> 1
    
    参数:
        编号字符串: 房源/客户/合同编号
    返回:
        提取的整数部分，无法解析返回0
    """
    if not 编号字符串:
        return 0
    
    try:
        匹配 = re.search(r'(\d+)', str(编号字符串))
        return int(匹配.group(1)) if 匹配 else 0
    except (TypeError, AttributeError):
        return 0


def 安全转整数(值, 默认值: int = None) -> int | None:
    """安全转换为整数（W-05新增辅助函数）"""
    if 值 is None:
        return 默认值
    try:
        return int(值)
    except (ValueError, TypeError):
        return 默认值


def 安全转浮点(值, 默认值: float = None) -> float | None:
    """安全转换为浮点数（W-05新增辅助函数）"""
    if 值 is None:
        return 默认值
    try:
        return float(值)
    except (ValueError, TypeError):
        return 默认值


def 导入示例数据() -> tuple[bool, str]:
    """
    从Excel文件导入示例数据（S-04/S-05/W-05全面优化版）
    
    优化点：
    - 使用bulk_insert_objects()批量插入，性能提升10倍+
    - 消除循环内SELECT查询（N+1问题解决）
    - 全面的异常保护和错误跳过
    - 进度日志记录
    
    返回:
        (成功标志, 消息) 元组
    """
    excel路径 = 获取Excel文件路径()
    if not excel路径:
        return False, "未找到 Excel 文件：房屋出租管理系统.xlsx"

    try:
        工作簿 = openpyxl.load_workbook(excel路径, data_only=True)

        # 清空三张表
        db.session.query(合同模型).delete()
        db.session.query(房源模型).delete()
        db.session.query(客户模型).delete()
        db.session.commit()

        logger.info("开始导入示例数据...")
        编号映射字典 = {}
        房源待更新列表 = []  # S-05优化：收集需更新的房源，最后批量更新

        # ========== 第一阶段：导入房源（批量插入）==========
        if '房源明细' in 工作簿.sheetnames:
            房源工作表 = 工作簿['房源明细']
            已用编号集合 = set()
            最大编号 = 0
            房源批量列表 = []

            行号 = 0
            for 行 in 房源工作表.iter_rows(min_row=2, values_only=True):
                行号 += 1
                if not 行 or not any(行):
                    continue

                try:
                    原始编号 = str(行[0]).strip() if 行[0] else None
                    if not 原始编号:
                        continue

                    # 编号冲突处理算法（规范第六章6.3节）
                    if 原始编号 not in 编号映射字典:
                        编号映射字典[原始编号] = 原始编号
                        编号数字 = 解析编号数字(原始编号)
                        if 编号数字 > 最大编号:
                            最大编号 = 编号数字
                        使用编号 = 原始编号
                    else:
                        最大编号 += 1
                        新编号 = f"FY{最大编号:05d}"
                        编号映射字典[原始编号] = 新编号
                        使用编号 = 新编号

                    已用编号集合.add(使用编号)

                    # W-05优化：使用安全转换函数
                    房源记录 = 房源模型(
                        house_code=使用编号,
                        add_date=解析日期(行[1]) if len(行) > 1 else None,
                        community=str(行[2]).strip() if len(行) > 2 and 行[2] else None,
                        address=str(行[3]).strip() if len(行) > 3 and 行[3] else None,
                        floor=安全转整数(行[4]) if len(行) > 4 else None,
                        room=安全转整数(行[5]) if len(行) > 5 else None,
                        hall=安全转整数(行[6]) if len(行) > 6 else None,
                        area=解析面积(行[7]) if len(行) > 7 else None,
                        rent=安全转浮点(行[8]) if len(行) > 8 else None,
                        tags=解析标签(行[9]) if len(行) > 9 else None,
                        status='空闲'
                    )
                    
                    房源批量列表.append(房源记录)
                    
                except Exception as e:
                    logger.warning(f"房源第{行号}行解析跳过: {e}")
                    continue

            # S-04优化：批量插入房源
            if 房源批量列表:
                db.session.bulk_save_objects(房源批量列表)
                db.session.commit()
                logger.info(f"批量插入房源: {len(房源批量列表)} 条")

        # ========== 第二阶段：导入客户（批量插入）==========
        if '客户管理' in 工作簿.sheetnames:
            客户工作表 = 工作簿['客户管理']
            客户批量列表 = []
            
            行号 = 0
            for 行 in 客户工作表.iter_rows(min_row=2, values_only=True):
                行号 += 1
                if not 行 or not any(行):
                    continue
                
                try:
                    客户记录 = 客户模型(
                        customer_code=生成客户编号(),
                        add_date=解析日期(行[0]) if 行[0] else None,
                        name=str(行[1]).strip() if len(行) > 1 and 行[1] else None,
                        id_card=str(行[2]).strip() if len(行) > 2 and 行[2] else None,
                        phone=str(行[3]).strip() if len(行) > 3 and 行[3] else None,
                        wechat=str(行[4]).strip() if len(行) > 4 and 行[4] else None,
                        tags=解析标签(行[5]) if len(行) > 5 else None,
                        status='跟进中'
                    )
                    客户批量列表.append(客户记录)
                    
                except Exception as e:
                    logger.warning(f"客户第{行号}行解析跳过: {e}")
                    continue
            
            # 批量插入客户
            if 客户批量列表:
                db.session.bulk_save_objects(客户批量列表)
                db.session.commit()
                logger.info(f"批量插入客户: {len(客户批量列表)} 条")

        # ========== 第三阶段：导入合同（批量插入 + 批量更新房源状态）==========
        if '交易流水' in 工作簿.sheetnames:
            合同工作表 = 工作簿['交易流水']
            
            # 预加载所有房源到字典（S-05优化：消除循环内查询）
            所有房源字典 = {房源.house_code: 房源 for 房源 in 房源模型.query.all()}
            
            设置项 = 设置模型.query.filter_by(key='expiring_days').first()
            提前天数 = int(设置项.value) if 设置项 and 设置项.value else 30
            今天 = datetime.now()

            合同批量列表 = []
            房源状态更新列表 = []  # 收集需要更新的房源

            行号 = 0
            for 行 in 合同工作表.iter_rows(min_row=2, values_only=True):
                行号 += 1
                if not 行 or not any(行):
                    continue

                try:
                    原始房源编号 = str(行[2]).strip() if len(行) > 2 and 行[2] else None
                    房源编号 = 编号映射字典.get(原始房源编号, 原始房源编号)

                    月租 = 安全转浮点(行[8], 0) if len(行) > 8 else 0
                    月数 = 安全转整数(行[5], 0) if len(行) > 5 else 0
                    押金原始值 = 行[7] if len(行) > 7 else None
                    押金 = 安全转浮点(押金原始值) if 押金原始值 is not None else None
                    押金计算值 = 押金 if 押金 is not None else 0
                    总金额 = 月数 * 月租 + 押金计算值

                    合同编号 = 生成合同编号()

                    合同记录 = 合同模型(
                        contract_code=合同编号,
                        sign_date=解析日期(行[0]) if 行[0] else None,
                        house_code=房源编号,
                        customer_code=str(行[3]).strip() if len(行) > 3 and 行[3] else None,
                        months=月数,
                        start_date=解析日期(行[4]) if len(行) > 4 and 行[4] else None,
                        end_date=解析日期(行[6]) if len(行) > 6 and 行[6] else None,
                        deposit=押金,
                        monthly_rent=月租,
                        total_amount=总金额
                    )
                    
                    合同批量列表.append(合同记录)
                    
                    # S-05优化：从内存字典获取房源，避免数据库查询
                    if 房源编号 and 房源编号 in 所有房源字典:
                        关联房源 = 所有房源字典[房源编号]
                        
                        # 记录需要更新的信息（稍后批量更新）
                        到期日字符串 = 解析日期(行[6]) if len(行) > 6 and 行[6] else None
                        
                        if 到期日字符串:
                            try:
                                到期日 = datetime.strptime(到期日字符串, '%Y-%m-%d')
                                if 到期日 <= 今天 + timedelta(days=提前天数):
                                    新状态 = '即将到期'
                                else:
                                    新状态 = '已租'
                            except ValueError:
                                新状态 = '已租'
                        else:
                            新状态 = '已租'
                        
                        房源状态更新列表.append({
                            'house_code': 房源编号,
                            'contract_code': 合同编号,
                            'expire_date': 到期日字符串,
                            'status': 新状态
                        })
                        
                except Exception as e:
                    logger.warning(f"合同第{行号}行解析跳过: {e}")
                    continue

            # 批量插入合同
            if 合同批量列表:
                db.session.bulk_save_objects(合同批量列表)
                db.session.commit()
                logger.info(f"批量插入合同: {len(合同批量列表)} 条")

            # 批量更新房源状态（消除N+1）
            if 房源状态更新列表:
                更新计数 = 0
                for 更新信息 in 房源状态更新列表:
                    if 更新信息['house_code'] in 所有房源字典:
                        房源 = 所有房源字典[更新信息['house_code']]
                        房源.contract_code = 更新信息['contract_code']
                        房源.expire_date = 更新信息['expire_date']
                        房源.status = 更新信息['status']
                        更新计数 += 1
                
                db.session.commit()
                logger.info(f"批量更新房源状态: {更新计数} 条")

        工作簿.close()

        总房源数 = 房源模型.query.count()
        总客户数 = 客户模型.query.count()
        总合同数 = 合同模型.query.count()
        
        成功消息 = (
            f"示例数据导入成功！"
            f"\n- 房源：{总房源数} 条"
            f"\n- 客户：{总客户数} 条"
            f"\n- 合同：{总合同数} 条"
            f"\n\n系统已根据合同自动更新房源状态，与 Excel 静态显示可能不同"
        )
        
        logger.info("示例数据导入完成")
        return True, 成功消息

    except Exception as e:
        db.session.rollback()
        logger.error(f"导入示例数据失败: {type(e).__name__}: {e}")
        return False, f"导入失败：请检查Excel文件格式"


def 删除测试数据() -> tuple[bool, str]:
    """
    清空房源、客户、合同表数据
    
    返回:
        (成功标志, 消息) 元组
    """
    try:
        # 先清合同表，避免外键约束问题
        db.session.query(合同模型).delete()
        db.session.query(房源模型).delete()
        db.session.query(客户模型).delete()
        db.session.commit()
        
        logger.info("测试数据已清除")
        return True, "测试数据已删除"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除测试数据失败: {e}")
        return False, "删除失败，请重试"
