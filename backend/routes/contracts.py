from flask import Blueprint, request, jsonify, Response
import re
from datetime import datetime
from models import db
from models.contract import 合同模型
from models.house import 房源模型
from models.customer import 客户模型
from utils.id_generator import 生成合同编号
from utils.helpers import 构建响应, 计算房源状态
from utils.api_decorator import api_handler

contracts_bp = Blueprint('contracts', __name__)


def 校验日期先后(开始日期值, 结束日期值) -> str | None:
    """校验开始/结束日期格式与先后顺序，返回错误消息，合法返回 None"""
    try:
        开始日 = datetime.strptime(str(开始日期值), '%Y-%m-%d')
        结束日 = datetime.strptime(str(结束日期值), '%Y-%m-%d')
    except (ValueError, TypeError):
        return "日期格式必须为 YYYY-MM-DD"
    if 结束日 <= 开始日:
        return "结束日期必须晚于开始日期"
    return None


@contracts_bp.route('/contracts', methods=['GET'])
@api_handler("获取合同列表", 需要回滚=False)
def 获取合同列表() -> Response:
    """获取合同列表，支持分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    分页对象 = 合同模型.query.order_by(合同模型.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify(构建响应(200, {
        'items': [合同.to_dict() for 合同 in 分页对象.items],
        'total': 分页对象.total,
        'pages': 分页对象.pages,
        'current_page': 分页对象.page
    }))


@contracts_bp.route('/contracts', methods=['POST'])
@api_handler("创建合同", 需要回滚=True)
def 创建合同() -> Response:
    """
    创建新合同
    业务逻辑：
    - 自动计算 total_amount = months * monthly_rent + deposit
    - 自动更新房源表的 contract_code、expire_date、status 为"已租"
    """
    数据 = request.get_json()

    if not 数据:
        return jsonify(构建响应(400, None, "请求数据为空"))

    # 安全获取房源编号（避免KeyError）
    房源编号 = 数据.get('house_code')
    if not 房源编号:
        return jsonify(构建响应(400, None, "房源编号不能为空"))

    # 验证房源编号格式
    if not re.match(r'^FY\d{5}$', 房源编号):
        return jsonify(构建响应(400, None, "房源编号格式错误"))

    # 验证必填字段
    必填字段列表 = ['customer_code', 'months',
                     'start_date', 'end_date', 'monthly_rent']
    缺失字段 = [字段 for 字段 in 必填字段列表 if 字段 not in 数据 or not 数据[字段]]

    if 缺失字段:
        return jsonify(构建响应(400, None, f"缺少必填字段：{', '.join(缺失字段)}"))

    # 检查房源是否存在
    关联房源 = 房源模型.query.filter_by(house_code=房源编号).first()
    if not 关联房源:
        return jsonify(构建响应(404, None, "房源不存在"))

    # 检查客户是否存在（防止合同挂在不存在的客户编号上）
    关联客户 = 客户模型.query.filter_by(customer_code=数据['customer_code']).first()
    if not 关联客户:
        return jsonify(构建响应(404, None, "客户不存在"))

    # 检查房源是否已出租（包括已租和即将到期）
    if 关联房源.status in ['已租', '即将到期']:
        return jsonify(构建响应(400, None, f"该房源已{关联房源.status}，无法重复签约"))

    # 数值字段校验（前端传字符串，统一转换）
    try:
        月数 = int(数据['months'])
        月租 = float(数据['monthly_rent'])
        押金原始值 = 数据.get('deposit')
        押金 = float(押金原始值) if 押金原始值 is not None else 0
    except (ValueError, TypeError):
        return jsonify(构建响应(400, None, "月数/月租/押金必须为有效数值"))

    if 月数 <= 0:
        return jsonify(构建响应(400, None, "租期月数必须大于0"))
    if 月租 <= 0:
        return jsonify(构建响应(400, None, "月租金必须大于0"))
    if 押金 < 0:
        return jsonify(构建响应(400, None, "押金不能为负数"))

    # 日期格式与先后顺序校验
    日期错误 = 校验日期先后(数据['start_date'], 数据['end_date'])
    if 日期错误:
        return jsonify(构建响应(400, None, 日期错误))

    总金额 = 月数 * 月租 + 押金

    新合同 = 合同模型(
        contract_code=生成合同编号(),
        sign_date=数据.get('sign_date'),
        house_code=房源编号,
        customer_code=数据['customer_code'],
        months=月数,
        start_date=数据['start_date'],
        end_date=数据['end_date'],
        deposit=押金 if 押金 > 0 else None,
        monthly_rent=月租,
        total_amount=总金额
    )

    db.session.add(新合同)

    # 更新房源状态和关联信息（新签约统一设为"已租"，"即将到期"由定时刷新计算）
    关联房源.contract_code = 新合同.contract_code
    关联房源.expire_date = 数据['end_date']
    关联房源.status = '已租'

    # 同步客户状态（与主数据一次提交，避免中间崩溃造成不一致）
    if 关联客户:
        关联客户.status = '已签单'

    db.session.commit()

    return jsonify(构建响应(200, 新合同.to_dict(), "创建成功"))


@contracts_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@api_handler("更新合同", 需要回滚=True)
def 更新合同(contract_id: int) -> Response:
    """更新合同信息"""
    合同 = 合同模型.query.get_or_404(contract_id)
    数据 = request.get_json()

    if not 数据:
        return jsonify(构建响应(400, None, "请求数据为空"))

    # 数值字段合法性校验
    for 数值字段, 下限 in (('months', 1), ('monthly_rent', 0.01), ('deposit', 0)):
        if 数值字段 in 数据 and 数据[数值字段] is not None:
            try:
                if float(数据[数值字段]) < 下限:
                    return jsonify(构建响应(400, None, f"{'租期月数' if 数值字段 == 'months' else ('月租金' if 数值字段 == 'monthly_rent' else '押金')}不能小于{下限}"))
            except (ValueError, TypeError):
                return jsonify(构建响应(400, None, f"{数值字段}必须为数值"))

    # 日期格式与先后顺序校验（未传的字段用现有值补齐）
    开始日期值 = 数据.get('start_date') or 合同.start_date
    结束日期值 = 数据.get('end_date') or 合同.end_date
    if 开始日期值 and 结束日期值:
        日期错误 = 校验日期先后(开始日期值, 结束日期值)
        if 日期错误:
            return jsonify(构建响应(400, None, 日期错误))

    # 客户变更校验：新客户必须存在
    新客户编号 = 数据.get('customer_code')
    原客户编号 = 合同.customer_code
    if 新客户编号 and 新客户编号 != 原客户编号:
        if not 客户模型.query.filter_by(customer_code=新客户编号).first():
            return jsonify(构建响应(404, None, "新客户不存在"))

    可更新字段 = ['sign_date', 'months', 'start_date', 'end_date',
                   'deposit', 'monthly_rent', 'customer_code']

    for 字段 in 可更新字段:
        if 字段 in 数据:
            setattr(合同, 字段, 数据[字段])

    # 重新计算总金额
    if 'months' in 数据 or 'monthly_rent' in 数据 or 'deposit' in 数据:
        月数 = 合同.months or 0
        月租 = 合同.monthly_rent or 0
        押金 = 合同.deposit or 0
        合同.total_amount = 月数 * 月租 + 押金

    # 同步新旧客户的签单状态
    if 新客户编号 and 新客户编号 != 原客户编号:
        新客户 = 客户模型.query.filter_by(customer_code=新客户编号).first()
        if 新客户:
            新客户.status = '已签单'
        if 原客户编号:
            原客户 = 客户模型.query.filter_by(customer_code=原客户编号).first()
            剩余合同数 = 合同模型.query.filter(
                合同模型.customer_code == 原客户编号,
                合同模型.id != 合同.id
            ).count()
            if 原客户 and 剩余合同数 == 0:
                原客户.status = '跟进中'

    # 如果结束日期变更，同步更新房源到期日和状态
    if 'end_date' in 数据 and 合同.house_code:
        关联房源 = 房源模型.query.filter_by(house_code=合同.house_code).first()
        if 关联房源:
            关联房源.expire_date = 数据['end_date']
            关联房源.status = 计算房源状态(数据['end_date'])

    db.session.commit()
    return jsonify(构建响应(200, 合同.to_dict(), "更新成功"))


@contracts_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
@api_handler("删除合同", 需要回滚=True)
def 删除合同(contract_id: int) -> Response:
    """
    删除合同
    业务逻辑：自动清空关联房源的合同信息，状态改回"空闲"
    """
    合同 = 合同模型.query.get_or_404(contract_id)

    # 清空关联房源的合同信息
    if 合同.house_code:
        关联房源 = 房源模型.query.filter_by(house_code=合同.house_code).first()
        if 关联房源:
            关联房源.contract_code = None
            关联房源.expire_date = None
            关联房源.status = '空闲'

    # 记录客户编号，用于删除后更新客户状态
    客户编号 = 合同.customer_code

    db.session.delete(合同)
    db.session.commit()

    # 检查该客户是否还有其他合同，没有则回退状态为"跟进中"
    if 客户编号:
        剩余合同数 = 合同模型.query.filter(
            合同模型.customer_code == 客户编号,
            合同模型.id != contract_id
        ).count()
        关联客户 = 客户模型.query.filter_by(customer_code=客户编号).first()
        if 关联客户:
            if 剩余合同数 == 0:
                关联客户.status = '跟进中'
            else:
                关联客户.status = '已签单'
            db.session.commit()

    return jsonify(构建响应(200, None, "删除成功"))
