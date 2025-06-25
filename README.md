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

---

⭐ 如果这个项目对你有帮助，请给它一个星标！ 