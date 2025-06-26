from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

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
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.exists(os.path.join(path, "index.html")):
            print(f"找到模板目录: {path}")
            return path
    
    # 如果都找不到，返回默认路径
    default_path = os.path.join(BASE_DIR, "templates")
    print(f"使用默认模板目录: {default_path}")
    return default_path

# 挂载静态文件
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # 尝试其他可能的静态文件路径
    static_paths = [
        os.path.join(os.getcwd(), "app", "static"),
        os.path.join(os.getcwd(), "static"),
    ]
    for path in static_paths:
        if os.path.exists(path):
            app.mount("/static", StaticFiles(directory=path), name="static")
            break

# 设置模板
template_dir = get_template_directory()
templates = Jinja2Templates(directory=template_dir)

# 包含API路由
app.include_router(courts.router)
app.include_router(scraper.router)
app.include_router(details.router)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print(f"启动 {settings.app_name} v{settings.app_version}")
    init_db()
    print("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("应用正在关闭...")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        # 如果模板加载失败，返回详细的诊断信息
        import os
        
        # 收集诊断信息
        cwd = os.getcwd()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = templates.directory
        
        diagnostic_info = f"""
        <h3>诊断信息:</h3>
        <ul>
            <li>当前工作目录: {cwd}</li>
            <li>应用目录: {base_dir}</li>
            <li>模板目录: {template_dir}</li>
            <li>模板目录存在: {os.path.exists(template_dir)}</li>
            <li>index.html存在: {os.path.exists(os.path.join(template_dir, 'index.html')) if os.path.exists(template_dir) else 'N/A'}</li>
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
            </style>
        </head>
        <body>
            <h1>北京网球场馆信息抓取系统</h1>
            <p>系统正在运行中...</p>
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
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug
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