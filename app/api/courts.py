from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import TennisCourt, TennisCourtResponse, TennisCourtCreate, TennisCourtUpdate, CourtDetail
from ..config import settings
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)
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

@router.get("/")
async def get_courts(
    limit: int = Query(1000, ge=1, le=10000, description="返回数量限制"),
    area: Optional[str] = Query(None, description="区域筛选"),
    db: Session = Depends(get_db)
):
    """获取场馆列表"""
    try:
        query = db.query(TennisCourt)
        
        if area:
            if area not in settings.target_areas:
                raise HTTPException(status_code=400, detail=f"无效的区域：{area}")
            query = query.filter(TennisCourt.area == area)
        
        courts = query.limit(limit).all()
        
        # 为每个场馆添加价格信息
        result = []
        for court in courts:
            court_data = {
                "id": court.id,
                "name": court.name,
                "address": court.address,
                "phone": court.phone,
                "area": court.area,
                "area_name": court.area_name,
                "latitude": court.latitude,
                "longitude": court.longitude,
                "court_type": court.court_type,
                "has_roof": court.has_roof,
                "court_count": court.court_count,
                "business_hours": court.business_hours,
                "is_open": court.is_open,
                "description": court.description,
                "facilities": court.facilities,
                "traffic_info": court.traffic_info,
                "data_source": court.data_source,
                "source_url": court.source_url,
                "created_at": court.created_at,
                "updated_at": court.updated_at,
                "price_updated_at": court.price_updated_at,
                # 添加价格信息
                "real_prices": [],
                "predicted_prices": None,
                "comment": court.description or "",
                "rating": ""
            }
            
            # 价格可疑判断函数
            def is_suspicious_price(val):
                try:
                    v = float(val)
                    return v < 50 or v > 500
                except Exception:
                    return True
            
            # 从基础字段构建真实价格
            if court.peak_price or court.off_peak_price or court.member_price:
                real_prices = []
                if court.peak_price:
                    suspicious = is_suspicious_price(court.peak_price)
                    real_prices.append({
                        "type": "黄金时段",
                        "value": court.peak_price,
                        "unit": court.price_unit or "元/小时",
                        "source": "场馆信息",
                        "suspicious": suspicious
                    })
                if court.off_peak_price:
                    suspicious = is_suspicious_price(court.off_peak_price)
                    real_prices.append({
                        "type": "非黄金时段",
                        "value": court.off_peak_price,
                        "unit": court.price_unit or "元/小时",
                        "source": "场馆信息",
                        "suspicious": suspicious
                    })
                if court.member_price:
                    suspicious = is_suspicious_price(court.member_price)
                    real_prices.append({
                        "type": "会员价",
                        "value": court.member_price,
                        "unit": court.price_unit or "元/小时",
                        "source": "场馆信息",
                        "suspicious": suspicious
                    })
                # 只在主卡片返回real_prices，详情接口不返回
                court_data["real_prices"] = real_prices
            
            # 添加预测价格（基于场地类型）
            court_type = court.court_type or "气膜"
            predicted_prices = get_predicted_prices_by_type(court_type)
            if predicted_prices:
                court_data["predicted_prices"] = [
                    {
                        "type": "预测最高",
                        "value": predicted_prices["max"],
                        "unit": predicted_prices["unit"],
                        "type_label": "预测价格",
                        "source": "价格预测"
                    },
                    {
                        "type": "预测中点",
                        "value": predicted_prices["mid"],
                        "unit": predicted_prices["unit"],
                        "type_label": "预测价格",
                        "source": "价格预测"
                    },
                    {
                        "type": "预测最低",
                        "value": predicted_prices["min"],
                        "unit": predicted_prices["unit"],
                        "type_label": "预测价格",
                        "source": "价格预测"
                    }
                ]
            
            # 评论和评分如无真实数据则留空
            if not court.description or court.description == "未抓取到有效信息":
                court_data["comment"] = ""
            court_data["rating"] = ""
            
            result.append(court_data)
        
        return result
        
    except Exception as e:
        logger.error(f"获取场馆列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取场馆列表失败: {str(e)}")

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

def get_predicted_prices_by_type(court_type: str) -> dict:
    """根据场地类型获取预测价格"""
    # 基于场地类型的预测价格
    price_ranges = {
        "室内": {"min": 150, "max": 300, "mid": 225, "unit": "元/小时"},
        "气膜": {"min": 120, "max": 250, "mid": 185, "unit": "元/小时"},
        "室外": {"min": 80, "max": 180, "mid": 130, "unit": "元/小时"}
    }
    
    # 根据场地类型返回对应价格范围
    for type_key, prices in price_ranges.items():
        if type_key in court_type:
            return prices
    
    # 默认返回气膜价格
    return price_ranges["气膜"] 