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
    
    # 检查并导入数据
    try:
        from .database import get_db
        from .models import TennisCourt
        
        db = next(get_db())
        court_count = db.query(TennisCourt).count()
        print(f"数据库场馆数量: {court_count}")
        
        if court_count == 0:
            print("数据库为空，尝试导入数据...")
            await import_initial_data()
        else:
            print("数据库已有数据，无需导入")
            
    except Exception as e:
        print(f"数据检查失败: {e}")
    
    print("应用启动完成")

async def import_initial_data():
    """导入初始数据"""
    try:
        import json
        from .database import get_db
        from .models import TennisCourt, CourtDetail
        from datetime import datetime
        
        # 优先使用完整数据文件
        data_file = "complete_courts_data.json"
        if not os.path.exists(data_file):
            data_file = "courts_data.json"
            if not os.path.exists(data_file):
                print(f"数据文件不存在，跳过导入")
                return
        
        # 读取数据
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 判断数据格式
        if 'courts' in data and 'details' in data:
            # 完整数据格式
            courts_data = data['courts']
            details_data = data['details']
            print(f"读取到完整数据: {len(courts_data)} 个场馆, {len(details_data)} 个详情")
        else:
            # 旧格式，只有场馆数据
            courts_data = data
            details_data = []
            print(f"读取到场馆数据: {len(courts_data)} 个场馆")
        
        # 导入数据
        db = next(get_db())
        imported_courts = 0
        imported_details = 0
        
        # 导入场馆数据
        for court_data in courts_data:
            try:
                # 处理时间字段
                created_at = None
                updated_at = None
                if court_data.get('created_at'):
                    created_at = datetime.fromisoformat(court_data['created_at'])
                if court_data.get('updated_at'):
                    updated_at = datetime.fromisoformat(court_data['updated_at'])
                
                # 创建场馆对象
                court = TennisCourt(
                    id=court_data.get('id'),  # 保持原有ID
                    name=court_data.get('name'),
                    address=court_data.get('address'),
                    area=court_data.get('area'),
                    area_name=court_data.get('area_name'),
                    court_type=court_data.get('court_type'),
                    phone=court_data.get('phone'),
                    latitude=court_data.get('latitude'),
                    longitude=court_data.get('longitude'),
                    has_roof=court_data.get('has_roof', False),
                    court_count=court_data.get('court_count', 1),
                    business_hours=court_data.get('business_hours'),
                    is_open=court_data.get('is_open', True),
                    peak_price=court_data.get('peak_price'),
                    off_peak_price=court_data.get('off_peak_price'),
                    member_price=court_data.get('member_price'),
                    price_unit=court_data.get('price_unit'),
                    description=court_data.get('description'),
                    facilities=court_data.get('facilities'),
                    traffic_info=court_data.get('traffic_info'),
                    data_source=court_data.get('data_source'),
                    source_url=court_data.get('source_url'),
                    created_at=created_at,
                    updated_at=updated_at,
                    price_updated_at=court_data.get('price_updated_at')
                )
                
                db.add(court)
                imported_courts += 1
                
            except Exception as e:
                print(f"导入场馆 {court_data.get('name', 'unknown')} 失败: {e}")
                continue
        
        # 提交场馆数据
        db.commit()
        print(f"✅ 场馆数据导入完成: {imported_courts} 个场馆")
        
        # 导入详情数据
        for detail_data in details_data:
            try:
                # 处理时间字段
                created_at = None
                updated_at = None
                if detail_data.get('created_at'):
                    created_at = datetime.fromisoformat(detail_data['created_at'])
                if detail_data.get('updated_at'):
                    updated_at = datetime.fromisoformat(detail_data['updated_at'])
                
                # 创建详情对象
                detail = CourtDetail(
                    id=detail_data.get('id'),  # 保持原有ID
                    court_id=detail_data.get('court_id'),
                    merged_description=detail_data.get('merged_description'),
                    merged_facilities=detail_data.get('merged_facilities'),
                    merged_traffic_info=detail_data.get('merged_traffic_info'),
                    merged_business_hours=detail_data.get('merged_business_hours'),
                    prices=detail_data.get('prices'),
                    dianping_prices=detail_data.get('dianping_prices'),
                    meituan_prices=detail_data.get('meituan_prices'),
                    merged_prices=detail_data.get('merged_prices'),
                    predict_prices=detail_data.get('predict_prices'),
                    bing_prices=detail_data.get('bing_prices'),
                    dianping_rating=detail_data.get('dianping_rating'),
                    meituan_rating=detail_data.get('meituan_rating'),
                    merged_rating=detail_data.get('merged_rating'),
                    dianping_reviews=detail_data.get('dianping_reviews'),
                    meituan_reviews=detail_data.get('meituan_reviews'),
                    dianping_images=detail_data.get('dianping_images'),
                    meituan_images=detail_data.get('meituan_images'),
                    map_image=detail_data.get('map_image'),
                    last_dianping_update=detail_data.get('last_dianping_update'),
                    last_meituan_update=detail_data.get('last_meituan_update'),
                    cache_expires_at=detail_data.get('cache_expires_at'),
                    manual_prices=detail_data.get('manual_prices'),
                    manual_remark=detail_data.get('manual_remark'),
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                db.add(detail)
                imported_details += 1
                
            except Exception as e:
                print(f"导入详情 {detail_data.get('court_id', 'unknown')} 失败: {e}")
                continue
        
        # 提交详情数据
        db.commit()
        print(f"✅ 详情数据导入完成: {imported_details} 个详情")
        print(f"✅ 总导入完成: {imported_courts} 个场馆, {imported_details} 个详情")
        
    except Exception as e:
        print(f"数据导入失败: {e}")

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