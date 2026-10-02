"""
P0核心测试：合同CRUD + 房源联动状态

覆盖场景：
- 创建合同自动更新房源为已租/即将到期
- 删除合同自动清空房源信息并恢复空闲
- 已签约房源无法重复签约
- 不存在的房源无法签合同
"""


class Test合同CRUD:
    """合同增删改查及联动测试"""

    def _创建测试房源(self, 客户端, house_code='FY00001', status='空闲'):
        """辅助：创建一个测试房源"""
        return 客户端.post('/api/houses', json={
            'house_code': house_code,
            'community': '测试小区',
            'address': '测试地址',
            'room': 2,
            'hall': 1,
            'area': 80.0,
            'rent': 3000,
            'status': status
        })

    def _创建测试客户(self, 客户端, customer_code='F00001'):
        """辅助：创建一个测试客户"""
        return 客户端.post('/api/customers', json={
            'name': '测试客户',
            'phone': '13800138000',
            'customer_code': customer_code
        })

    def test_创建合同自动更新房源状态(self, 客户端):
        """签约后房源状态应变为'已租'或'即将到期'"""
        self._创建测试房源(客户端)
        self._创建测试客户(客户端)

        明年 = __import__('datetime').date.today().year + 1
        响应 = 客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 12,
            'start_date': '2025-01-01',
            'end_date': f'{明年}-12-31',
            'monthly_rent': 3000,
            'deposit': 3000
        })

        assert 响应.status_code == 200
        数据 = 响应.get_json()
        assert 数据['code'] == 200
        assert 数据['data']['contract_code'].startswith('FYH')

        # 验证房源状态已更新
        房源响应 = 客户端.get('/api/houses/by_code/FY00001')
        房源数据 = 房源响应.get_json()['data']
        assert 房源数据['status'] in ('已租', '即将到期')
        assert 房源数据['contract_code'] is not None
        assert 房源数据['expire_date'] == f'{明年}-12-31'

    def test_删除合同恢复房源空闲(self, 客户端):
        """解约后房源应恢复为空闲"""
        self._创建测试房源(客户端)
        self._创建测试客户(客户端)

        # 先创建合同
        客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 12,
            'start_date': '2025-01-01',
            'end_date': '2026-01-01',
            'monthly_rent': 3000,
            'deposit': 3000
        })

        # 获取合同ID
        合同列表 = 客户端.get('/api/contracts').get_json()['data']
        合同ID = 合同列表['items'][0]['id']

        # 删除合同
        响应 = 客户端.delete(f'/api/contracts/{合同ID}')
        assert 响应.status_code == 200

        # 验证房源已恢复空闲
        房源响应 = 客户端.get('/api/houses/by_code/FY00001')
        房源数据 = 房源响应.get_json()['data']
        assert 房源数据['status'] == '空闲'
        assert 房源数据['contract_code'] is None
        assert 房源数据['expire_date'] is None

    def test_已签约房源不可重复签约(self, 客户端):
        """已租/即将到期的房源不能再次签约"""
        self._创建测试房源(客户端)
        self._创建测试客户(客户端)

        # 第一次签约
        客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 6,
            'start_date': '2025-06-01',
            'end_date': '2025-12-01',
            'monthly_rent': 3000,
            'deposit': 3000
        })

        # 第二次签约应被拒绝
        响应 = 客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 6,
            'start_date': '2025-06-01',
            'end_date': '2025-12-01',
            'monthly_rent': 3000,
            'deposit': 3000
        })
        assert 响应.status_code == 200
        数据 = 响应.get_json()
        assert 数据['code'] == 400
        assert '已' in 数据['msg']

    def test_不存在的房源无法签约(self, 客户端):
        self._创建测试客户(客户端)

        响应 = 客户端.post('/api/contracts', json={
            'house_code': 'FY99999',
            'customer_code': 'F00001',
            'months': 12,
            'start_date': '2025-01-01',
            'end_date': '2026-01-01',
            'monthly_rent': 3000,
            'deposit': 3000
        })
        assert 响应.status_code == 200
        数据 = 响应.get_json()
        assert 数据['code'] == 404

    def test_合同金额自动计算正确(self, 客户端):
        """total_amount = months * monthly_rent + deposit"""
        self._创建测试房源(客户端)
        self._创建测试客户(客户端)

        响应 = 客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 12,
            'start_date': '2025-01-01',
            'end_date': '2026-01-01',
            'monthly_rent': 2500,
            'deposit': 2500
        })
        数据 = 响应.get_json()['data']
        assert 数据['total_amount'] == 12 * 2500 + 2500  # 32500


class Test房源CRUD:
    """基础房源CRUD测试"""

    def test_创建房源(self, 客户端):
        响应 = 客户端.post('/api/houses', json={
            'community': '翠苑小区',
            'address': '1栋1单元101',
            'floor': 3,
            'room': 2,
            'hall': 1,
            'area': 85.5,
            'rent': 3500,
            'tags': '有电梯,近地铁'
        })
        assert 响应.status_code == 200
        数据 = 响应.get_json()
        assert 数据['code'] == 200
        assert 数据['data']['community'] == '翠苑小区'
        assert 数据['data']['status'] == '空闲'
        assert 数据['data']['house_code'].startswith('FY')

    def test_已签约房源不可删除(self, 客户端):
        """有关联合同的房源删除应被拒绝"""
        # 创建房源
        客户端.post('/api/houses', json={
            'community': '测试小区',
            'address': '测试地址',
            'room': 2, 'hall': 1, 'area': 80.0, 'rent': 3000
        })
        # 创建客户
        客户端.post('/api/customers', json={
            'name': '测试人', 'phone': '13800138001'
        })
        # 签约
        客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 6,
            'start_date': '2025-01-01',
            'end_date': '2025-07-01',
            'monthly_rent': 3000,
            'deposit': 3000
        })

        # 尝试删除
        响应 = 客户端.delete('/api/houses/1')
        数据 = 响应.get_json()
        assert 数据['code'] == 400
        assert '已签约' in 数据['msg']


class Test客户CRUD:
    """基础客户CRUD + 字段校验测试"""

    def test_创建客户(self, 客户端):
        响应 = 客户端.post('/api/customers', json={
            'name': '张三',
            'phone': '13800138002',
            'id_card': '110101199001011234',
            'wechat': 'zhangsan'
        })
        assert 响应.status_code == 200
        数据 = 响应.get_json()
        assert 数据['code'] == 200
        assert 数据['data']['name'] == '张三'
        assert 数据['data']['status'] == '跟进中'

    def test_手机号格式不合法被拒绝(self, 客户端):
        响应 = 客户端.post('/api/customers', json={
            'name': '测试',
            'phone': '12345',  # 不合法
        })
        数据 = 响应.get_json()
        assert 数据['code'] == 400
        assert '手机号' in 数据['msg']

    def test_身份证号格式不合法被拒绝(self, 客户端):
        响应 = 客户端.post('/api/customers', json={
            'name': '测试',
            'phone': '13800138003',
            'id_card': '123'  # 不合法
        })
        数据 = 响应.get_json()
        assert 数据['code'] == 400
        assert '身份证' in 数据['msg']

    def test_已签约客户不可删除(self, 客户端):
        """有关联合同的客户删除应被拒绝"""
        # 创建房源和客户
        客户端.post('/api/houses', json={
            'community': '测试', 'address': '测试',
            'room': 1, 'hall': 0, 'area': 50.0, 'rent': 2000
        })
        客户端.post('/api/customers', json={
            'name': '签约客户', 'phone': '13800138004'
        })
        # 签约
        客户端.post('/api/contracts', json={
            'house_code': 'FY00001',
            'customer_code': 'F00001',
            'months': 3,
            'start_date': '2025-01-01',
            'end_date': '2025-04-01',
            'monthly_rent': 2000,
            'deposit': 1000
        })

        响应 = 客户端.delete('/api/customers/1')
        数据 = 响应.get_json()
        assert 数据['code'] == 400
        assert '已签约' in 数据['msg']
