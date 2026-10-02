from flask import Blueprint, request, jsonify, Response
from models import db
from models.setting import 设置模型, 获取默认设置
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型
from utils.helpers import 构建响应
from utils.api_decorator import api_handler

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings', methods=['GET'])
@api_handler("获取设置", 需要回滚=False)
def 获取设置() -> Response:
    """获取所有参数设置"""
    设置列表 = 设置模型.query.all()
    设置字典 = {设置项.key: 设置项.value for 设置项 in 设置列表}
    return jsonify(构建响应(200, 设置字典))


@settings_bp.route('/settings', methods=['PUT'])
@api_handler("更新设置", 需要回滚=True)
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
@api_handler("重置系统", 需要回滚=True)
def 重置系统() -> Response:
    """
    系统重置（需二次确认密码）：
    清空三张表（房源、客户、合同）
    恢复 settings 默认值

    请求体: { "confirm_password": "管理密码" }
    - 若 admin_password 为空（首次使用）→ 直接允许
    - 若已设置密码 → 必须匹配才允许重置
    """
    数据 = request.get_json()

    # 校验管理密码
    密码设置项 = 设置模型.query.filter_by(key='admin_password').first()
    当前密码 = 密码设置项.value if 密码设置项 and 密码设置项.value else ''

    if 当前密码:
        用户输入密码 = (数据 or {}).get('confirm_password', '')
        if 用户输入密码 != 当前密码:
            return jsonify(构建响应(403, None, "管理密码不正确，无法重置"))

    # 清空三张表（先清合同表，避免外键问题）
    db.session.query(合同模型).delete()
    db.session.query(房源模型).delete()
    db.session.query(客户模型).delete()

    # 删除现有设置
    db.session.query(设置模型).delete()
    db.session.commit()

    # 恢复默认设置（使用模型层统一定义，保留用户设置的管理密码）
    for 键, 值 in 获取默认设置().items():
        设置项 = 设置模型(key=键, value=值)
        db.session.add(设置项)

    # 如果之前设置了管理密码，恢复它
    if 当前密码:
        密码恢复项 = 设置模型.query.filter_by(key='admin_password').first()
        if 密码恢复项:
            密码恢复项.value = 当前密码

    db.session.commit()

    return jsonify(构建响应(200, None, "系统已重置"))
