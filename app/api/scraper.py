from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
from ..database import get_db
from ..models import TennisCourt, CourtDetail
from ..scrapers.amap_scraper import AmapScraper
from ..config import settings

router = APIRouter(prefix="/api/scraper", tags=["scraper"])

@router.post("/scrape/amap")
def scrape_amap_data(
    area: str = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """触发高德地图数据抓取"""
    if area and area not in settings.target_areas:
        raise HTTPException(status_code=400, detail=f"无效的区域：{area}")
    
    # 如果没有指定区域，抓取所有区域
    areas_to_scrape = [area] if area else list(settings.target_areas.keys())
    
    # 在后台执行抓取任务
    if background_tasks:
        background_tasks.add_task(run_amap_scraping, areas_to_scrape, db)
        return {
            "message": f"已启动后台抓取任务，目标区域：{', '.join(areas_to_scrape)}",
            "areas": areas_to_scrape
        }
    else:
        # 同步执行
        results = run_amap_scraping(areas_to_scrape, db)
        return {
            "message": "数据抓取完成",
            "results": results
        }

@router.post("/scrape/all")
def scrape_all_sources(
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """触发所有数据源抓取"""
    if background_tasks:
        background_tasks.add_task(run_all_scraping, db)
        return {"message": "已启动所有数据源的后台抓取任务"}
    else:
        results = run_all_scraping(db)
        return {
            "message": "所有数据源抓取完成",
            "results": results
        }

@router.get("/status")
def get_scraper_status(db: Session = Depends(get_db)):
    """获取爬虫状态信息"""
    total_courts = db.query(TennisCourt).count()
    
    # 按数据来源统计
    source_stats = {}
    sources = db.query(TennisCourt.data_source).distinct().all()
    for source in sources:
        if source[0]:
            count = db.query(TennisCourt).filter(TennisCourt.data_source == source[0]).count()
            latest_update = db.query(TennisCourt.updated_at).filter(
                TennisCourt.data_source == source[0]
            ).order_by(TennisCourt.updated_at.desc()).first()
            
            source_stats[source[0]] = {
                "count": count,
                "latest_update": latest_update[0] if latest_update else None
            }
    
    return {
        "total_courts": total_courts,
        "source_stats": source_stats,
        "target_areas": settings.target_areas
    }

def run_amap_scraping(areas: List[str], db: Session) -> Dict:
    """执行高德地图数据抓取"""
    scraper = AmapScraper()
    results = {}
    
    for area in areas:
        try:
            print(f"开始抓取 {settings.target_areas[area]['name']} 区域数据...")
            courts_data = scraper.search_tennis_courts(area)
            
            # 保存到数据库
            saved_count = 0
            for court_data in courts_data:
                # 检查是否已存在
                existing = db.query(TennisCourt).filter(
                    TennisCourt.name == court_data.name,
                    TennisCourt.area == area
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.address = court_data.address
                    existing.phone = court_data.phone
                    existing.latitude = court_data.latitude
                    existing.longitude = court_data.longitude
                    existing.business_hours = court_data.business_hours
                    existing.description = court_data.description
                    existing.updated_at = datetime.now()
                    existing.data_source = court_data.data_source
                    existing.source_url = court_data.source_url
                else:
                    # 创建新记录
                    new_court = TennisCourt(
                        name=court_data.name,
                        address=court_data.address,
                        phone=court_data.phone,
                        area=area,
                        area_name=settings.target_areas[area]['name'],
                        latitude=court_data.latitude,
                        longitude=court_data.longitude,
                        business_hours=court_data.business_hours,
                        description=court_data.description,
                        data_source=court_data.data_source,
                        source_url=court_data.source_url
                    )
                    db.add(new_court)
                    saved_count += 1
            
            db.commit()
            results[area] = {
                "scraped": len(courts_data),
                "saved": saved_count,
                "updated": len(courts_data) - saved_count
            }
            
            print(f"{settings.target_areas[area]['name']} 区域抓取完成：{len(courts_data)} 个场馆")
            
        except Exception as e:
            print(f"抓取 {area} 区域时出错：{e}")
            results[area] = {"error": str(e)}
    
    return results

def run_all_scraping(db: Session) -> Dict:
    """执行所有数据源抓取"""
    results = {}
    
    # 高德地图抓取
    try:
        amap_results = run_amap_scraping(list(settings.target_areas.keys()), db)
        results["amap"] = amap_results
    except Exception as e:
        results["amap"] = {"error": str(e)}
    
    # TODO: 添加其他数据源抓取
    # results["dianping"] = run_dianping_scraping(db)
    # results["meituan"] = run_meituan_scraping(db)
    
    return results

@router.delete("/clear")
def clear_all_data(db: Session = Depends(get_db)):
    """清空所有数据"""
    try:
        db.query(TennisCourt).delete()
        db.commit()
        return {"message": "所有数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空数据失败：{str(e)}") 