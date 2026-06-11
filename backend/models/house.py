from models import db
from datetime import datetime


class 房源模型(db.Model):
    __tablename__ = 'houses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_code = db.Column(db.Text, unique=True, nullable=False)
    add_date = db.Column(db.Text)
    community = db.Column(db.Text)
    address = db.Column(db.Text)
    floor = db.Column(db.Integer)
    room = db.Column(db.Integer)
    hall = db.Column(db.Integer)
    area = db.Column(db.Float)
    rent = db.Column(db.Float)
    tags = db.Column(db.Text)
    contract_code = db.Column(db.Text)
    expire_date = db.Column(db.Text)
    status = db.Column(db.Text, default='空闲')
    
    def to_dict(self):
        return {
            'id': self.id,
            'house_code': self.house_code,
            'add_date': self.add_date,
            'community': self.community,
            'address': self.address,
            'floor': self.floor,
            'room': self.room,
            'hall': self.hall,
            'area': self.area,
            'rent': self.rent,
            'tags': self.tags,
            'contract_code': self.contract_code,
            'expire_date': self.expire_date,
            'status': self.status
        }
