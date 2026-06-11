import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app import 创建应用
from models import db
from models.house import 房源模型
from models.customer import 客户模型
from models.contract import 合同模型
from datetime import datetime, timedelta

app = 创建应用()
with app.app_context():
    db.create_all()

    小区列表 = ['翠苑小区', '幸福花园', '阳光家园', '锦绣华庭', '绿城公寓', '万科城', '恒大名都', '碧桂园', '保利花园', '龙湖小区']
    标签池 = ['精装修', '有电梯', '有家具', '近地铁', '有空调', '有车位', '民水民电', '随时看房', '楼层低', '拎包入住']
    姓氏 = ['张', '李', '王', '赵', '刘', '陈', '杨', '黄', '周', '吴']
    名字 = ['伟', '芳', '娜', '敏', '静', '强', '磊', '洋', '艳', '杰']

    # 100条房源
    for i in range(1, 101):
        小区 = random.choice(小区列表)
        楼栋 = f'{random.randint(1,20)}栋'
        单元 = f'{random.randint(1,6)}单元'
        房号 = f'{random.randint(1,30):02d}室'
        地址 = f'{小区}{楼栋}{单元}{房号}'
        面积 = round(random.uniform(35, 180), 1)
        租金 = int(面积 * random.randint(25, 60))
        室 = random.randint(1, 5)
        厅 = random.randint(0, 2)
        楼层 = random.randint(1, 33)
        状态随机 = random.random()
        if 状态随机 < 0.55:
            状态 = '空闲'
        elif 状态随机 < 0.85:
            状态 = '已租'
        else:
            状态 = '即将到期'
        随机标签 = random.sample(标签池, random.randint(2, 5))
        房源 = 房源模型(
            house_code=f'FY{i:05d}',
            community=小区,
            address=地址,
            floor=楼层,
            room=室,
            hall=厅,
            area=面积,
            rent=租金,
            tags=','.join(随机标签),
            status=状态
        )
        db.session.add(房源)
    db.session.commit()
    print(f'房源: {房源模型.query.count()} 条')

    # 30个客户
    for i in range(1, 31):
        姓名 = f'{random.choice(姓氏)}{random.choice(名字)}{random.choice(名字)}'
        身份证 = str(random.randint(110101199001010000, 110101200512319999))
        电话前缀 = random.choice([3, 5, 7, 8, 9])
        电话后缀 = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        电话 = f'1{电话前缀}{电话后缀}'
        客户状态 = random.choice(['跟进中', '已签单', '已放弃'])
        客户标签 = random.choice(['刚需客户', '投资客户', '改善客户', '短期租赁'])
        客户 = 客户模型(
            customer_code=f'KH{i:05d}',
            name=姓名,
            id_card=身份证,
            phone=电话,
            wechat=姓名.lower(),
            tags=客户标签,
            status=客户状态
        )
        db.session.add(客户)
    db.session.commit()
    print(f'客户: {客户模型.query.count()} 条')

    # 35条合同（只给已租和即将到期的房源）
    已租房源列表 = 房源模型.query.filter(房源模型.status.in_(['已租', '即将到期'])).all()
    所有客户 = 客户模型.query.all()
    for i in range(min(35, len(已租房源列表))):
        房源 = 已租房源列表[i]
        客户 = random.choice(所有客户)
        月数 = random.choice([6, 12, 24])
        开始日期 = datetime.now() - timedelta(days=random.randint(30, 365))
        结束日期 = 开始日期 + timedelta(days=月数 * 30)
        押金 = int(房源.rent * random.choice([1, 2]))
        总金额 = 房源.rent * 月数 + 押金
        合同编号 = f'HT{i+1:05d}'
        合同 = 合同模型(
            contract_code=合同编号,
            house_code=房源.house_code,
            customer_code=客户.customer_code,
            months=月数,
            start_date=开始日期.strftime('%Y-%m-%d'),
            end_date=结束日期.strftime('%Y-%m-%d'),
            deposit=押金,
            monthly_rent=房源.rent,
            total_amount=总金额
        )
        db.session.add(合同)
        房源.contract_code = 合同编号
        房源.expire_date = 结束日期.strftime('%Y-%m-%d')
    db.session.commit()
    print(f'合同: {合同模型.query.count()} 条')
    print('测试数据生成完成！')
