from models import db


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
