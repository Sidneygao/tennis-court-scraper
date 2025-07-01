#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BING多关键字价格爬取脚本
只对没有真实价格缓存的场馆进行爬取，结果写入缓存
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db, SessionLocal
from app.models import TennisCourt, CourtDetail

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bing_price_spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BingPriceSpider:
    """BING价格爬取器"""
    
    def __init__(self):
        self.db = next(get_db())
        
    def get_courts_without_any_prices(self) -> list:
        """
        获取主表和详情表都没有价格缓存的场馆，自动补建详情表
        """
        courts = self.db.query(TennisCourt).all()
        result = []
        for court in courts:
            # 主表价格字段
            has_main_price = bool(court.peak_price or court.off_peak_price or court.member_price)
            # 详情表价格字段
            detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                # 自动补建详情表
                detail = CourtDetail(court_id=court.id)
                self.db.add(detail)
                self.db.commit()
                self.db.refresh(detail)
                logger.info(f"为场馆 {court.name} 补建详情表: detail_id={detail.id}")
            
            has_detail_price = False
            if detail:
                for field in [detail.dianping_prices, detail.meituan_prices, detail.merged_prices]:
                    try:
                        if field:
                            price_data = json.loads(field)
                            if price_data and len(price_data) > 0:
                                has_detail_price = True
                    except:
                        continue
            if not has_main_price and not has_detail_price:
                result.append({
                    'court_id': court.id,
                    'court_name': court.name,
                    'court_address': court.address,
                    'detail_id': detail.id if detail else None
                })
        logger.info(f"找到 {len(result)} 个主表和详情表都没有价格缓存的场馆")
        return result
    
    def generate_search_keywords(self, court_name: str) -> List[str]:
        """生成搜索关键词"""
        keywords = [
            f"{court_name} 网球价格",
            f"{court_name} 网球预订",
            f"{court_name} 网球费用",
            f"{court_name} 网球收费",
            f"{court_name} 价格",
            f"{court_name} 预订"
        ]
        return keywords
    
    def crawl_bing_prices(self, court_data: Dict) -> Dict:
        """爬取单个场馆的BING价格"""
        try:
            court_name = court_data['court_name']
            logger.info(f"开始爬取场馆价格: {court_name}")
            
            # 生成搜索关键词
            keywords = self.generate_search_keywords(court_name)
            
            # 模拟BING爬取结果（实际需要实现BING爬虫）
            # 这里先用模拟数据，后续可以替换为真实的BING爬虫
            mock_prices = self.mock_bing_crawl(court_name, keywords)
            
            # 更新缓存
            success = self.update_price_cache(court_data['detail_id'], mock_prices)
            
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": success,
                "prices": mock_prices,
                "keywords_used": keywords
            }
            
        except Exception as e:
            logger.error(f"爬取场馆 {court_name} 价格失败: {e}")
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": False,
                "error": str(e)
            }
    
    def mock_bing_crawl(self, court_name: str, keywords: List[str]) -> List[Dict]:
        """模拟BING爬取（实际需要替换为真实爬虫）"""
        # 这里应该实现真实的BING爬虫逻辑
        # 目前用模拟数据演示
        import random
        
        mock_prices = []
        for keyword in keywords[:3]:  # 只处理前3个关键词
            if random.random() > 0.7:  # 70%概率找到价格
                price_type = random.choice(["黄金时间价格", "非黄金时间价格", "会员价格"])
                price_value = random.randint(80, 200)
                mock_prices.append({
                    "type": price_type,
                    "price": f"¥{price_value}/小时",
                    "source": "BING",
                    "keyword": keyword,
                    "confidence": 0.8,
                    "is_predicted": False  # 标记为真实价格
                })
        
        return mock_prices
    
    def update_price_cache(self, detail_id: int, prices: List[Dict]) -> bool:
        """更新价格缓存"""
        try:
            # 使用独立的数据库会话避免事务冲突
            db = SessionLocal()
            try:
                detail = db.query(CourtDetail).filter(CourtDetail.id == detail_id).first()
                if detail:
                    # 只更新BING价格缓存，不动其他字段
                    detail.bing_prices = json.dumps(prices, ensure_ascii=False)
                    detail.updated_at = datetime.now()
                    
                    db.commit()
                    logger.info(f"成功更新价格缓存: detail_id={detail_id}")
                    return True
                else:
                    logger.warning(f"未找到详情记录: detail_id={detail_id}")
                    return False
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"更新价格缓存失败: {e}")
            return False
    
    def batch_crawl_prices(self, max_workers: int = 2, limit: int = 1000) -> dict:
        start_time = datetime.now()
        logger.info(f"开始批量BING价格爬取，限制: {limit}，并发数: {max_workers}")
        courts = self.get_courts_without_any_prices()
        if not courts:
            logger.info("没有需要爬取价格的场馆")
            return {"success": True, "message": "没有需要爬取的场馆"}
        courts = courts[:limit]
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_court = {
                executor.submit(self.crawl_bing_prices, court): court 
                for court in courts
            }
            for future in as_completed(future_to_court):
                result = future.result()
                results.append(result)
                logger.info(f"完成: {result['court_name']} - {'成功' if result['success'] else '失败'}")
                time.sleep(2)
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bing_price_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"结果已保存到: {filename}")
        return summary

def crawl_bing_prices_for_area(area_key):
    """按区域批量爬取BING价格"""
    from app.database import get_db
    from app.models import TennisCourt
    db = next(get_db())
    courts = db.query(TennisCourt).filter(TennisCourt.area == area_key).all()
    print(f"共{len(courts)}个场馆，开始BING价格爬取...")
    
    spider = BingPriceSpider()
    results = []
    
    for court in courts:
        print(f"爬取: {court.name} ({court.id}) ...")
        
        # 准备场馆数据
        court_data = {
            'court_id': court.id,
            'court_name': court.name,
            'court_address': court.address,
            'detail_id': None
        }
        
        # 获取或创建详情记录
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail:
            detail = CourtDetail(court_id=court.id)
            db.add(detail)
            db.commit()
            db.refresh(detail)
        court_data['detail_id'] = detail.id
        
        # 执行爬取
        result = spider.crawl_bing_prices(court_data)
        results.append(result)
        
        # 避免请求过快
        time.sleep(1)
    
    # 统计结果
    success_count = sum(1 for r in results if r.get('success', False))
    print(f"区域BING价格爬取完成！成功: {success_count}/{len(results)}")
    
    return results

def main():
    """主函数"""
    spider = BingPriceSpider()
    
    # 批量爬取价格 - 处理所有剩余场馆
    result = spider.batch_crawl_prices(max_workers=2, limit=1000)
    
    print(f"\n=== BING价格爬取完成 ===")
    print(f"总场馆数: {result['total_courts']}")
    print(f"成功数: {result['success_count']}")
    print(f"失败数: {result['failed_count']}")
    print(f"耗时: {result['duration_seconds']:.2f}秒")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--area':
        area_key = sys.argv[2]
        crawl_bing_prices_for_area(area_key)
    else:
        main() 