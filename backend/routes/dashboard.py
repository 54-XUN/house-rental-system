import time
from flask import Blueprint, jsonify, Response
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func
from models import db
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型
from utils.helpers import 构建响应, 构建错误响应, 更新所有房源状态
from utils.api_decorator import api_handler

dashboard_bp = Blueprint('dashboard', __name__)

# 看板状态更新缓存（5分钟）
_最后更新时间 = 0
_缓存间隔 = 300


def 需要更新状态() -> bool:
    global _最后更新时间
    当前时间 = time.time()
    if 当前时间 - _最后更新时间 > _缓存间隔:
        _最后更新时间 = 当前时间
        return True
    return False


@dashboard_bp.route('/dashboard/summary', methods=['GET'])
@api_handler("获取概览统计", 需要回滚=False)
def 获取概览统计() -> Response:
    """获取总览统计：总房源数、本月成交金额、本月成交数、总客户数"""
    if 需要更新状态():
        更新所有房源状态()

    总房源数 = 房源模型.query.count()

    今天 = datetime.now()
    本月第一天 = 今天.replace(day=1).strftime('%Y-%m-%d')

    本月金额 = db.session.query(
        func.coalesce(func.sum(合同模型.total_amount), 0)
    ).filter(合同模型.sign_date >= 本月第一天).scalar()

    本月数量 = 合同模型.query.filter(
        合同模型.sign_date >= 本月第一天
    ).count()

    总客户数 = 客户模型.query.count()

    数据 = {
        'total_houses': 总房源数,
        'month_amount': 本月金额,
        'month_count': 本月数量,
        'total_customers': 总客户数
    }

    return jsonify(构建响应(200, 数据))


@dashboard_bp.route('/dashboard/amount_trend', methods=['GET'])
@api_handler("获取金额趋势", 需要回滚=False)
def 获取金额趋势() -> Response:
    """获取最近15天的成交金额趋势"""
    if 需要更新状态():
        更新所有房源状态()

    结束日期 = datetime.now()
    开始日期 = 结束日期 - timedelta(days=14)

    趋势数据 = []

    for i in range(15):
        当前日期 = (开始日期 + timedelta(days=i)).strftime('%Y-%m-%d')

        当日金额 = db.session.query(
            func.coalesce(func.sum(合同模型.total_amount), 0)
        ).filter(合同模型.sign_date == 当前日期).scalar()

        趋势数据.append({
            'date': 当前日期,
            'amount': 当日金额
        })

    return jsonify(构建响应(200, 趋势数据))


@dashboard_bp.route('/dashboard/customer_trend', methods=['GET'])
@api_handler("获取客户趋势", 需要回滚=False)
def 获取客户趋势() -> Response:
    """获取最近7个月的新增客户趋势"""
    if 需要更新状态():
        更新所有房源状态()

    结束月份 = datetime.now().replace(day=1)
    趋势数据 = []

    for i in range(6, -1, -1):
        目标月份 = (结束月份 - timedelta(days=30*i)).strftime('%Y-%m')

        月初 = f'{目标月份}-01'
        if i == 0:
            月末 = datetime.now().strftime('%Y-%m-%d')
        else:
            下一月 = (结束月份 - timedelta(days=30*(i-1))).replace(day=1)
            月末 = (下一月 - timedelta(days=1)).strftime('%Y-%m-%d')

        当月客户数 = 客户模型.query.filter(
            客户模型.add_date >= 月初,
            客户模型.add_date <= 月末
        ).count()

        趋势数据.append({
            'month': 目标月份,
            'count': 当月客户数
        })

    return jsonify(构建响应(200, 趋势数据))


@dashboard_bp.route('/dashboard/house_status', methods=['GET'])
@api_handler("获取房源状态分布", 需要回滚=False)
def 获取房源状态分布() -> Response:
    """获取房源状态分布：空闲、已租、即将到期、出租率"""
    if 需要更新状态():
        更新所有房源状态()

    总房源数 = 房源模型.query.count()

    空闲数 = 房源模型.query.filter_by(status='空闲').count()
    已租数 = 房源模型.query.filter_by(status='已租').count()
    即将到期数 = 房源模型.query.filter_by(status='即将到期').count()

    出租率 = round((已租数 + 即将到期数) / 总房源数 * 100, 1) if 总房源数 > 0 else 0

    数据 = {
        'vacant': 空闲数,
        'rented': 已租数,
        'expiring': 即将到期数,
        'rate': 出租率
    }

    return jsonify(构建响应(200, 数据))


@dashboard_bp.route('/dashboard/top_communities', methods=['GET'])
@api_handler("获取热门小区", 需要回滚=False)
def 获取热门小区() -> Response:
    """获取房源数量前5的小区排名"""
    if 需要更新状态():
        更新所有房源状态()

    所有房源 = 房源模型.query.all()
    小区计数器 = Counter(房源.community for 房源 in 所有房源 if 房源.community)

    排名数据 = [
        {'community': 小区, 'count': 数量}
        for 小区, 数量 in 小区计数器.most_common(5)
    ]

    return jsonify(构建响应(200, 排名数据))


@dashboard_bp.route('/dashboard/best_day', methods=['GET'])
@api_handler("获取最佳成交日", 需要回滚=False)
def 获取最佳成交日() -> Response:
    """获取单日最高成交额的日期和金额"""
    if 需要更新状态():
        更新所有房源状态()

    最佳记录 = db.session.query(
        合同模型.sign_date,
        func.coalesce(func.sum(合同模型.total_amount), 0).label('总金额')
    ).filter(
        合同模型.sign_date.isnot(None)
    ).group_by(合同模型.sign_date).order_by(
        func.coalesce(func.sum(合同模型.total_amount), 0).desc()
    ).first()

    if not 最佳记录:
        return jsonify(构建响应(200, {'date': None, 'amount': 0}))

    数据 = {
        'date': 最佳记录.sign_date,
        'amount': float(最佳记录.总金额)
    }

    return jsonify(构建响应(200, 数据))


@dashboard_bp.route('/dashboard/best_month_customers', methods=['GET'])
@api_handler("获取最佳新增客户月", 需要回滚=False)
def 获取最佳新增客户月() -> Response:
    """获取单月最高新增客户数的月份和数量"""
    if 需要更新状态():
        更新所有房源状态()

    所有客户 = 客户模型.query.filter(客户模型.add_date.isnot(None)).all()

    if not 所有客户:
        return jsonify(构建响应(200, {'month': None, 'count': 0}))

    月客户计数器 = {}
    for 客户 in 所有客户:
        if not 客户.add_date or len(客户.add_date) < 7:
            continue
        月份 = 客户.add_date[:7]
        月客户计数器[月份] = 月客户计数器.get(月份, 0) + 1

    最佳月份 = max(月客户计数器.items(), key=lambda x: x[1])

    数据 = {
        'month': 最佳月份[0],
        'count': 最佳月份[1]
    }

    return jsonify(构建响应(200, 数据))
