#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量价格获取器
从多个来源获取网球场地价格数据
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
from app.scrapers.detail_scraper import DetailScraper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_price_fetch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchPriceFetcher:
    """批量价格获取器"""
    
    def __init__(self):
        self.price_predictor = PricePredictor()
        self.detail_scraper = DetailScraper()
        
    def get_courts_without_prices(self, limit: int = 50) -> List[TennisCourt]:
        """获取没有价格信息的场馆"""
        db = next(get_db())
        try:
            courts = db.query(TennisCourt).filter(
                (TennisCourt.peak_price.is_(None)) | 
                (TennisCourt.peak_price == '') |
                (TennisCourt.price_updated_at.is_(None))
            ).limit(limit).all()
            
            # 转换为字典，避免会话问题
            court_data = []
            for court in courts:
                court_data.append({
                    'id': court.id,
                    'name': court.name,
                    'area': court.area,
                    'court_type': court.court_type,
                    'facilities': court.facilities
                })
            
            logger.info(f"找到 {len(court_data)} 个需要更新价格的场馆")
            return court_data
        finally:
            db.close()
    
    def fetch_court_prices(self, court_data: Dict) -> Dict:
        """获取单个场馆的价格信息"""
        try:
            logger.info(f"开始获取场馆价格: {court_data['name']}")
            
            # 1. 智能价格预测（创建临时对象）
            class TempCourt:
                def __init__(self, data):
                    self.id = data.get('id', 0)
                    self.name = data.get('name', '')
                    self.address = data.get('address', '')
                    self.latitude = data.get('latitude', None)
                    self.longitude = data.get('longitude', None)
                    self.area = data['area']
                    self.court_type = data['court_type']
                    self.facilities = data['facilities']
            
            temp_court = TempCourt(court_data)
            prediction = self.price_predictor.predict_price_for_court(temp_court)
            if prediction is None:
                logger.warning(f"场馆 {court_data['name']} 预测失败，未获得有效预测价格")
                return {
                    "court_id": court_data['id'],
                    "court_name": court_data['name'],
                    "success": False,
                    "error": "预测器未返回有效结果"
                }
            
            # 2. 暂时跳过真实价格获取（避免异步问题）
            real_prices = None
            
            # 3. 融合价格数据
            final_prices = self.merge_prices(prediction, real_prices)
            
            # 4. 更新数据库
            success = self.update_court_prices(court_data['id'], final_prices)
            
            return {
                "court_id": court_data['id'],
                "court_name": court_data['name'],
                "success": success,
                "predicted_prices": prediction,
                "real_prices": real_prices,
                "final_prices": final_prices
            }
            
        except Exception as e:
            logger.error(f"获取场馆 {court_data['name']} 价格失败: {e}")
            return {
                "court_id": court_data['id'],
                "court_name": court_data['name'],
                "success": False,
                "error": str(e)
            }
    
    def merge_prices(self, prediction: Dict, real_prices: Optional[List]) -> List[Dict]:
        """融合预测价格和真实价格"""
        merged_prices = []
        
        # 添加预测价格
        if prediction.get("peak_price"):
            merged_prices.append({
                "type": "黄金时间价格",
                "price": prediction["peak_price"],
                "is_predicted": True,
                "confidence": prediction.get("prediction_confidence", 0.8)
            })
        
        if prediction.get("off_peak_price"):
            merged_prices.append({
                "type": "非黄金时间价格", 
                "price": prediction["off_peak_price"],
                "is_predicted": True,
                "confidence": prediction.get("prediction_confidence", 0.8)
            })
        
        if prediction.get("member_price"):
            merged_prices.append({
                "type": "会员价格",
                "price": prediction["member_price"], 
                "is_predicted": True,
                "confidence": prediction.get("prediction_confidence", 0.8)
            })
        
        # 添加真实价格（如果有）
        if real_prices:
            for price in real_prices:
                if isinstance(price, dict) and price.get("price") != "该数据不能获得":
                    merged_prices.append({
                        "type": price.get("type", "价格信息"),
                        "price": price.get("price", ""),
                        "is_predicted": False,
                        "confidence": 1.0
                    })
        
        return merged_prices
    
    def update_court_prices(self, court_id: int, prices: List[Dict]) -> bool:
        """更新场馆价格到数据库"""
        try:
            # 找到最高置信度的价格
            best_prices = {}
            for price in prices:
                price_type = price.get("type", "")
                confidence = price.get("confidence", 0)
                
                if price_type not in best_prices or confidence > best_prices[price_type]["confidence"]:
                    best_prices[price_type] = price
            
            # 更新主表价格字段
            db = next(get_db())
            court = db.query(TennisCourt).filter(TennisCourt.id == court_id).first()
            if court:
                court.peak_price = best_prices.get("黄金时间价格", {}).get("price", "")
                court.off_peak_price = best_prices.get("非黄金时间价格", {}).get("price", "")
                court.member_price = best_prices.get("会员价格", {}).get("price", "")
                court.price_updated_at = datetime.now()
            
            # 更新详情表
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
            if not detail:
                detail = CourtDetail(court_id=court_id)
                db.add(detail)
            
            detail.merged_prices = json.dumps(prices, ensure_ascii=False)
            detail.updated_at = datetime.now()
            
            db.commit()
            logger.info(f"成功更新场馆价格: {court.name}")
            return True
            
        except Exception as e:
            logger.error(f"更新数据库失败: {e}")
            db.rollback()
            return False
    
    def batch_fetch_prices(self, max_workers: int = 3, limit: int = 50) -> Dict:
        """批量获取价格"""
        start_time = datetime.now()
        logger.info(f"开始批量获取价格，限制: {limit}，并发数: {max_workers}")
        
        # 获取需要更新的场馆
        courts = self.get_courts_without_prices(limit)
        if not courts:
            logger.info("没有需要更新价格的场馆")
            return {"success": True, "message": "没有需要更新的场馆"}
        
        # 并发获取价格
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_court = {
                executor.submit(self.fetch_court_prices, court): court 
                for court in courts
            }
            
            for future in as_completed(future_to_court):
                result = future.result()
                results.append(result)
                logger.info(f"完成: {result['court_name']} - {'成功' if result['success'] else '失败'}")
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - success_count
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "success": True,
            "total_courts": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "duration_seconds": duration,
            "results": results
        }
        
        logger.info(f"批量获取完成: 成功 {success_count}/{len(results)}, 耗时 {duration:.2f}秒")
        
        # 保存结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_price_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"结果已保存到: {filename}")
        return summary

def main():
    """主函数"""
    fetcher = BatchPriceFetcher()
    
    # 批量获取价格 - 处理所有需要更新的场馆
    result = fetcher.batch_fetch_prices(max_workers=3, limit=1000)
    
    print(f"\n=== 批量价格获取完成 ===")
    print(f"总场馆数: {result['total_courts']}")
    print(f"成功数: {result['success_count']}")
    print(f"失败数: {result['failed_count']}")
    print(f"耗时: {result['duration_seconds']:.2f}秒")

if __name__ == "__main__":
    main() 