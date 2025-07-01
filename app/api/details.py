from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import TennisCourt, CourtDetail, CourtDetailResponse, CourtDetailCreate
from ..scrapers.detail_scraper import DetailScraper
from ..scrapers.price_predictor import PricePredictor
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
        
        # 只在明确要求强制更新时才更新数据，否则只返回缓存
        if force_update:
            try:
                await update_court_detail_data(court, detail, db)
            except Exception as e:
                logger.error(f"更新详情数据失败: {e}")
                if not detail.merged_description:
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
                "prices": safe_json_loads(detail.prices),
                "dianping_prices": safe_json_loads(detail.dianping_prices),
                "meituan_prices": safe_json_loads(detail.meituan_prices),
                "merged_prices": safe_json_loads(detail.merged_prices),
                "predict_prices": safe_json_loads(detail.predict_prices),
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
        summary = all_data.get('summary', {})
        
        # 真实渠道价格融合
        real_prices = []
        # 优先点评
        if detail.dianping_prices:
            try:
                prices = json.loads(detail.dianping_prices)
                if prices and isinstance(prices, list) and any(p.get('price') for p in prices):
                    real_prices.extend(prices)
            except:
                pass
        # 其次美团
        if not real_prices and detail.meituan_prices:
            try:
                prices = json.loads(detail.meituan_prices)
                if prices and isinstance(prices, list) and any(p.get('price') for p in prices):
                    real_prices.extend(prices)
            except:
                pass
        
        # 检查现有的merged_prices中的BING价格
        bing_prices = []
        if detail.merged_prices:
            try:
                existing_prices = json.loads(detail.merged_prices)
                if existing_prices and isinstance(existing_prices, list):
                    # 分离BING价格和真实价格
                    for price in existing_prices:
                        if price.get('source') == 'BING':
                            bing_prices.append(price)
                        else:
                            real_prices.append(price)
            except:
                pass
        
        # 更新价格数据 - 只保留真实价格（非BING）
        if real_prices:
            detail.merged_prices = json.dumps(real_prices, ensure_ascii=False)
        else:
            detail.merged_prices = json.dumps([], ensure_ascii=False)
        
        # ====== 处理BING价格作为预测价格 ======
        # 如果没有真实价格但有BING价格，将BING价格转换为预测价格格式
        if not real_prices and bing_prices and not detail.predict_prices:
            try:
                # 从BING价格中提取价格信息
                peak_prices = []
                off_peak_prices = []
                
                for price_data in bing_prices:
                    price = price_data.get('price')
                    if price and isinstance(price, (int, float)):
                        # 根据时间段判断是黄金还是非黄金时段
                        time_info = price_data.get('time_info', '')
                        if any(keyword in time_info for keyword in ['黄金', '高峰', 'peak', '19:00', '20:00', '21:00']):
                            peak_prices.append(price)
                        else:
                            off_peak_prices.append(price)
                
                # 计算平均价格
                if peak_prices or off_peak_prices:
                    predict_result = {
                        'peak_price': int(sum(peak_prices) / len(peak_prices)) if peak_prices else None,
                        'off_peak_price': int(sum(off_peak_prices) / len(off_peak_prices)) if off_peak_prices else None,
                        'confidence': 0.7,  # BING价格的置信度
                        'source': 'BING_SCRAPED',
                        'sample_count': len(bing_prices)
                    }
                    detail.predict_prices = json.dumps(predict_result, ensure_ascii=False)
                    logger.info(f"场馆 {court.name} 将BING价格转换为预测价格: {predict_result}")
            except Exception as e:
                logger.error(f"转换BING价格为预测价格失败: {e}")
        
        # ====== 自动预测价格 ======
        # 如果没有真实价格和BING价格，自动调用预测算法
        if not real_prices and not bing_prices and not detail.predict_prices:
            try:
                predictor = PricePredictor()
                predict_result = predictor.predict_price_for_court(court)
                if predict_result:
                    detail.predict_prices = json.dumps(predict_result, ensure_ascii=False)
                    logger.info(f"场馆 {court.name} 自动生成预测价格: {predict_result}")
            except Exception as e:
                logger.error(f"自动预测价格失败: {e}")
        
        # 其它字段照常更新
        merged_data = {
            "description": f"{court.name}是一家专业的网球场地，设施完善，环境优美。",
            "facilities": "、".join(summary.get('all_facilities', [])),
            "business_hours": "09:00-22:00",
            "prices": real_prices if real_prices else [],
            "rating": summary.get('avg_rating', 0.0),
            "reviews": summary.get('all_reviews', []),
            "images": summary.get('all_images', [])
        }
        detail.merged_description = merged_data["description"]
        detail.merged_facilities = merged_data["facilities"]
        detail.merged_business_hours = merged_data["business_hours"]
        detail.merged_rating = merged_data["rating"]
        detail.dianping_reviews = json.dumps(merged_data["reviews"], ensure_ascii=False)
        detail.dianping_images = json.dumps(merged_data["images"], ensure_ascii=False)
        db.commit()
    except Exception as e:
        print(f"❌ update_court_detail_data异常: {e}")
        db.rollback()
        raise

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