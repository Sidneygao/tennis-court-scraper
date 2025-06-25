#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量价格爬取脚本
使用Bing搜索对所有场馆进行价格信息爬取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from app.scrapers.bing_price_scraper import BingPriceScraper
from app.scrapers.price_predictor import PricePredictor
import json
import time
import logging
from typing import Dict, List

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
    def __init__(self):
        self.db = SessionLocal()
        self.bing_scraper = BingPriceScraper()
        self.price_predictor = PricePredictor()
        
    def get_all_courts(self) -> List[TennisCourt]:
        """获取所有场馆"""
        return self.db.query(TennisCourt).all()
    
    def update_court_prices(self, court: TennisCourt, price_data: Dict) -> Dict:
        """更新场馆价格信息"""
        try:
            # 获取或创建详情记录
            detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                detail = CourtDetail(court_id=court.id)
                self.db.add(detail)
            
            # 处理价格数据
            prices = []
            
            # 如果有真实价格数据
            if price_data.get("peak_price") or price_data.get("off_peak_price"):
                price_info = {
                    "type": "真实价格",
                    "source": "bing_search",
                    "peak_price": price_data.get("peak_price"),
                    "off_peak_price": price_data.get("off_peak_price"),
                    "weekend_price": price_data.get("weekend_price"),
                    "notes": price_data.get("price_notes", []),
                    "phone": price_data.get("phone"),
                    "address": price_data.get("address")
                }
                prices.append(price_info)
                
                # 更新场馆基本信息
                if price_data.get("phone") and not court.phone:
                    court.phone = price_data["phone"]
                if price_data.get("address") and not court.address:
                    court.address = price_data["address"]
            
            # 如果没有真实价格，使用预测价格
            if not prices:
                court_type = court.court_type or "气膜"
                predicted_prices = self.price_predictor.predict_prices(court.name, court.address, court_type)
                
                price_info = {
                    "type": "预测价格",
                    "source": "price_predictor",
                    "peak_price": predicted_prices.get("peak_price"),
                    "off_peak_price": predicted_prices.get("off_peak_price"),
                    "weekend_price": predicted_prices.get("weekend_price"),
                    "notes": ["基于2公里范围内同类型场馆价格预测"],
                    "confidence": predicted_prices.get("confidence", 0.7)
                }
                prices.append(price_info)
            
            # 更新详情记录
            detail.merged_prices = json.dumps(prices, ensure_ascii=False)
            
            # 如果有真实价格，更新场馆表的价格字段
            if price_data.get("peak_price"):
                court.peak_price = price_data["peak_price"]
            if price_data.get("off_peak_price"):
                court.off_peak_price = price_data["off_peak_price"]
            
            self.db.commit()
            
            return {
                "court_id": court.id,
                "court_name": court.name,
                "has_real_price": bool(price_data.get("peak_price")),
                "peak_price": price_data.get("peak_price"),
                "off_peak_price": price_data.get("off_peak_price"),
                "phone": price_data.get("phone"),
                "address": price_data.get("address")
            }
            
        except Exception as e:
            logger.error(f"更新场馆 {court.name} 价格失败: {e}")
            self.db.rollback()
            return {
                "court_id": court.id,
                "court_name": court.name,
                "error": str(e)
            }
    
    def fetch_all_prices(self) -> Dict:
        """爬取所有场馆的价格信息"""
        courts = self.get_all_courts()
        results = {
            "total_courts": len(courts),
            "success_count": 0,
            "error_count": 0,
            "real_price_count": 0,
            "predicted_price_count": 0,
            "results": []
        }
        
        logger.info(f"开始爬取 {len(courts)} 个场馆的价格信息")
        
        for i, court in enumerate(courts, 1):
            try:
                logger.info(f"处理 {i}/{len(courts)}: {court.name}")
                
                # 爬取价格信息
                price_data = self.bing_scraper.scrape_court_prices(court.name, court.address)
                
                # 更新数据库
                result = self.update_court_prices(court, price_data)
                results["results"].append(result)
                
                if "error" not in result:
                    results["success_count"] += 1
                    if result.get("has_real_price"):
                        results["real_price_count"] += 1
                        logger.info(f"✅ {court.name}: 找到真实价格 {price_data.get('peak_price')}元")
                    else:
                        results["predicted_price_count"] += 1
                        logger.info(f"📊 {court.name}: 使用预测价格")
                else:
                    results["error_count"] += 1
                    logger.error(f"❌ {court.name}: {result['error']}")
                
                # 避免请求过快
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"处理场馆 {court.name} 失败: {e}")
                results["error_count"] += 1
                results["results"].append({
                    "court_id": court.id,
                    "court_name": court.name,
                    "error": str(e)
                })
        
        logger.info(f"价格爬取完成: 成功 {results['success_count']}, 错误 {results['error_count']}")
        logger.info(f"真实价格: {results['real_price_count']}, 预测价格: {results['predicted_price_count']}")
        
        return results
    
    def close(self):
        """关闭资源"""
        if self.bing_scraper:
            self.bing_scraper.close()
        if self.db:
            self.db.close()

def main():
    """主函数"""
    fetcher = BatchPriceFetcher()
    
    try:
        # 爬取所有价格
        results = fetcher.fetch_all_prices()
        
        # 保存结果到文件
        with open('batch_price_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 打印统计信息
        print("\n" + "="*50)
        print("🎾 批量价格爬取完成")
        print("="*50)
        print(f"总场馆数: {results['total_courts']}")
        print(f"成功处理: {results['success_count']}")
        print(f"处理失败: {results['error_count']}")
        print(f"真实价格: {results['real_price_count']}")
        print(f"预测价格: {results['predicted_price_count']}")
        print("="*50)
        
        # 显示有真实价格的场馆
        real_price_courts = [r for r in results["results"] if r.get("has_real_price")]
        if real_price_courts:
            print("\n🏆 找到真实价格的场馆:")
            for court in real_price_courts:
                print(f"  • {court['court_name']}: {court['peak_price']}元")
        
        # 显示处理失败的场馆
        error_courts = [r for r in results["results"] if "error" in r]
        if error_courts:
            print("\n❌ 处理失败的场馆:")
            for court in error_courts:
                print(f"  • {court['court_name']}: {court['error']}")
        
    except Exception as e:
        logger.error(f"批量价格爬取失败: {e}")
        print(f"❌ 批量价格爬取失败: {e}")
    
    finally:
        fetcher.close()

if __name__ == "__main__":
    main() 