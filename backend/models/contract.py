from models import db


class 合同模型(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_code = db.Column(db.Text, unique=True, nullable=False)
    sign_date = db.Column(db.Text)
    house_code = db.Column(db.Text)
    customer_code = db.Column(db.Text)
    months = db.Column(db.Integer)
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)
    deposit = db.Column(db.Float)
    monthly_rent = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_code': self.contract_code,
            'sign_date': self.sign_date,
            'house_code': self.house_code,
            'customer_code': self.customer_code,
            'months': self.months,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'deposit': self.deposit,
            'monthly_rent': self.monthly_rent,
            'total_amount': self.total_amount
        }
