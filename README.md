# 房屋出租管理系统

基于 Flask + Vue3 的单机房屋出租管理系统：管理房源、客户与合同，内置统计看板。打包为单个 EXE 后双击即用，无需安装 Python 或数据库。

## 功能特性

- **房源管理**：按小区分组的卡片视图 / 表格视图，高级筛选（状态、面积、标签、室厅），折叠展开浏览
- **客户管理**：跟进中 / 已签单 / 已放弃状态流转，标签画像
- **合同签约**：编号自动生成，月租金与合同金额自动计算，签约/退租自动联动房源与客户状态
- **统计看板**：成交金额趋势、新增客户趋势、房源状态分布、小区排名、最高成交日
- **参数设置**：卡片列数、状态配色、小区与标签字典、示例数据导入/清空

## 技术栈

| 层 | 技术 |
|---|---|
| 桌面壳 | PyWebView（EdgeChromium） |
| 后端 | Flask + SQLAlchemy |
| 前端 | Vue 3 + Element Plus + ECharts |
| 存储 | SQLite（单文件，随用户数据目录存放） |
| 打包 | PyInstaller |

## 快速开始

### 方式一：源码运行

需要 Python 3.12+（推荐用 [uv](https://docs.astral.sh/uv/) 管理环境）与 Node.js：

```powershell
# 后端依赖
uv sync

# 前端依赖与构建
cd frontend
npm install
npm run build
cd ..

# 启动（PyWebView 桌面窗口，也可浏览器访问 http://127.0.0.1:5000）
.venv\Scripts\python.exe 启动脚本.py
```

### 方式二：打包为 EXE

```powershell
.venv\Scripts\python.exe build\build.py
```

产物在 `build/dist/房屋出租管理系统.exe`，双击运行，拷到其他 Windows 电脑同样可用。

## 运行测试

```powershell
.venv\Scripts\python.exe -m pytest backend/tests
```

## 项目结构

```
backend/          Flask 后端（API + 数据模型，含 generate_data.py 测试数据生成）
frontend/         Vue3 前端源码
build/            打包脚本（build.py；build.spec 与图标不随仓库分发）
docs/             开发规范.md（需求规格）、开发文档.md（维护手册）
启动脚本.py        开发/打包通用入口
```

## 文档

- [docs/开发规范.md](docs/开发规范.md) — 产品需求规格（数据库设计、API 定义、业务规则）
- [docs/开发文档.md](docs/开发文档.md) — 维护手册（架构说明、环境要点、打包流程）

## License

[MIT](LICENSE)
