from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import TennisCourt, TennisCourtResponse, TennisCourtCreate, TennisCourtUpdate
from ..config import settings
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

@router.get("/", response_model=List[TennisCourtResponse])
def get_courts(
    area: Optional[str] = Query(None, description="区域筛选：wangjing, dongba, jiuxianqiao"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取网球场馆列表"""
    query = db.query(TennisCourt)
    
    if area:
        if area not in settings.target_areas:
            raise HTTPException(status_code=400, detail=f"无效的区域：{area}")
        query = query.filter(TennisCourt.area == area)
    
    courts = query.offset(skip).limit(limit).all()
    return courts

@router.get("/{court_id}", response_model=TennisCourtResponse)
def get_court(court_id: int, db: Session = Depends(get_db)):
    """获取单个网球场馆详情"""
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="网球场馆不存在")
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

@router.get("/stats/summary")
def get_courts_summary(db: Session = Depends(get_db)):
    """获取网球场馆统计信息"""
    total_courts = db.query(TennisCourt).count()
    
    area_stats = {}
    for area_key in settings.target_areas.keys():
        count = db.query(TennisCourt).filter(TennisCourt.area == area_key).count()
        area_stats[area_key] = {
            "name": settings.target_areas[area_key]["name"],
            "count": count
        }
    
    # 按数据来源统计
    source_stats = {}
    sources = db.query(TennisCourt.data_source).distinct().all()
    for source in sources:
        if source[0]:
            count = db.query(TennisCourt).filter(TennisCourt.data_source == source[0]).count()
            source_stats[source[0]] = count
    
    return {
        "total_courts": total_courts,
        "area_stats": area_stats,
        "source_stats": source_stats
    } 