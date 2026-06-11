from flask import Blueprint, request, jsonify, Response
from models import db
from models.setting import 设置模型
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型
from utils.helpers import 构建响应

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
def 获取设置() -> Response:
    """获取所有参数设置"""
    设置列表 = 设置模型.query.all()
    设置字典 = {设置项.key: 设置项.value for 设置项 in 设置列表}
    return jsonify(构建响应(200, 设置字典))


@settings_bp.route('/settings', methods=['PUT'])
def 更新设置() -> Response:
    """更新参数设置"""
    数据 = request.get_json()
    
    for 键, 值 in 数据.items():
        设置项 = 设置模型.query.filter_by(key=键).first()
        if 设置项:
            设置项.value = str(值)
        else:
            新设置 = 设置模型(key=键, value=str(值))
            db.session.add(新设置)
    
    db.session.commit()
    return jsonify(构建响应(200, None, "更新成功"))


@settings_bp.route('/settings/reset', methods=['POST'])
def 重置系统() -> Response:
    """
    模板初始化：
    清空三张表（房源、客户、合同）
    恢复 settings 默认值
    """
    try:
        # 清空三张表（先清合同表，避免外键问题）
        db.session.query(合同模型).delete()
        db.session.query(房源模型).delete()
        db.session.query(客户模型).delete()
        
        # 删除现有设置
        db.session.query(设置模型).delete()
        db.session.commit()
        
        # 恢复默认设置
        默认设置 = {
            'card_columns': '5',
            'vacant_style': 'WPS',
            'rented_style': 'WPS',
            'expiring_style': 'WPS',
            'expiring_days': '30',
            'communities': '["小区名称A","小区名称B","小区名称C","小区名称D","小区名称E","小区名称F","小区名称G","小区名称H","小区名称I"]',
            'house_tags': '["楼层低","有电梯","近地铁","有家具","有空调","有车位","精装修","民水民电","随时看房"]'
        }
        
        for 键, 值 in 默认设置.items():
            设置项 = 设置模型(key=键, value=值)
            db.session.add(设置项)
        
        db.session.commit()
        
        return jsonify(构建响应(200, None, "系统已重置"))
    
    except Exception as e:
        db.session.rollback()
        return jsonify(构建响应(500, None, f"重置失败：{str(e)}"))


@settings_bp.route('/import-example', methods=['POST'])
def 导入示例数据接口() -> Response:
    """导入示例数据接口"""
    from utils.excel_import import 导入示例数据
    成功, 消息 = 导入示例数据()
    
    if 成功:
        return jsonify(构建响应(200, None, 消息))
    else:
        return jsonify(构建响应(500, None, 消息))


@settings_bp.route('/delete-test-data', methods=['POST'])
def 删除测试数据接口() -> Response:
    """删除测试数据接口"""
    from utils.excel_import import 删除测试数据
    成功, 消息 = 删除测试数据()
    
    if 成功:
        return jsonify(构建响应(200, None, 消息))
    else:
        return jsonify(构建响应(500, None, 消息))
