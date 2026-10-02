import os
import sys

# 兼容 PyInstaller --onefile 打包模式：把自身目录加入 sys.path
# 解决 from models import db / from utils.xxx import yyy 类相对导入找不到的问题
_pkg_root = os.path.dirname(os.path.abspath(__file__))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import secrets
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db
from routes.houses import houses_bp
from routes.customers import customers_bp
from routes.contracts import contracts_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp

# API访问令牌（启动时随机生成，防止外部未授权调用写接口）
_API令牌 = secrets.token_urlsafe(32)


def 获取API令牌() -> str:
    """获取当前API访问令牌（供前端读取后附加到请求头）"""
    return _API令牌


def 获取前端dist目录():
    """获取前端构建产物目录路径"""
    import sys as _sys
    if getattr(_sys, 'frozen', False):
        # 打包模式：PyInstaller 解压临时目录（--onefile 模式数据在这里）
        基础目录 = getattr(_sys, '_MEIPASS', os.path.dirname(_sys.executable))
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

    # 写操作令牌校验中间件（仅对POST/PUT/DELETE生效，GET和静态文件不受影响）
    @app.before_request
    def 校验写操作令牌():
        if request.method in ('POST', 'PUT', 'DELETE'):
            # 静态文件跳过、健康检查跳过
            if request.path.startswith('/api/'):
                客户端令牌 = request.headers.get('X-API-Token')
                if 客户端令牌 != _API令牌:
                    return jsonify({'code': 401, 'data': None, 'msg': '未授权访问'}), 401

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

    @app.route('/api/token', methods=['GET'])
    def 获取令牌接口():
        """前端启动时获取API访问令牌，后续写操作需携带此令牌"""
        return jsonify({'token': _API令牌})

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
    from models.setting import 设置模型, 获取默认设置
    for 键, 值 in 获取默认设置().items():
        if not 设置模型.query.filter_by(key=键).first():
            设置项 = 设置模型(key=键, value=值)
            db.session.add(设置项)
    
    db.session.commit()


if __name__ == '__main__':
    import sys, os

    # PyInstaller 打包后无窗口模式下标准输出不可用，需要重定向
    if getattr(sys, 'frozen', False):
        if hasattr(sys.stdout, 'buffer'):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        else:
            # --windowed 模式下 stdout 为 None，重定向到空设备
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')

    app = 创建应用()
    app.run(port=5000)
