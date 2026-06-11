from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db
from routes.houses import houses_bp
from routes.customers import customers_bp
from routes.contracts import contracts_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp


def 获取前端dist目录():
    """获取前端构建产物目录路径"""
    import os
    if getattr(__import__('sys'), 'frozen', False):
        # 打包模式：exe所在目录/frontend/dist
        基础目录 = os.path.dirname(__import__('sys').executable)
    else:
        # 开发模式：项目根目录/frontend/dist
        基础目录 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(基础目录, 'frontend', 'dist')


def 创建应用():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    CORS(app)

    db.init_app(app)

    with app.app_context(): 
        db.create_all()
        初始化默认设置()

    app.register_blueprint(houses_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(contracts_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')

    @app.route('/api/health', methods=['GET'])
    def 健康检查():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    # 添加前端静态文件托管路由（用于打包后的单文件部署）
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        dist_dir = 获取前端dist目录()
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        return send_from_directory(dist_dir, 'index.html')

    return app


def 初始化默认设置():
    from models.setting import 设置模型
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
        if not 设置模型.query.filter_by(key=键).first():
            设置项 = 设置模型(key=键, value=值)
            db.session.add(设置项)
    
    db.session.commit()


if __name__ == '__main__':
    app = 创建应用()
    app.run(debug=True, port=5000)
