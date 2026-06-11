from models import db


def 获取默认设置() -> dict:
    """获取系统默认设置字典（统一来源，避免多处重复定义）"""
    return {
        'card_columns': '5',
        'vacant_style': 'WPS',
        'rented_style': 'WPS',
        'expiring_style': 'WPS',
        'expiring_days': '30',
        'admin_password': '',
        'communities': '["小区名称A","小区名称B","小区名称C","小区名称D","小区名称E","小区名称F","小区名称G","小区名称H","小区名称I"]',
        'house_tags': '["楼层低","有电梯","近地铁","有家具","有空调","有车位","精装修","民水民电","随时看房"]'
    }


class 设置模型(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.Text, unique=True, nullable=False)
    value = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }
