# TennisCourt Scraper 🎾

一个专业的北京网球场地信息抓取系统，集成多平台数据源，提供完整的场馆信息查询服务。

## 🌟 项目特色

- **多平台数据融合**: 集成高德地图、小红书、大众点评等多个数据源
- **智能爬虫系统**: 采用智能模板匹配，快速获取场馆详情
- **现代化Web界面**: 基于Bootstrap的响应式设计，支持移动端
- **实时数据更新**: 支持后台任务和手动更新，确保数据时效性
- **完整API服务**: RESTful API设计，支持第三方集成

## 🚀 功能特性

### 数据抓取
- 高德地图API场馆基础信息抓取
- 小红书智能爬虫（模板匹配 + 模拟数据）
- 多平台数据融合与去重
- 自动缓存管理与更新策略

### 前端功能
- 场馆列表展示与搜索
- 按区域、价格、评分筛选
- 场馆详情页面（价格、评论、设施等）
- 响应式设计，支持移动端

### 后端API
- 场馆信息查询API
- 详情数据获取与更新API
- 爬虫任务管理API
- 健康检查与统计API

## 📋 技术栈

### 后端
- **FastAPI**: 现代化Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **Uvicorn**: ASGI服务器

### 前端
- **Bootstrap 5**: 响应式UI框架
- **JavaScript**: 动态交互
- **HTML5/CSS3**: 现代化Web标准

### 爬虫
- **Requests**: HTTP请求库
- **BeautifulSoup**: HTML解析
- **Selenium**: 浏览器自动化（备用）
- **智能模板系统**: 快速数据提取

## 🛠️ 安装部署

### 环境要求
- Python 3.8+
- pip包管理器

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/yourusername/tennis-court-scraper.git
cd tennis-court-scraper
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp env.example .env
# 编辑.env文件，配置必要的API密钥
```

4. **初始化数据库**
```bash
python -c "from app.database import init_db; init_db()"
```

5. **启动服务**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **访问应用**
- 前端页面: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📊 数据源

### 高德地图API
- 场馆基础信息（名称、地址、坐标）
- 区域划分与统计
- 实时数据更新

### 小红书智能爬虫
- 场馆详情信息（评分、评论、价格）
- 设施信息与营业时间
- 图片资源链接

### 数据融合
- 多平台数据去重与合并
- 智能评分计算
- 价格信息标准化

## 🔧 API接口

### 场馆相关
- `GET /api/courts` - 获取场馆列表
- `GET /api/courts/{court_id}` - 获取场馆详情
- `GET /api/courts/areas` - 获取区域列表
- `GET /api/courts/stats` - 获取统计信息

### 详情相关
- `GET /api/details/{court_id}` - 获取完整详情
- `GET /api/details/{court_id}/preview` - 预览详情
- `POST /api/details/{court_id}/update` - 更新详情
- `GET /api/details/batch/update` - 批量更新

### 爬虫相关
- `POST /api/scraper/scrape/{source}` - 启动爬虫任务
- `GET /api/scraper/status` - 获取爬虫状态

## 🧪 测试

运行自动化测试：
```bash
# 主应用测试
python test_app.py

# 详情API测试
python test_detail_api.py

# 智能爬虫测试
python test_xiaohongshu_smart.py

# 完整流程测试
python test_full_scraper.py
```

## 📁 项目结构

```
tennis_court_scraper/
├── app/                    # 主应用目录
│   ├── api/               # API路由
│   ├── scrapers/          # 爬虫模块
│   ├── static/            # 静态文件
│   ├── templates/         # 模板文件
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库配置
│   ├── main.py           # 应用入口
│   └── models.py         # 数据模型
├── data/                  # 数据目录
├── tests/                 # 测试文件
├── requirements.txt       # 依赖列表
├── README.md             # 项目文档
└── run.py                # 启动脚本
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢高德地图提供的API服务
- 感谢开源社区的技术支持
- 感谢所有贡献者的付出

## 📞 联系方式

- 项目主页: https://github.com/yourusername/tennis-court-scraper
- 问题反馈: https://github.com/yourusername/tennis-court-scraper/issues
- 邮箱: your.email@example.com

## 📋 项目规则

### 价格数据管理规则
- **爬取到的真实价格缓存在完全隔离的字段，不要和预测字段混淆**
- **真实价格是预测计算的唯一依据**
- **价格字段分离原则**：
  - `merged_prices`: 存储爬取到的真实价格数据
  - `predict_prices`: 存储基于真实价格计算的预测数据
  - `bing_prices`: 存储BING爬虫获取的价格数据
- **数据隔离**: 不同来源的价格数据必须存储在独立字段中，避免混淆

### 数据保护规则
- **所有爬取的数据不做删除，只做增量修正**
- **数据完整性**: 确保所有爬取到的有效数据得到保留
- **增量更新**: 新数据只做添加或更新，不删除已有数据

### BING爬取价格置信度模型规则
- **动态置信度计算**: 若单个场馆抓取到不同价格，每个价格的置信度不应该是一个常数
- **正态分布模型**: 为所有室内（含气膜）和室外的真实价格按价格高低建立正态分布模型
- **时段分离**: 可能的话分开黄金时段和非黄金时段建立模型
- **迭代动态模型**: 这个模型是以真实价格驱动的迭代动态模型
- **权重赋值**: 用这个模型的值为室内和室外之后爬取到的新价格赋值权重
- **中心权重原则**: 越靠近正态分布中心的价格权重越高
- **异常价格调整**: 对于室外≤30或≥300，室内≤50或≥500的价格，置信度在正态分布置信度基础上叠加不超过标准置信度的30%

### 置信度计算方法永久规则
- **核心原则**: 基于真实价格分布动态计算，不得使用固定常数
- **算法流程**: 
  1. 收集真实价格数据（BING、融合等字段）
  2. 建立正态分布模型（室内/室外，黄金/非黄金时段）
  3. 计算基础正态分布置信度
  4. 应用极端价格处理规则
- **极端价格处理**:
  - 完全排除：室内<30或>800，室外<20或>500，置信度设为0.0
  - 异常调整：室内≤80或≥400，室外≤50或≥250，调整幅度不超过20%
- **置信度范围**: 0.0 - 0.9
- **实施要求**: 所有价格置信度计算必须遵循此算法，详见`.cursor/rules/confidence-calculation.mdc`

---

⭐ 如果这个项目对你有帮助，请给它一个星标！ 