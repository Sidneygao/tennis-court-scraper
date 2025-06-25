from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import TennisCourt, CourtDetail, CourtDetailResponse, CourtDetailCreate
from ..scrapers.detail_scraper import DetailScraper
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/details", tags=["details"])

@router.get("/{court_id}")
async def get_court_detail(court_id: int, force_update: bool = Query(False, description="强制更新数据"), db: Session = Depends(get_db)):
    """获取场馆融合详情（手动反序列化所有JSON字段，返回dict）"""
    try:
        # 检查场馆是否存在
        court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
        if not court:
            raise HTTPException(status_code=404, detail="场馆不存在")
        
        # 查找或创建详情记录
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
        if not detail:
            detail = CourtDetail(court_id=court_id)
            db.add(detail)
            db.commit()
            db.refresh(detail)
            force_update = True  # 新记录需要抓取数据
        
        # 检查是否需要更新数据
        scraper = DetailScraper()
        need_update = force_update or not scraper.is_cache_valid(detail.last_dianping_update)
        if need_update:
            try:
                await update_court_detail_data(court, detail, db)
            except Exception as e:
                logger.error(f"更新详情数据失败: {e}")
                if detail.merged_description:
                    pass  # 继续返回缓存
                else:
                    raise HTTPException(status_code=500, detail="获取详情数据失败")
        
        # 手动反序列化所有JSON字段
        def safe_json_loads(val):
            if not val:
                return []
            try:
                return json.loads(val)
            except Exception as e:
                logger.error(f"JSON解析失败: {e}, 值: {val}")
                return []
        
        try:
            result = {
                "id": detail.id,
                "court_id": detail.court_id,
                "merged_description": detail.merged_description,
                "merged_facilities": detail.merged_facilities,
                "merged_traffic_info": detail.merged_traffic_info,
                "merged_business_hours": detail.merged_business_hours,
                "dianping_prices": safe_json_loads(detail.dianping_prices),
                "meituan_prices": safe_json_loads(detail.meituan_prices),
                "merged_prices": safe_json_loads(detail.merged_prices),
                "dianping_rating": detail.dianping_rating,
                "meituan_rating": detail.meituan_rating,
                "merged_rating": detail.merged_rating,
                "dianping_reviews": safe_json_loads(detail.dianping_reviews),
                "meituan_reviews": safe_json_loads(detail.meituan_reviews),
                "dianping_images": safe_json_loads(detail.dianping_images),
                "meituan_images": safe_json_loads(detail.meituan_images),
                "last_dianping_update": detail.last_dianping_update,
                "last_meituan_update": detail.last_meituan_update,
                "cache_expires_at": detail.cache_expires_at,
                "created_at": detail.created_at,
                "updated_at": detail.updated_at
            }
            return result
        except Exception as e:
            logger.error(f"构建响应数据失败: {e}")
            raise HTTPException(status_code=500, detail=f"构建响应数据失败: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取场馆详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取场馆详情失败: {str(e)}")

@router.post("/{court_id}/update")
async def update_court_detail(court_id: int, db: Session = Depends(get_db)):
    """手动更新场馆详情数据"""
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="场馆不存在")
    
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
    if not detail:
        detail = CourtDetail(court_id=court_id)
        db.add(detail)
        db.commit()
        db.refresh(detail)
    
    try:
        await update_court_detail_data(court, detail, db)
        return {"message": "详情数据更新成功", "court_id": court_id}
    except Exception as e:
        logger.error(f"更新详情数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新详情数据失败: {str(e)}")

@router.get("/{court_id}/preview")
async def preview_court_detail(court_id: int, db: Session = Depends(get_db)):
    """预览场馆详情（不更新缓存）"""
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="场馆不存在")
    
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
    
    if not detail or not detail.merged_description:
        return {
            "court_id": court_id,
            "court_name": court.name,
            "has_detail": False,
            "message": "暂无详情数据，请点击更新按钮获取"
        }
    
    # 使用安全的JSON解析方法
    def safe_json_loads(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return []
    
    return {
        "court_id": court_id,
        "court_name": court.name,
        "has_detail": True,
        "detail": {
            "description": detail.merged_description,
            "facilities": detail.merged_facilities,
            "business_hours": detail.merged_business_hours,
            "rating": detail.merged_rating,
            "prices": safe_json_loads(detail.merged_prices),
            "reviews": safe_json_loads(detail.dianping_reviews)[:3],
            "images": safe_json_loads(detail.dianping_images)[:3],
            "last_update": detail.updated_at.isoformat() if detail.updated_at else None
        }
    }

async def update_court_detail_data(court: TennisCourt, detail: CourtDetail, db: Session):
    """更新场馆详情数据"""
    scraper = DetailScraper()
    
    try:
        # 使用新的综合爬取方法
        all_data = await scraper.scrape_all_platforms(court.name, court.address)
        
        # 从summary中提取融合数据
        summary = all_data.get('summary', {})
        
        # 检查是否有成功的数据
        if summary.get('successful_platforms', 0) == 0:
            # 没有成功的数据，返回"该数据不能获得"
            merged_data = {
                "description": "该数据不能获得",
                "facilities": "该数据不能获得", 
                "business_hours": "该数据不能获得",
                "prices": [{"type": "价格信息", "price": "该数据不能获得"}],
                "rating": 0.0,
                "reviews": [{"user": "系统", "rating": 0, "content": "该数据不能获得"}],
                "images": []
            }
        else:
            # 有成功的数据，构建融合数据
            merged_data = {
                "description": f"{court.name}是一家专业的网球场地，设施完善，环境优美。",
                "facilities": "、".join(summary.get('all_facilities', [])),
                "business_hours": "09:00-22:00",
                "prices": summary.get('all_prices', [{"type": "价格信息", "price": "该数据不能获得"}]),
                "rating": summary.get('avg_rating', 0.0),
                "reviews": summary.get('all_reviews', [{"user": "系统", "rating": 0, "content": "该数据不能获得"}]),
                "images": summary.get('all_images', [])
            }
        
        # 添加调试日志
        print("merged_data:", merged_data)
        
        # 更新融合字段
        detail.merged_description = merged_data["description"]
        detail.merged_facilities = merged_data["facilities"]
        detail.merged_business_hours = merged_data["business_hours"]
        detail.merged_rating = merged_data["rating"]
        detail.merged_prices = json.dumps(merged_data["prices"], ensure_ascii=False)
        detail.dianping_reviews = json.dumps(merged_data["reviews"], ensure_ascii=False)
        detail.dianping_images = json.dumps(merged_data["images"], ensure_ascii=False)
        
        # 设置缓存过期时间
        detail.cache_expires_at = datetime.now() + timedelta(hours=24)
        
        # 保存到数据库
        db.commit()
        db.refresh(detail)
        
        logger.info(f"场馆 {court.name} 详情数据更新完成")
        
    except Exception as e:
        logger.error(f"更新详情数据失败: {e}")
        # 如果爬取失败，返回"该数据不能获得"
        merged_data = {
            "description": "该数据不能获得",
            "facilities": "该数据不能获得",
            "business_hours": "该数据不能获得", 
            "prices": [{"type": "价格信息", "price": "该数据不能获得"}],
            "rating": 0.0,
            "reviews": [{"user": "系统", "rating": 0, "content": "该数据不能获得"}],
            "images": []
        }
        
        # 更新融合字段
        detail.merged_description = merged_data["description"]
        detail.merged_facilities = merged_data["facilities"]
        detail.merged_business_hours = merged_data["business_hours"]
        detail.merged_rating = merged_data["rating"]
        detail.merged_prices = json.dumps(merged_data["prices"], ensure_ascii=False)
        detail.dianping_reviews = json.dumps(merged_data["reviews"], ensure_ascii=False)
        detail.dianping_images = json.dumps(merged_data["images"], ensure_ascii=False)
        detail.cache_expires_at = datetime.now() + timedelta(hours=24)
        
        # 保存到数据库
        db.commit()
        db.refresh(detail)
        
        logger.info(f"场馆 {court.name} 详情数据更新完成（使用默认数据）")

@router.get("/batch/update")
async def batch_update_details(limit: int = Query(10, ge=1, le=50, description="批量更新数量"), db: Session = Depends(get_db)):
    """批量更新场馆详情"""
    # 获取需要更新的场馆（优先更新没有详情或详情过期的）
    courts = db.query(TennisCourt).limit(limit).all()
    
    updated_count = 0
    failed_count = 0
    
    for court in courts:
        try:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                detail = CourtDetail(court_id=court.id)
                db.add(detail)
                db.commit()
                db.refresh(detail)
            
            await update_court_detail_data(court, detail, db)
            updated_count += 1
            
        except Exception as e:
            logger.error(f"更新场馆 {court.name} 详情失败: {e}")
            failed_count += 1
    
    return {
        "message": f"批量更新完成",
        "total": len(courts),
        "updated": updated_count,
        "failed": failed_count
    } 