from flask import Blueprint, request, jsonify, Response
from models import db
from models.house import 房源模型
from utils.id_generator import 生成房源编号
from utils.helpers import 构建响应, 构建错误响应, 更新所有房源状态
from utils.api_decorator import api_handler
from datetime import datetime, timedelta

houses_bp = Blueprint('houses', __name__)


@houses_bp.route('/houses', methods=['GET'])
@api_handler("获取房源列表", 需要回滚=False)
def 获取房源列表() -> Response:
    """获取房源列表，支持筛选和分页"""
    查询 = 房源模型.query

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    状态筛选 = request.args.get('status')
    if 状态筛选:
        查询 = 查询.filter(房源模型.status == 状态筛选)

    排除状态 = request.args.get('status_exclude')
    if 排除状态:
        查询 = 查询.filter(房源模型.status != 排除状态)

    面积最小值 = request.args.get('area_min')
    if 面积最小值:
        查询 = 查询.filter(房源模型.area >= float(面积最小值))

    面积最大值 = request.args.get('area_max')
    if 面积最大值:
        查询 = 查询.filter(房源模型.area <= float(面积最大值))

    标签筛选 = request.args.get('tags')
    if 标签筛选:
        标签列表 = 标签筛选.split(',')
        from sqlalchemy import and_, or_
        条件列表 = []
        for 标签 in 标签列表:
            # 转义LIKE通配符和特殊字符，防止逻辑污染
            标签 = 标签.strip().replace('%', '\\%').replace('_', '\\_').replace(',', '')
            if not 标签:
                continue
            # 单个标签用OR匹配多种位置，多个标签用AND组合（必须全部包含）
            条件列表.append(or_(
                房源模型.tags.like(f'{标签},%'),
                房源模型.tags.like(f'%,{标签},%'),
                房源模型.tags.like(f'%,{标签}'),
                房源模型.tags == 标签
            ))
        if 条件列表:
            查询 = 查询.filter(and_(*条件列表))

    室数筛选 = request.args.get('room')
    if 室数筛选:
        查询 = 查询.filter(房源模型.room == int(室数筛选))

    厅数筛选 = request.args.get('hall')
    if 厅数筛选:
        查询 = 查询.filter(房源模型.hall == int(厅数筛选))

    pagination = 查询.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(构建响应(200, {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }))


@houses_bp.route('/houses', methods=['POST'])
@api_handler("创建房源", 需要回滚=True)
def 创建房源() -> Response:
    """创建新房源"""
    数据 = request.get_json()

    if not 数据:
        return jsonify(构建响应(400, None, "请求数据为空"))

    if 数据.get('area') and (数据['area'] < 0 or 数据['area'] > 9999):
        return jsonify(构建响应(400, None, "面积必须在0-9999之间"))

    新房源 = 房源模型(
        house_code=生成房源编号(),
        add_date=数据.get('add_date'),
        community=数据.get('community'),
        address=数据.get('address'),
        floor=数据.get('floor'),
        room=数据.get('room'),
        hall=数据.get('hall'),
        area=数据.get('area'),
        rent=数据.get('rent'),
        tags=数据.get('tags'),
        status='空闲'
    )

    db.session.add(新房源)
    db.session.commit()

    return jsonify(构建响应(200, 新房源.to_dict(), "创建成功"))


@houses_bp.route('/houses/<int:house_id>', methods=['PUT'])
@api_handler("更新房源", 需要回滚=True)
def 更新房源(house_id: int) -> Response:
    """更新房源信息"""
    房源 = 房源模型.query.get_or_404(house_id)
    数据 = request.get_json()

    if not 数据:
        return jsonify(构建响应(400, None, "请求数据为空"))

    可更新字段 = ['add_date', 'community', 'address', 'floor', 'room', 'hall',
                   'area', 'rent', 'tags']

    for 字段 in 可更新字段:
        if 字段 in 数据:
            setattr(房源, 字段, 数据[字段])

    db.session.commit()
    return jsonify(构建响应(200, 房源.to_dict(), "更新成功"))


@houses_bp.route('/houses/<int:house_id>', methods=['DELETE'])
@api_handler("删除房源", 需要回滚=True)
def 删除房源(house_id: int) -> Response:
    """删除房源"""
    房源 = 房源模型.query.get_or_404(house_id)

    # 如果房源有关联合同，不允许删除
    if 房源.contract_code:
        return jsonify(构建响应(400, None, "该房源已签约，无法删除"))

    db.session.delete(房源)
    db.session.commit()
    return jsonify(构建响应(200, None, "删除成功"))


@houses_bp.route('/houses/by_code/<string:house_code>', methods=['GET'])
@api_handler("查询房源", 需要回滚=False)
def 根据编号获取房源(house_code: str) -> Response:
    """根据房源编号获取详情"""
    房源 = 房源模型.query.filter_by(house_code=house_code).first_or_404()
    return jsonify(构建响应(200, 房源.to_dict()))


@houses_bp.route('/houses/refresh-status', methods=['POST'])
@api_handler("刷新房源状态", 需要回滚=True)
def 刷新房源状态() -> Response:
    """委托helpers统一刷新所有房源状态"""
    更新所有房源状态()
    return jsonify(构建响应(200, None, "状态刷新完成"))
