from flask import Blueprint, request, jsonify, Response
import re
from models import db
from models.contract import 合同模型
from models.house import 房源模型
from utils.id_generator import 生成合同编号
from utils.helpers import 构建响应, 构建错误响应, 计算房源状态

contracts_bp = Blueprint('contracts', __name__)


@contracts_bp.route('/contracts', methods=['GET'])
def 获取合同列表() -> Response:
    """获取合同列表，支持分页"""
    try:
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

    except Exception as e:
        return jsonify(构建错误响应(e, "获取合同列表"))


@contracts_bp.route('/contracts', methods=['POST'])
def 创建合同() -> Response:
    """
    创建新合同
    业务逻辑：
    - 自动计算 total_amount = months * monthly_rent + deposit
    - 自动更新房源表的 contract_code、expire_date、status 为"已租"
    """
    try:
        数据 = request.get_json()

        if not 数据:
            return jsonify(构建响应(400, None, "请求数据为空"))

        # 显式事务控制
        事务嵌套 = db.session.begin_nested()

        # 验证房源编号格式
        if not re.match(r'^FY\d{5}$', 数据['house_code']):
            return jsonify(构建响应(400, None, "房源编号格式错误"))

        # 验证必填字段
        必填字段列表 = ['house_code', 'customer_code', 'months', 
                         'start_date', 'end_date', 'monthly_rent']
        缺失字段 = [字段 for 字段 in 必填字段列表 if 字段 not in 数据 or not 数据[字段]]
        
        if 缺失字段:
            return jsonify(构建响应(400, None, f"缺少必填字段：{', '.join(缺失字段)}"))
        
        # 检查房源是否存在
        关联房源 = 房源模型.query.filter_by(house_code=数据['house_code']).first()
        if not 关联房源:
            return jsonify(构建响应(404, None, "房源不存在"))
        
        # 检查房源是否已出租（包括已租和即将到期）
        if 关联房源.status in ['已租', '即将到期']:
            return jsonify(构建响应(400, None, f"该房源已{关联房源.status}，无法重复签约"))
        
        # 计算合同金额
        月数 = int(数据['months'])
        月租 = float(数据['monthly_rent'])
        押金原始值 = 数据.get('deposit')
        押金 = float(押金原始值) if 押金原始值 is not None else 0
        总金额 = 月数 * 月租 + 押金
        
        新合同 = 合同模型(
            contract_code=生成合同编号(),
            sign_date=数据.get('sign_date'),
            house_code=数据['house_code'],
            customer_code=数据['customer_code'],
            months=月数,
            start_date=数据['start_date'],
            end_date=数据['end_date'],
            deposit=押金 if 押金 > 0 else None,
            monthly_rent=月租,
            total_amount=总金额
        )
        
        db.session.add(新合同)
        
        # 更新房源状态和关联信息
        关联房源.contract_code = 新合同.contract_code
        关联房源.expire_date = 数据['end_date']
        关联房源.status = 计算房源状态(数据['end_date'])
        
        db.session.commit()
        
        return jsonify(构建响应(200, 新合同.to_dict(), "创建成功"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建错误响应(e, "创建合同"))


@contracts_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
def 删除合同(contract_id: int) -> Response:
    """
    删除合同
    业务逻辑：自动清空关联房源的合同信息，状态改回"空闲"
    """
    try:
        合同 = 合同模型.query.get_or_404(contract_id)
        
        # 清空关联房源的合同信息
        if 合同.house_code:
            关联房源 = 房源模型.query.filter_by(house_code=合同.house_code).first()
            if 关联房源:
                关联房源.contract_code = None
                关联房源.expire_date = None
                关联房源.status = '空闲'
        
        db.session.delete(合同)
        db.session.commit()
        
        return jsonify(构建响应(200, None, "删除成功"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建错误响应(e, "删除合同"))
