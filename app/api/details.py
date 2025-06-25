from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from ..database import get_db
from ..models import TennisCourt, CourtDetail, CourtDetailResponse
from ..scrapers.detail_scraper import DetailScraper
from ..scrapers.price_predictor import PricePredictor
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/details", tags=["details"])

# 全局价格预测器实例
price_predictor = PricePredictor()

@router.get("/{court_id}")
async def get_court_detail(court_id: int, force_update: bool = Query(False, description="强制更新数据"), db: Session = Depends(get_db)):
    """获取场馆融合详情（带缓存比较功能）"""
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
                # 获取当前缓存的数据
                current_data = {
                    'description': detail.merged_description,
                    'facilities': detail.merged_facilities,
                    'business_hours': detail.merged_business_hours,
                    'prices': json.loads(detail.merged_prices) if detail.merged_prices else [],
                    'rating': detail.merged_rating or 0,
                    'reviews': json.loads(detail.dianping_reviews) if detail.dianping_reviews else [],
                    'images': json.loads(detail.dianping_images) if detail.dianping_images else []
                }
                
                # 爬取新数据
                await update_court_detail_data_with_cache(court, detail, current_data, db)
                
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
    """手动更新场馆详情数据（带缓存比较）"""
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
        # 获取当前缓存的数据
        current_data = {
            'description': detail.merged_description,
            'facilities': detail.merged_facilities,
            'business_hours': detail.merged_business_hours,
            'prices': json.loads(detail.merged_prices) if detail.merged_prices else [],
            'rating': detail.merged_rating or 0,
            'reviews': json.loads(detail.dianping_reviews) if detail.dianping_reviews else [],
            'images': json.loads(detail.dianping_images) if detail.dianping_images else []
        }
        
        # 更新数据（带缓存比较）
        changes = await update_court_detail_data_with_cache(court, detail, current_data, db)
        
        if changes:
            return {
                "message": "详情数据更新成功", 
                "court_id": court_id,
                "changes": changes,
                "updated_fields": [k for k, v in changes.items() if v]
            }
        else:
            return {
                "message": "数据无变化，无需更新", 
                "court_id": court_id,
                "changes": changes
            }
            
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
    
    # 检查是否有真实抓取的数据
    reviews = safe_json_loads(detail.dianping_reviews)
    has_real_reviews = len(reviews) > 0 and not all(review.get('content', '').startswith('该数据不能获得') for review in reviews)
    
    # 过滤掉虚拟评论
    real_reviews = []
    if has_real_reviews:
        for review in reviews:
            if not review.get('content', '').startswith('该数据不能获得') and review.get('content', '').strip():
                real_reviews.append(review)

    # 过滤虚拟设施
    facilities = detail.merged_facilities
    if not facilities or facilities == '该数据不能获得':
        facilities = ''

    # 处理价格信息，添加类型标识和suspicious标记
    prices = safe_json_loads(detail.merged_prices)
    processed_prices = []

    # 新增：价格可疑判断函数
    def is_suspicious_price(val):
        try:
            v = float(val)
            return v < 50 or v > 500
        except Exception:
            return True

    if prices:
        for price in prices:
            if isinstance(price, dict):
                price_value = price.get('value', '')
                suspicious = is_suspicious_price(price_value)
                if price_value and str(price_value).isdigit() and float(price_value) > 0:
                    price['type_label'] = '真实价格'
                    price['source'] = price.get('source', '场馆信息')
                    price['suspicious'] = suspicious
                else:
                    price['type_label'] = '预测价格'
                    price['source'] = '价格预测'
                    price['suspicious'] = False
                processed_prices.append(price)

    # 只保留合理区间的真实价格参与后续模型
    valid_prices = [p for p in processed_prices if not p.get('suspicious', False) and p.get('type_label') == '真实价格']
    if not valid_prices:
        # 没有合理真实价格，添加预测价格
        court_type = court.court_type or "气膜"
        predicted_prices = get_predicted_prices_by_type(court_type, db)
        if predicted_prices:
            processed_prices = [
                {
                    "type": "预测最高",
                    "value": predicted_prices["max"],
                    "unit": predicted_prices["unit"],
                    "type_label": "预测价格",
                    "source": "价格预测",
                    "suspicious": False
                },
                {
                    "type": "预测中点", 
                    "value": predicted_prices["mid"],
                    "unit": predicted_prices["unit"],
                    "type_label": "预测价格",
                    "source": "价格预测",
                    "suspicious": False
                },
                {
                    "type": "预测最低",
                    "value": predicted_prices["min"], 
                    "unit": predicted_prices["unit"],
                    "type_label": "预测价格",
                    "source": "价格预测",
                    "suspicious": False
                }
            ]
        else:
            processed_prices = []
    else:
        processed_prices = valid_prices + [p for p in processed_prices if p.get('suspicious', False)]
    
    return {
        "court_id": court_id,
        "court_name": court.name,
        "has_detail": True,
        "detail": {
            "description": detail.merged_description,
            "facilities": facilities,
            "business_hours": detail.merged_business_hours,
            "rating": detail.merged_rating,
            "prices": processed_prices,
            "reviews": real_reviews[:3],
            "reviews_status": "未抓取到有效信息" if not real_reviews else f"已抓取 {len(real_reviews)} 条真实评论",
            "images": safe_json_loads(detail.dianping_images)[:3],
            "last_update": detail.updated_at.isoformat() if detail.updated_at else None
        }
    }

def get_predicted_prices_by_type(court_type: str, db: Session = None) -> dict:
    """根据场地类型和数据库真实价格动态生成预测价格"""
    # 默认静态区间
    static_price_ranges = {
        "室内": {"min": 150, "max": 300, "mid": 225, "unit": "元/小时"},
        "气膜": {"min": 120, "max": 250, "mid": 185, "unit": "元/小时"},
        "室外": {"min": 80, "max": 180, "mid": 130, "unit": "元/小时"}
    }
    if db is None:
        return static_price_ranges["气膜"]
    # 动态聚合真实价格
    from app.models import CourtDetail, TennisCourt
    import json
    prices = []
    details = db.query(CourtDetail, TennisCourt).join(TennisCourt, CourtDetail.court_id == TennisCourt.id).all()
    for detail, court in details:
        if court_type in (court.court_type or "") and detail.merged_prices:
            try:
                price_list = json.loads(detail.merged_prices)
                for p in price_list:
                    v = p.get("value") if isinstance(p, dict) else None
                    if v and str(v).isdigit():
                        v = float(v)
                        if 30 <= v <= 800:
                            prices.append(v)
            except Exception:
                continue
    if prices:
        min_p = min(prices)
        max_p = max(prices)
        mid_p = sum(prices) / len(prices)
        return {"min": int(min_p), "max": int(max_p), "mid": int(mid_p), "unit": "元/小时"}
    # 没有真实数据则用静态区间
    for type_key, val in static_price_ranges.items():
        if type_key in court_type:
            return val
    return static_price_ranges["气膜"]

async def update_court_detail_data_with_cache(court: TennisCourt, detail: CourtDetail, current_data: dict, db: Session) -> dict:
    """更新场馆详情数据（带缓存比较）"""
    scraper = DetailScraper()
    
    try:
        # 使用新的综合爬取方法
        all_data = await scraper.scrape_all_platforms(court.name, court.address)
        
        # 从summary中提取融合数据
        summary = all_data.get('summary', {})
        
        # 检查是否有成功的数据
        if summary.get('successful_platforms', 0) == 0:
            # 没有成功的数据，返回"该数据不能获得"
            new_data = {
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
            new_data = {
                "description": f"{court.name}是一家专业的网球场地，设施完善，环境优美。",
                "facilities": "、".join(summary.get('all_facilities', [])),
                "business_hours": "09:00-22:00",
                "prices": summary.get('all_prices', [{"type": "价格信息", "price": "该数据不能获得"}]),
                "rating": summary.get('avg_rating', 0.0),
                "reviews": summary.get('all_reviews', [{"user": "系统", "rating": 0, "content": "该数据不能获得"}]),
                "images": summary.get('all_images', [])
            }
        
        # 比较新旧数据
        changes = scraper.compare_data(current_data, new_data)
        
        # 只有在有变化时才更新数据库
        if scraper.has_changes(changes):
            logger.info(f"检测到数据变化，更新场馆 {court.name} 的详情数据")
            
            # 更新变化的字段
            if changes['description']:
                detail.merged_description = new_data["description"]
            if changes['facilities']:
                detail.merged_facilities = new_data["facilities"]
            if changes['business_hours']:
                detail.merged_business_hours = new_data["business_hours"]
            if changes['rating']:
                detail.merged_rating = new_data["rating"]
            if changes['prices']:
                detail.merged_prices = json.dumps(new_data["prices"], ensure_ascii=False)
            if changes['reviews']:
                detail.dianping_reviews = json.dumps(new_data["reviews"], ensure_ascii=False)
            if changes['images']:
                detail.dianping_images = json.dumps(new_data["images"], ensure_ascii=False)
            
            # 设置缓存过期时间
            detail.last_dianping_update = datetime.now()
            detail.cache_expires_at = datetime.now() + timedelta(hours=24)
            
            db.commit()
            logger.info(f"场馆 {court.name} 详情数据更新完成")
        else:
            logger.info(f"场馆 {court.name} 数据无变化，跳过更新")
            # 只更新时间戳，不更新数据
            detail.last_dianping_update = datetime.now()
            detail.cache_expires_at = datetime.now() + timedelta(hours=24)
            db.commit()
        
        return changes
        
    except Exception as e:
        logger.error(f"更新场馆详情数据失败: {e}")
        raise

async def update_court_detail_data(court: TennisCourt, detail: CourtDetail, db: Session):
    """更新场馆详情数据（兼容旧版本）"""
    current_data = {
        'description': detail.merged_description,
        'facilities': detail.merged_facilities,
        'business_hours': detail.merged_business_hours,
        'prices': json.loads(detail.merged_prices) if detail.merged_prices else [],
        'rating': detail.merged_rating or 0,
        'reviews': json.loads(detail.dianping_reviews) if detail.dianping_reviews else [],
        'images': json.loads(detail.dianping_images) if detail.dianping_images else []
    }
    
    return await update_court_detail_data_with_cache(court, detail, current_data, db)

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

@router.get("/preview/{court_id}")
async def preview_court_details(court_id: int, db: Session = Depends(get_db)):
    """预览场馆详情（不保存到数据库）"""
    try:
        # 获取场馆基本信息
        court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
        if not court:
            raise HTTPException(status_code=404, detail="场馆不存在")
        
        # 获取所有场馆数据用于价格预测
        all_courts = db.query(TennisCourt).all()
        all_venues = []
        for c in all_courts:
            if c.details:
                all_venues.append({
                    'venue_name': c.name,
                    'prices': json.loads(c.details.prices) if c.details.prices else []
                })
        
        # 爬取详情
        scraper = DetailScraper()
        result = scraper.scrape_court_details(court.name, all_venues)
        
        if not result:
            raise HTTPException(status_code=500, detail="爬取失败")
        
        # 获取价格预测
        predicted_prices = price_predictor.predict_price_range(
            court.name, 
            result.get('description', ''), 
            all_venues
        )
        
        # 格式化价格标签
        actual_prices = result.get('prices', [])
        formatted_prices = price_predictor.format_price_labels(actual_prices, predicted_prices)
        
        # 构建响应
        response = {
            "court_id": court_id,
            "venue_name": court.name,
            "rating": result.get('rating'),
            "review_count": result.get('review_count'),
            "facilities": result.get('facilities'),
            "business_hours": result.get('business_hours'),
            "description": result.get('description'),
            "prices": formatted_prices,
            "images": result.get('images', []),
            "court_type": predicted_prices.court_type.value,
            "prediction_info": {
                "predicted_min": predicted_prices.predicted_min,
                "predicted_max": predicted_prices.predicted_max,
                "predicted_mid": predicted_prices.predicted_mid,
                "confidence": predicted_prices.confidence,
                "nearby_prices_count": len(predicted_prices.nearby_prices)
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"预览详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")

@router.post("/update/{court_id}")
async def update_court_details(court_id: int, db: Session = Depends(get_db)):
    """更新场馆详情到数据库"""
    try:
        # 获取场馆基本信息
        court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
        if not court:
            raise HTTPException(status_code=404, detail="场馆不存在")
        
        # 获取所有场馆数据用于价格预测
        all_courts = db.query(TennisCourt).all()
        all_venues = []
        for c in all_courts:
            if c.details:
                all_venues.append({
                    'venue_name': c.name,
                    'prices': json.loads(c.details.prices) if c.details.prices else []
                })
        
        # 爬取详情
        scraper = DetailScraper()
        result = scraper.scrape_court_details(court.name, all_venues)
        
        if not result:
            raise HTTPException(status_code=500, detail="爬取失败")
        
        # 获取价格预测
        predicted_prices = price_predictor.predict_price_range(
            court.name, 
            result.get('description', ''), 
            all_venues
        )
        
        # 检查缓存
        existing_detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
        
        if existing_detail:
            # 检查缓存是否有效
            if scraper.is_cache_valid({
                'venue_name': court.name,
                'rating': existing_detail.rating,
                'review_count': existing_detail.review_count,
                'facilities': existing_detail.facilities,
                'prices': existing_detail.prices
            }, court.name):
                return {"message": "数据已是最新，无需更新", "court_id": court_id}
        
        # 准备数据
        detail_data = {
            "court_id": court_id,
            "rating": result.get('rating'),
            "review_count": result.get('review_count'),
            "facilities": result.get('facilities'),
            "business_hours": result.get('business_hours'),
            "description": result.get('description'),
            "images": json.dumps(result.get('images', []), ensure_ascii=False),
            "court_type": predicted_prices.court_type.value,
            "predicted_prices": json.dumps({
                "predicted_min": predicted_prices.predicted_min,
                "predicted_max": predicted_prices.predicted_max,
                "predicted_mid": predicted_prices.predicted_mid,
                "confidence": predicted_prices.confidence
            }, ensure_ascii=False)
        }
        
        # 详情页不返回价格字段
        if "prices" in detail_data:
            detail_data.pop("prices")
        # 评论和评分如无真实数据则留空
        if not detail_data.get("description") or detail_data.get("description") == "未抓取到有效信息":
            detail_data["description"] = ""
        if not detail_data.get("rating") or detail_data.get("rating") == "-1":
            detail_data["rating"] = ""
        
        # 更新或创建详情
        if existing_detail:
            for key, value in detail_data.items():
                if key != "court_id":
                    setattr(existing_detail, key, value)
        else:
            new_detail = CourtDetail(**detail_data)
            db.add(new_detail)
        
        db.commit()
        
        return {"message": "详情更新成功", "court_id": court_id}
        
    except Exception as e:
        logger.error(f"更新详情失败: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@router.get("/{court_id}")
async def get_court_details(court_id: int, db: Session = Depends(get_db)):
    """获取场馆完整详情"""
    try:
        # 获取场馆基本信息
        court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
        if not court:
            raise HTTPException(status_code=404, detail="场馆不存在")
        
        # 获取详情
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="详情不存在")
        
        # 解析JSON字段
        prices = json.loads(detail.prices) if detail.prices else []
        images = json.loads(detail.images) if detail.images else []
        predicted_prices = json.loads(detail.predicted_prices) if detail.predicted_prices else {}
        
        # 格式化价格标签
        if predicted_prices:
            predicted_price_obj = type('PredictedPrice', (), {
                'predicted_min': predicted_prices.get('predicted_min', 0),
                'predicted_max': predicted_prices.get('predicted_max', 0),
                'predicted_mid': predicted_prices.get('predicted_mid', 0),
                'confidence': predicted_prices.get('confidence', 0),
                'court_type': type('CourtType', (), {'value': detail.court_type or '气膜'})()
            })()
            
            formatted_prices = price_predictor.format_price_labels(prices, predicted_price_obj)
        else:
            formatted_prices = prices
        
        # 构建响应
        response = {
            "court_id": court_id,
            "venue_name": court.name,
            "address": court.address,
            "rating": detail.rating,
            "review_count": detail.review_count,
            "facilities": detail.facilities,
            "business_hours": detail.business_hours,
            "description": detail.description,
            "prices": formatted_prices,
            "images": images,
            "court_type": detail.court_type,
            "prediction_info": predicted_prices,
            "updated_at": detail.updated_at.isoformat() if detail.updated_at else None
        }
        
        return response
        
    except Exception as e:
        logger.error(f"获取详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}") 