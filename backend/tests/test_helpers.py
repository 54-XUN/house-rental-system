"""
P0核心测试：计算房源状态() 边界值覆盖

覆盖场景：
- 空日期 → 空闲
- 过期日期(<=今天) → 已租
- 即将到期(今天+1 ~ 今天+30) → 即将到期
- 远期未来(>今天+30) → 已租
- 无效日期格式 → 空闲(容错)
"""
from datetime import datetime, timedelta
from utils.helpers import 计算房源状态


class Test计算房源状态:
    """房源状态计算逻辑测试"""

    def setup_method(self):
        """每个测试方法前的基准时间"""
        self.今天 = datetime.now()

    def test_空日期返回空闲(self):
        assert 计算房源状态(None) == '空闲'
        assert 计算房源状态('') == '空闲'

    def test_过期日期返回已租(self):
        昨天 = (self.今天 - timedelta(days=1)).strftime('%Y-%m-%d')
        今天str = self.今天.strftime('%Y-%m-%d')
        assert 计算房源状态(昨天) == '已租'
        assert 计算房源状态(今天str) == '已租'

    def test_即将到期返回即将到期(self):
        明天 = (self.今天 + timedelta(days=1)).strftime('%Y-%m-%d')
        第15天 = (self.今天 + timedelta(days=15)).strftime('%Y-%m-%d')
        第30天 = (self.今天 + timedelta(days=30)).strftime('%Y-%m-%d')

        assert 计算房源状态(明天) == '即将到期'
        assert 计算房源状态(第15天) == '即将到期'
        assert 计算房源状态(第30天) == '即将到期'

    def test_远期未来返回已租(self):
        第31天 = (self.今天 + timedelta(days=31)).strftime('%Y-%m-%d')
        第365天 = (self.今天 + timedelta(days=365)).strftime('%Y-%m-%d')

        assert 计算房源状态(第31天) == '已租'
        assert 计算房源状态(第365天) == '已租'

    def test_无效格式容错返回空闲(self):
        assert 计算房源状态('不是日期') == '空闲'
        assert 计算房源状态('2024/13/45') == '空闲'
        assert 计算房源状态('abc-def') == '空闲'


class Test构建响应:
    """标准响应格式测试"""

    def test_成功响应结构(self):
        from utils.helpers import 构建响应
        结果 = 构建响应(200, {'key': 'value'}, 'ok')
        assert 结果['code'] == 200
        assert 结果['data'] == {'key': 'value'}
        assert 结果['msg'] == 'ok'

    def test_错误响应不含堆栈(self):
        from utils.helpers import 构建错误响应
        try:
            raise ValueError("测试异常")
        except Exception as e:
            结果 = 构建错误响应(e, "测试操作")
        assert 结果['code'] == 500
        assert 结果['data'] is None
        assert 'ValueError' not in 结果['msg']
        assert '测试异常' not in 结果['msg']
