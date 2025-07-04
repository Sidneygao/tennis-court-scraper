from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import TennisCourt, CourtDetail, CourtDetailResponse, CourtDetailCreate
from ..scrapers.detail_scraper import DetailScraper
from ..scrapers.price_predictor import PricePredictor
from ..scrapers.map_generator import MapGenerator
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
        
        def standardize_price_type(price):
            """标准化价格type字段"""
            t = price.get('type', '')
            if not t:
                t = ''
            t = t.lower()
            if '黄金' in t or '高峰' in t or 'peak' in t:
                price['type'] = '黄金时段'
            elif '非黄金' in t or 'off' in t:
                price['type'] = '非黄金'
            elif '会员' in t or 'member' in t:
                price['type'] = '会员价'
            else:
                price['type'] = '综合价格'
            return price
        
        # 统一所有价格对象的type字段
        def standardize_prices(prices):
            if not prices:
                return []
            result = []
            for p in prices:
                if isinstance(p, dict):
                    result.append(standardize_price_type(p))
            return result
        
        # 处理predict_prices为数组并补全type
        def standardize_predict_prices(pred):
            if not pred:
                return []
            result = []
            if isinstance(pred, list):
                for p in pred:
                    if isinstance(p, dict):
                        t = p.get('type', '')
                        if not t and p.get('label'):
                            t = p['label']
                        p['type'] = t or '综合价格'
                        result.append(standardize_price_type(p))
            elif isinstance(pred, dict):
                # 兼容旧结构
                if 'peak_price' in pred:
                    result.append({'type': '黄金时段', 'price': pred['peak_price'], 'source': pred.get('source', '预测'), 'predict_method': pred.get('predict_method', '')})
                if 'off_peak_price' in pred:
                    result.append({'type': '非黄金', 'price': pred['off_peak_price'], 'source': pred.get('source', '预测'), 'predict_method': pred.get('predict_method', '')})
            return result
        
        try:
            result = {
                "id": detail.id,
                "court_id": detail.court_id,
                "court_name": court.name,
                "address": court.address,
                "merged_description": detail.merged_description,
                "merged_facilities": detail.merged_facilities,
                "merged_traffic_info": detail.merged_traffic_info,
                "merged_business_hours": detail.merged_business_hours,
                "manual_prices": safe_json_loads(detail.manual_prices),
                "manual_remark": detail.manual_remark,
                "prices": standardize_prices(safe_json_loads(detail.prices)),
                "dianping_prices": standardize_prices(safe_json_loads(detail.dianping_prices)),
                "meituan_prices": standardize_prices(safe_json_loads(detail.meituan_prices)),
                "merged_prices": standardize_prices(safe_json_loads(detail.manual_prices)) if detail.manual_prices else standardize_prices(safe_json_loads(detail.merged_prices)),
                "predict_prices": standardize_predict_prices(safe_json_loads(detail.predict_prices)),
                "dianping_rating": detail.dianping_rating,
                "meituan_rating": detail.meituan_rating,
                "merged_rating": detail.merged_rating,
                "dianping_reviews": safe_json_loads(detail.dianping_reviews),
                "meituan_reviews": safe_json_loads(detail.meituan_reviews),
                "dianping_images": safe_json_loads(detail.dianping_images),
                "meituan_images": safe_json_loads(detail.meituan_images),
                "map_image": detail.map_image,  # 地图图片字段
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
    
    # 新增：只要有价格就返回has_detail: True
    def safe_json_loads(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return []
    merged_prices = safe_json_loads(detail.merged_prices) if detail else []
    predict_prices = safe_json_loads(detail.predict_prices) if detail else []
    has_price = (merged_prices and len(merged_prices) > 0) or (predict_prices and isinstance(predict_prices, dict) and (predict_prices.get('peak_price') or predict_prices.get('off_peak_price')))
    if not detail or (not detail.merged_description and not has_price):
        return {
            "court_id": court_id,
            "court_name": court.name,
            "has_detail": False,
            "message": "暂无详情数据，请点击更新按钮获取"
        }
    
    return {
        "court_id": court_id,
        "court_name": court.name,
        "has_detail": True,
        "detail": {
            "description": detail.merged_description,
            "facilities": detail.merged_facilities,
            "business_hours": detail.merged_business_hours,
            "rating": detail.merged_rating,
            "prices": safe_json_loads(detail.prices),
            "bing_prices": safe_json_loads(detail.bing_prices),
            "merged_prices": safe_json_loads(detail.merged_prices),
            "predict_prices": safe_json_loads(detail.predict_prices),
            "manual_prices": safe_json_loads(detail.manual_prices),
            "manual_remark": detail.manual_remark,
            "reviews": safe_json_loads(detail.dianping_reviews)[:3],
            "images": safe_json_loads(detail.dianping_images)[:3],
            "last_update": detail.updated_at.isoformat() if detail.updated_at else None
        }
    }

@router.post("/{court_id}/manual_price")
async def set_manual_price(court_id: int, manual_prices: dict = Body(...), manual_remark: str = Body(None), db: Session = Depends(get_db)):
    """
    人工录入价格和备注
    manual_prices结构示例：{"peak_price":120,"off_peak_price":80,"member_price":60,"standard_price":100,"remark":"人工录入，节假日价格另议"}
    """
    court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
    if not court:
        raise HTTPException(status_code=404, detail="场馆不存在")
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
    if not detail:
        detail = CourtDetail(court_id=court_id)
        db.add(detail)
        db.commit()
        db.refresh(detail)
    # 写入人工价格
    detail.manual_prices = json.dumps(manual_prices, ensure_ascii=False)
    # 同步写入真实价格字段
    real_prices = []
    for k, v in manual_prices.items():
        if k.endswith('price') and v:
            real_prices.append({
                'type': k,
                'price': v,
                'is_predicted': False,
                'source': '人工录入'
            })
    if real_prices:
        detail.prices = json.dumps(real_prices, ensure_ascii=False)
        # 融合价格优先用人工录入
        detail.merged_prices = json.dumps(real_prices, ensure_ascii=False)
    # 写入备注
    if manual_remark is not None:
        detail.manual_remark = manual_remark
    else:
        detail.manual_remark = manual_prices.get("remark") if isinstance(manual_prices, dict) else None
    db.commit()
    db.refresh(detail)
    return {"message": "人工价格和备注已更新", "court_id": court_id}

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
        
        # ====== 彻底清理虚构数据 ======
        # 强制清空所有可能包含虚构数据的字段
        detail.merged_description = ''  # 清空描述
        detail.merged_facilities = ''   # 清空设施
        detail.merged_business_hours = ''  # 清空营业时间
        detail.merged_rating = 0.0      # 清空评分
        detail.dianping_reviews = json.dumps([], ensure_ascii=False)  # 清空评论
        detail.dianping_images = json.dumps([], ensure_ascii=False)   # 清空图片
        
        # 只保留真实爬取的数据（如果有的话）
        xiaohongshu_data = all_data.get('platforms', {}).get('xiaohongshu', {}).get('data', {})
        if xiaohongshu_data:
            # 只有在确认是真实数据时才赋值
            if xiaohongshu_data.get('description') and not any(keyword in xiaohongshu_data.get('description', '') for keyword in ['模板', '示例', '虚构']):
                detail.merged_description = xiaohongshu_data.get('description', '')
            
            if xiaohongshu_data.get('facilities') and not any(keyword in xiaohongshu_data.get('facilities', '') for keyword in ['模板', '示例', '虚构']):
                detail.merged_facilities = xiaohongshu_data.get('facilities', '')
            
            if xiaohongshu_data.get('business_hours') and not any(keyword in xiaohongshu_data.get('business_hours', '') for keyword in ['模板', '示例', '虚构']):
                detail.merged_business_hours = xiaohongshu_data.get('business_hours', '')
            
            if xiaohongshu_data.get('rating') and xiaohongshu_data.get('rating') > 0:
                detail.merged_rating = xiaohongshu_data.get('rating', 0.0)
            
            if xiaohongshu_data.get('reviews') and len(xiaohongshu_data.get('reviews', [])) > 0:
                detail.dianping_reviews = json.dumps(xiaohongshu_data.get('reviews', []), ensure_ascii=False)
            
            if xiaohongshu_data.get('images') and len(xiaohongshu_data.get('images', [])) > 0:
                detail.dianping_images = json.dumps(xiaohongshu_data.get('images', []), ensure_ascii=False)
        
        # ====== 生成智能地图图片 ======
        # 已禁用地图图片自动生成和覆盖，保护本地缓存
        # try:
        #     if court.latitude and court.longitude:
        #         map_generator = MapGenerator()
        #         map_image_path = map_generator.generate_smart_map(
        #             court.name, 
        #             court.latitude, 
        #             court.longitude, 
        #             court.address or ""
        #         )
        #         if map_image_path:
        #             detail.map_image = map_image_path
        #             logger.info(f"场馆 {court.name} 生成地图图片: {map_image_path}")
        #         else:
        #             detail.map_image = None
        #     else:
        #         detail.map_image = None
        # except Exception as e:
        #     logger.error(f"生成地图图片失败: {e}")
        #     detail.map_image = None
        
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