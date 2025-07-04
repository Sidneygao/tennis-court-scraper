from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import TennisCourt, TennisCourtResponse, TennisCourtCreate, TennisCourtUpdate
from ..config import settings
from ..scrapers.price_predictor import PricePredictor
from urllib.parse import quote

router = APIRouter(prefix="/api/courts", tags=["courts"])

@router.get("/search_urls")
def get_courts_search_urls(db: Session = Depends(get_db)):
    """获取所有场馆的名称及点评/美团搜索URL"""
    courts = db.query(TennisCourt).all()
    result = []
    for c in courts:
        result.append({
            "name": c.name,
            "dianping_url": f"https://www.dianping.com/search/keyword/2_0_{quote(c.name)}",
            "meituan_url": f"https://www.meituan.com/s/{quote(c.name)}/"
        })
    return result

def get_dynamic_area(court):
    """根据场馆信息动态判断区域归属"""
    name = court.name or ""
    address = court.address or ""
    # 坐标修复后：latitude存储经度，longitude存储纬度
    longitude = court.latitude or 0  # 修复：使用latitude字段作为经度
    latitude = court.longitude or 0  # 修复：使用longitude字段作为纬度
    
    # 丰台区判断：按经度116.321分界
    if '丰台' in name or '丰台' in address:
        if longitude > 116.321:
            return 'fengtai_east'  # 丰台区东部
        else:
            return 'fengtai_west'  # 丰台区西部
    
    # 亦庄判断
    elif '亦庄' in name or '亦庄' in address:
        return 'yizhuang'
    
    # 其他区域使用原有area字段
    return court.area

@router.get("/", response_model=List[TennisCourtResponse])
def get_courts(
    area: Optional[str] = Query(None, description="区域筛选：wangjing, dongba, jiuxianqiao, fengtai_east, fengtai_west, yizhuang"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取网球场馆列表"""
    query = db.query(TennisCourt)
    
    # 不再过滤类型为空的场馆，因为我们会实时判断类型
    # query = query.filter(TennisCourt.court_type != '').filter(TennisCourt.court_type.isnot(None))
    
    if area:
        if area not in settings.target_areas:
            raise HTTPException(status_code=400, detail=f"无效的区域：{area}")
        
        # 所有区域都使用数据库中的area字段，包括丰台和亦庄
        query = query.filter(TennisCourt.area == area)
    
    courts = query.offset(skip).limit(limit).all()
    
    # 实时判断每个场馆的类型，覆盖数据库字段
    predictor = PricePredictor()
    for court in courts:
        court.court_type = predictor.determine_court_type(court.name, court.address)
    
    return courts

@router.get("/{court_id}", response_model=TennisCourtResponse)
def get_court(court_id: int, db: Session = Depends(get_db)):
    """获取单个网球场馆详情"""
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="网球场馆不存在")
    
    # 实时判断场馆类型，覆盖数据库字段
    predictor = PricePredictor()
    court.court_type = predictor.determine_court_type(court.name, court.address)
    
    return court

@router.post("/", response_model=TennisCourtResponse)
def create_court(court: TennisCourtCreate, db: Session = Depends(get_db)):
    """创建新的网球场馆"""
    db_court = TennisCourt(**court.dict())
    db.add(db_court)
    db.commit()
    db.refresh(db_court)
    return db_court

@router.put("/{court_id}", response_model=TennisCourtResponse)
def update_court(court_id: int, court: TennisCourtUpdate, db: Session = Depends(get_db)):
    """更新网球场馆信息"""
    db_court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not db_court:
        raise HTTPException(status_code=404, detail="网球场馆不存在")
    
    update_data = court.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_court, field, value)
    
    db.commit()
    db.refresh(db_court)
    return db_court

@router.delete("/{court_id}")
def delete_court(court_id: int, db: Session = Depends(get_db)):
    """删除网球场馆"""
    db_court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not db_court:
        raise HTTPException(status_code=404, detail="网球场馆不存在")
    
    db.delete(db_court)
    db.commit()
    return {"message": "网球场馆已删除"}

@router.get("/areas/list")
def get_areas():
    """获取所有可用区域"""
    return {
        "areas": [
            {
                "key": key,
                "name": config["name"],
                "center": config["center"],
                "radius": config["radius"]
            }
            for key, config in settings.target_areas.items()
        ]
    }

@router.get("/{court_id}/coordinates")
def get_court_coordinates(court_id: int, db: Session = Depends(get_db)):
    """获取场馆坐标信息"""
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="网球场馆不存在")
    
    # 返回坐标信息（注意：latitude存储经度，longitude存储纬度）
    return {
        "court_id": court_id,
        "court_name": court.name,
        "latitude": court.latitude,  # 经度
        "longitude": court.longitude,  # 纬度
        "address": court.address
    }

@router.get("/stats/summary")
def get_courts_summary(db: Session = Depends(get_db)):
    """获取网球场馆统计信息"""
    # 获取所有场馆，实时判断类型
    all_courts = db.query(TennisCourt).all()
    predictor = PricePredictor()
    
    # 实时判断每个场馆的类型
    total_courts = 0
    area_stats = {}
    source_stats = {}
    
    for court in all_courts:
        court_type = predictor.determine_court_type(court.name, court.address)
        if court_type and court_type != "未知":
            total_courts += 1
            
            # 按区域统计
            if court.area in settings.target_areas:
                if court.area not in area_stats:
                    area_stats[court.area] = {
                        "name": settings.target_areas[court.area]["name"],
                        "count": 0
                    }
                area_stats[court.area]["count"] += 1
            
            # 按数据来源统计
            if court.data_source:
                if court.data_source not in source_stats:
                    source_stats[court.data_source] = 0
                source_stats[court.data_source] += 1
    
    return {
        "total_courts": total_courts,
        "area_stats": area_stats,
        "source_stats": source_stats
    } 