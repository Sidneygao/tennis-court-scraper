from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .config import settings
from .database import init_db
from .api import courts, scraper, details

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="北京网球场馆信息抓取系统",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 尝试多种可能的模板路径
def get_template_directory():
    """获取模板目录路径"""
    possible_paths = [
        os.path.join(BASE_DIR, "templates"),  # app/templates
        os.path.join(os.getcwd(), "app", "templates"),  # ./app/templates
        os.path.join(os.getcwd(), "templates"),  # ./templates
        "/opt/render/project/src/app/templates",  # Render环境
        "/opt/render/project/src/templates",  # Render环境备用
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.exists(os.path.join(path, "index.html")):
            logger.info(f"找到模板目录: {path}")
            return path
    
    # 如果都找不到，尝试创建目录并复制模板文件
    default_path = os.path.join(BASE_DIR, "templates")
    logger.warning(f"使用默认模板目录: {default_path}")
    
    # 确保目录存在
    os.makedirs(default_path, exist_ok=True)
    
    # 如果index.html不存在，创建一个基本的模板
    index_path = os.path.join(default_path, "index.html")
    if not os.path.exists(index_path):
        logger.warning("创建基本模板文件")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>北京网球场馆信息抓取系统</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .api-links { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 20px 0; }
        .api-link { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        .api-link:hover { background: #0056b3; }
        .status { text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>北京网球场馆信息抓取系统</h1>
        <div class="status">
            <p>系统运行正常</p>
            <p>模板文件已自动生成</p>
        </div>
        <div class="api-links">
            <a href="/api/docs" class="api-link">API文档</a>
            <a href="/api/courts/" class="api-link">场馆列表</a>
            <a href="/api/health" class="api-link">健康检查</a>
        </div>
    </div>
</body>
</html>""")
    
    return default_path

# 获取模板目录并记录
TEMPLATE_DIR = get_template_directory()

# 挂载静态文件
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"挂载静态文件目录: {static_dir}")
else:
    # 尝试其他可能的静态文件路径
    static_paths = [
        os.path.join(os.getcwd(), "app", "static"),
        os.path.join(os.getcwd(), "static"),
    ]
    for path in static_paths:
        if os.path.exists(path):
            app.mount("/static", StaticFiles(directory=path), name="static")
            logger.info(f"挂载静态文件目录: {path}")
            break
    else:
        logger.warning("未找到静态文件目录")

# 设置模板
try:
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    logger.info(f"模板目录设置成功: {TEMPLATE_DIR}")
except Exception as e:
    logger.error(f"设置模板目录失败: {e}")
    # 使用一个基本的模板目录作为后备
    templates = None

# 包含API路由
app.include_router(courts.router)
app.include_router(scraper.router)
app.include_router(details.router)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    try:
        logger.info(f"启动 {settings.app_name} v{settings.app_version}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"应用目录: {BASE_DIR}")
        
        # 初始化数据库
        init_db()
        logger.info("数据库初始化完成")
        
        # 检查关键文件
        logger.info(f"模板目录: {TEMPLATE_DIR}")
        
        static_dir = os.path.join(BASE_DIR, "static")
        logger.info(f"静态文件目录: {static_dir}")
        
        logger.info("应用启动完成")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("应用正在关闭...")

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {exc}")
    logger.error(f"请求路径: {request.url}")
    logger.error(f"请求方法: {request.method}")
    
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>系统错误</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: red; }}
                .info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>系统错误</h1>
            <div class="error">
                <h2>发生错误</h2>
                <p>{str(exc)}</p>
            </div>
            <div class="info">
                <h3>请求信息:</h3>
                <ul>
                    <li>路径: {request.url}</li>
                    <li>方法: {request.method}</li>
                    <li>时间: {datetime.now()}</li>
                </ul>
            </div>
            <p><a href="/">返回主页</a></p>
            <p><a href="/api/health">健康检查</a></p>
        </body>
        </html>
        """,
        status_code=500
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    try:
        if templates is None:
            raise Exception("模板系统未初始化")
        
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"模板加载失败: {e}")
        
        # 收集诊断信息
        import os
        
        # 收集诊断信息
        cwd = os.getcwd()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检查文件存在性
        template_exists = os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html'))
        
        diagnostic_info = f"""
        <h3>诊断信息:</h3>
        <ul>
            <li>当前工作目录: {cwd}</li>
            <li>应用目录: {base_dir}</li>
            <li>模板目录: {TEMPLATE_DIR}</li>
            <li>模板目录存在: {os.path.exists(TEMPLATE_DIR)}</li>
            <li>index.html存在: {template_exists}</li>
            <li>错误信息: {str(e)}</li>
        </ul>
        """
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>北京网球场馆信息抓取系统</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: red; }}
                .info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>北京网球场馆信息抓取系统</h1>
            <p class="success">✅ 系统正在运行中...</p>
            <p><a href="/api/health">健康检查</a></p>
            <p><a href="/api/docs">API文档</a></p>
            <div class="error">
                <h2>模板加载错误</h2>
                <p>{str(e)}</p>
            </div>
            <div class="info">
                {diagnostic_info}
            </div>
        </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "template_dir": TEMPLATE_DIR,
        "template_exists": os.path.exists(TEMPLATE_DIR),
        "index_exists": os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html')) if os.path.exists(TEMPLATE_DIR) else False
    }

@app.get("/api/info")
async def get_app_info():
    """获取应用信息"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "target_areas": settings.target_areas,
        "data_sources": ["amap", "dianping", "meituan"]  # 计划支持的数据源
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 