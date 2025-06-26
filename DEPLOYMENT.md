# 网球场地信息抓取系统部署指南

## 🚀 部署方式

### 1. Render 部署（推荐）

#### 步骤1：准备代码
1. 将代码推送到GitHub仓库
2. 确保包含以下文件：
   - `requirements.txt`
   - `runtime.txt`
   - `render.yaml`
   - `start.py`
   - `app/main.py`
   - `app/templates/index.html`

#### 步骤2：在Render上创建服务
1. 登录 [Render](https://render.com)
2. 点击 "New +" → "Web Service"
3. 连接GitHub仓库
4. 配置服务：
   - **Name**: tennis-court-scraper
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 步骤3：配置环境变量
在Render控制台中设置以下环境变量：
```
AMAP_API_KEY=your_amap_api_key_here
DATABASE_URL=sqlite:///./data/courts.db
DEBUG=false
```

#### 步骤4：部署
1. 点击 "Create Web Service"
2. 等待构建完成
3. 访问生成的URL

### 2. Railway 部署

#### 步骤1：准备代码
1. 将代码推送到GitHub仓库
2. 确保包含 `railway.json` 配置文件

#### 步骤2：在Railway上部署
1. 登录 [Railway](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择你的仓库
4. Railway会自动检测Python项目并部署

#### 步骤3：配置环境变量
在Railway控制台中设置环境变量：
```
AMAP_API_KEY=your_amap_api_key_here
DATABASE_URL=sqlite:///./data/courts.db
DEBUG=false
```

### 3. Vercel 部署

#### 步骤1：准备代码
1. 将代码推送到GitHub仓库
2. 确保包含 `vercel.json` 配置文件

#### 步骤2：在Vercel上部署
1. 登录 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 导入GitHub仓库
4. 配置构建设置：
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `app`
   - **Install Command**: `pip install -r requirements.txt`

#### 步骤3：配置环境变量
在Vercel控制台中设置环境变量：
```
AMAP_API_KEY=your_amap_api_key_here
DATABASE_URL=sqlite:///./data/courts.db
DEBUG=false
```

## 🔧 本地开发部署

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repo-url>
cd tennis_court_scraper
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

5. **初始化数据库**
```bash
python run.py
```

6. **启动应用**
```bash
python run.py
# 或
cd app && uvicorn main:app --reload
```

7. **访问应用**
打开浏览器访问: http://localhost:8000

## 🔑 获取高德地图API密钥

### 步骤1：注册高德开发者账号
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录开发者账号

### 步骤2：创建应用
1. 进入控制台
2. 点击 "应用管理" → "创建新应用"
3. 填写应用信息

### 步骤3：获取API密钥
1. 在应用详情页面找到 "Key"
2. 复制API密钥
3. 在环境变量中设置 `AMAP_API_KEY`

## 📊 数据库配置

### SQLite（默认）
- 适用于开发和测试
- 数据存储在 `data/courts.db` 文件中

### PostgreSQL（生产环境推荐）
1. 在Render/Railway上创建PostgreSQL数据库
2. 获取数据库连接URL
3. 设置环境变量：
```
DATABASE_URL=postgresql://username:password@host:port/database
```

## 🔍 监控和日志

### 应用监控
- 健康检查端点: `/api/health`
- 应用信息端点: `/api/info`
- 爬虫状态端点: `/api/scraper/status`

### 日志查看
- 本地开发：控制台输出
- Render：在服务控制台查看日志
- Railway：在部署日志中查看
- Vercel：在函数日志中查看

## 🚨 故障排除

### 常见问题

1. **应用无法启动**
   - 检查Python版本（需要3.8+）
   - 检查依赖是否正确安装
   - 检查环境变量配置

2. **数据库连接失败**
   - 检查DATABASE_URL配置
   - 确保数据库服务正常运行

3. **API密钥无效**
   - 检查AMAP_API_KEY是否正确设置
   - 确认API密钥有足够的配额

4. **爬虫功能异常**
   - 检查网络连接
   - 确认目标网站可访问
   - 检查请求频率限制

### 调试模式
设置环境变量启用调试模式：
```
DEBUG=true
```

## 📈 性能优化

### 数据库优化
- 定期清理过期数据
- 添加适当的索引
- 使用连接池

### 爬虫优化
- 调整请求间隔
- 使用代理IP轮换
- 实现断点续传

### 缓存策略
- 实现Redis缓存
- 缓存静态资源
- 使用CDN加速

## 🔒 安全考虑

### API安全
- 限制API访问频率
- 实现API密钥认证
- 使用HTTPS

### 数据安全
- 定期备份数据
- 加密敏感信息
- 实现访问控制

## 📞 支持

如果遇到部署问题，请：
1. 检查日志信息
2. 查看本文档的故障排除部分
3. 提交GitHub Issue
4. 联系技术支持

---

**祝您部署顺利！** 🎾 

## Render 部署

### 1. 准备工作

确保你的项目包含以下文件：
- `requirements.txt` - Python依赖
- `render.yaml` - Render配置文件
- `start.py` - 启动脚本
- `app/main.py` - 主应用文件
- `app/templates/index.html` - 模板文件

### 2. 部署步骤

1. 在Render控制台创建新的Web Service
2. 连接你的GitHub仓库
3. 选择Python环境
4. 配置环境变量（可选）：
   - `DATABASE_URL`: `sqlite:///./data/courts.db`
   - `DEBUG`: `false`
   - `AMAP_API_KEY`: 你的高德地图API密钥（可选）

### 3. 常见问题及解决方案

#### 问题1: 模板文件找不到
```
jinja2.exceptions.TemplateNotFound: 'index.html' not found
```

**解决方案:**
- 确保`app/templates/index.html`文件存在
- 检查`render.yaml`中的启动命令是否正确
- 使用`start.py`启动脚本进行诊断

#### 问题2: 数据库路径错误
```
sqlite3.OperationalError: unable to open database file
```

**解决方案:**
- 确保`data`目录存在
- 检查数据库文件权限
- 使用相对路径配置数据库

#### 问题3: 依赖安装失败
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案:**
- 检查`requirements.txt`是否包含所有依赖
- 确保Python版本兼容（推荐3.11+）
- 查看Render构建日志

#### 问题4: 端口配置错误
```
OSError: [Errno 98] Address already in use
```

**解决方案:**
- 使用环境变量`PORT`配置端口
- 确保绑定到`0.0.0.0`而不是`127.0.0.1`

### 4. 本地测试

在部署前，可以在本地测试部署环境：

```bash
# 运行部署测试
python test_deployment.py

# 使用启动脚本测试
python start.py
```

### 5. 环境变量配置

在Render控制台中配置以下环境变量：

| 变量名 | 值 | 说明 |
|--------|----|----|
| `DATABASE_URL` | `sqlite:///./data/courts.db` | 数据库连接字符串 |
| `DEBUG` | `false` | 调试模式 |
| `AMAP_API_KEY` | `your_api_key` | 高德地图API密钥（可选） |

### 6. 监控和日志

部署后，可以通过以下方式监控应用：

1. **健康检查**: 访问 `/api/health`
2. **API文档**: 访问 `/api/docs`
3. **应用信息**: 访问 `/api/info`

### 7. 故障排除

如果遇到问题，请按以下步骤排查：

1. 查看Render构建日志
2. 检查应用日志
3. 运行健康检查接口
4. 确认所有文件路径正确
5. 验证环境变量配置

### 8. 性能优化

- 使用SQLite数据库（适合小型应用）
- 启用静态文件缓存
- 配置适当的请求超时时间
- 监控内存使用情况

### 9. 安全注意事项

- 不要在生产环境中启用DEBUG模式
- 保护敏感的环境变量
- 定期更新依赖包
- 监控异常访问

## 本地开发

### 启动开发服务器

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 数据库初始化

```bash
# 初始化数据库
python -c "from app.database import init_db; init_db()"
```

### 运行测试

```bash
# 运行部署测试
python test_deployment.py

# 运行应用测试
python test_app.py
``` 