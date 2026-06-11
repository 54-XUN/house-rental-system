from models import db


class 客户模型(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_code = db.Column(db.Text, unique=True, nullable=False)
    add_date = db.Column(db.Text)
    name = db.Column(db.Text)
    id_card = db.Column(db.Text)
    phone = db.Column(db.Text)
    wechat = db.Column(db.Text)
    tags = db.Column(db.Text)
    status = db.Column(db.Text, default='跟进中')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'add_date': self.add_date,
            'name': self.name,
            'id_card': self.id_card,
            'phone': self.phone,
            'wechat': self.wechat,
            'tags': self.tags,
            'status': self.status
        }
