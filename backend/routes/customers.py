from flask import Blueprint, request, jsonify, Response
from models import db
from models.customer import 客户模型
from utils.id_generator import 生成客户编号
from utils.helpers import 构建响应, 构建错误响应

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/customers', methods=['GET'])
def 获取客户列表() -> Response:
    """获取客户列表，支持状态筛选和分页"""
    try:
        查询 = 客户模型.query

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)

        状态筛选 = request.args.get('status')
        if 状态筛选:
            查询 = 查询.filter(客户模型.status == 状态筛选)

        pagination = 查询.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify(构建响应(200, {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }))

    except Exception as e:
        return jsonify(构建错误响应(e, "获取客户列表"))


@customers_bp.route('/customers', methods=['POST'])
def 创建客户() -> Response:
    """创建新客户"""
    try:
        数据 = request.get_json()
        
        if not 数据:
            return jsonify(构建响应(400, None, "请求数据为空"))
        
        新客户 = 客户模型(
            customer_code=生成客户编号(),
            add_date=数据.get('add_date'),
            name=数据.get('name'),
            id_card=数据.get('id_card'),
            phone=数据.get('phone'),
            wechat=数据.get('wechat'),
            tags=数据.get('tags'),
            status='跟进中'
        )
        
        db.session.add(新客户)
        db.session.commit()
        
        return jsonify(构建响应(200, 新客户.to_dict(), "创建成功"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建错误响应(e, "创建客户"))


@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def 更新客户(customer_id: int) -> Response:
    """更新客户信息"""
    try:
        客户 = 客户模型.query.get_or_404(customer_id)
        数据 = request.get_json()
        
        if not 数据:
            return jsonify(构建响应(400, None, "请求数据为空"))
        
        可更新字段 = ['add_date', 'name', 'id_card', 'phone', 'wechat', 'tags', 'status']
        
        for 字段 in 可更新字段:
            if 字段 in 数据:
                setattr(客户, 字段, 数据[字段])
        
        db.session.commit()
        return jsonify(构建响应(200, 客户.to_dict(), "更新成功"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建错误响应(e, "更新客户"))


@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def 删除客户(customer_id: int) -> Response:
    """删除客户"""
    try:
        客户 = 客户模型.query.get_or_404(customer_id)
        
        # 检查是否有关联合同
        from models.contract import 合同模型
        关联合同 = 合同模型.query.filter_by(customer_code=客户.customer_code).first()
        if 关联合同:
            return jsonify(构建响应(400, None, "该客户已签约，无法删除"))
        
        db.session.delete(客户)
        db.session.commit()
        return jsonify(构建响应(200, None, "删除成功"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建错误响应(e, "删除客户"))


@customers_bp.route('/customers/by_code/<string:customer_code>', methods=['GET'])
def 根据编号获取客户(customer_code: str) -> Response:
    """根据客户编号获取详情"""
    try:
        客户 = 客户模型.query.filter_by(customer_code=customer_code).first_or_404()
        return jsonify(构建响应(200, 客户.to_dict()))
    
    except Exception as e:
        return jsonify(构建错误响应(e, "查询客户"))
