from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import os

print('>>> main.py 启动')
try:
    from .config import settings
    print('>>> config导入成功')
except Exception as e:
    print('!!! config导入失败:', e)
    raise
from .database import init_db
from .api import courts, scraper, details

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
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

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="app/templates")

# 包含API路由
app.include_router(courts.router)
app.include_router(scraper.router)
app.include_router(details.router)

@app.get("/data/map_cache/{filename:path}")
async def serve_map_image(filename: str):
    """服务地图图片文件"""
    file_path = f"data/map_cache/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    else:
        return {"error": "Image not found"}, 404

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print(f"启动 {settings.app_name} v{settings.version}")
    init_db()
    print("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("应用正在关闭...")

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/detail", response_class=HTMLResponse)
async def read_detail(request: Request):
    """详情页面"""
    return templates.TemplateResponse("detail.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug
    }

@app.get("/api/info")
async def get_app_info():
    """获取应用信息"""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "target_areas": settings.target_areas,
        "data_sources": ["amap", "dianping", "meituan"]  # 计划支持的数据源
    }

if __name__ == "__main__":
    print('>>> main.py __main__ 入口')
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 