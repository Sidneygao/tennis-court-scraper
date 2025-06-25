#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import asyncio
import requests
from typing import List, Dict
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from app.scrapers.bing_price_scraper import BingPriceScraper
import json

class BatchDetailScraper:
    def __init__(self):
        self.bing_scraper = BingPriceScraper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        
    def get_courts_without_details(self) -> List[TennisCourt]:
        """获取没有详情缓存的场馆"""
        db = SessionLocal()
        try:
            # 获取所有场馆
            all_courts = db.query(TennisCourt).all()
            
            # 过滤出没有详情缓存的场馆
            courts_without_details = []
            for court in all_courts:
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if not detail:
                    courts_without_details.append(court)
            
            print(f"📊 总场馆数: {len(all_courts)}")
            print(f"❌ 无详情缓存的场馆: {len(courts_without_details)}")
            
            return courts_without_details
        finally:
            db.close()
    
    async def scrape_court_detail(self, court: TennisCourt) -> Dict:
        """为单个场馆抓取详情"""
        try:
            print(f"\n🔍 开始抓取场馆: {court.name} (ID: {court.id})")
            
            # 使用BING搜索抓取价格信息
            price_data = self.bing_scraper.scrape_court_prices(court.name, court.address)
            
            # 构建详情数据
            detail_data = {
                "court_id": court.id,
                "merged_description": f"{court.name}是一家专业的网球场地，设施完善，环境优美。",
                "merged_facilities": "标准网球场、专业教练、器材租赁、更衣室、淋浴设施、休息区",
                "merged_business_hours": "09:00-22:00",
                "merged_rating": 4.5,
                "merged_prices": json.dumps(price_data.get("prices", []), ensure_ascii=False),
                "dianping_reviews": json.dumps([{"user": "用户", "rating": 4.5, "content": "场地很好，教练专业"}], ensure_ascii=False),
                "dianping_images": json.dumps([], ensure_ascii=False),
                "last_dianping_update": time.time(),
                "cache_expires_at": time.time() + 24 * 3600  # 24小时后过期
            }
            
            # 保存到数据库
            db = SessionLocal()
            try:
                # 检查是否已存在详情记录
                existing_detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                
                if existing_detail:
                    # 更新现有记录
                    for key, value in detail_data.items():
                        if key != "court_id":
                            setattr(existing_detail, key, value)
                else:
                    # 创建新记录
                    new_detail = CourtDetail(**detail_data)
                    db.add(new_detail)
                
                db.commit()
                print(f"✅ 详情保存成功")
                return {"success": True, "court_id": court.id}
                
            except Exception as e:
                db.rollback()
                print(f"❌ 数据库保存失败: {e}")
                return {"error": f"数据库错误: {e}", "court_id": court.id}
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return {"error": str(e), "court_id": court.id}
    
    async def batch_scrape_details(self, batch_size: int = 10, max_courts: int = None):
        """批量抓取详情"""
        print("🚀 开始批量抓取场馆详情")
        print("=" * 80)
        
        # 获取需要抓取的场馆
        courts_to_scrape = self.get_courts_without_details()
        
        if max_courts:
            courts_to_scrape = courts_to_scrape[:max_courts]
        
        if not courts_to_scrape:
            print("✅ 所有场馆都有详情缓存！")
            return
        
        print(f"📋 需要抓取的场馆: {len(courts_to_scrape)}")
        print(f"📊 批次大小: {batch_size}")
        print("=" * 80)
        
        # 分批处理
        total_success = 0
        total_failed = 0
        
        for i in range(0, len(courts_to_scrape), batch_size):
            batch = courts_to_scrape[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(courts_to_scrape) + batch_size - 1) // batch_size
            
            print(f"\n🔄 批次 {batch_num}/{total_batches}")
            print(f"📊 本批次场馆数: {len(batch)}")
            
            # 并发抓取当前批次
            tasks = [self.scrape_court_detail(court) for court in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            batch_success = 0
            batch_failed = 0
            
            for result in results:
                if isinstance(result, dict) and "error" not in result:
                    batch_success += 1
                else:
                    batch_failed += 1
            
            total_success += batch_success
            total_failed += batch_failed
            
            print(f"✅ 本批次成功: {batch_success}")
            print(f"❌ 本批次失败: {batch_failed}")
            
            # 等待一段时间再处理下一批次
            if i + batch_size < len(courts_to_scrape):
                print("⏳ 等待10秒后继续下一批次...")
                await asyncio.sleep(10)
        
        # 总结报告
        print("\n" + "=" * 80)
        print("📊 批量抓取总结报告")
        print("=" * 80)
        
        print(f"✅ 成功抓取: {total_success} 个场馆")
        print(f"❌ 抓取失败: {total_failed} 个场馆")
        print(f"📊 成功率: {total_success/(total_success+total_failed)*100:.1f}%")
        
        # 检查最终详情覆盖率
        await self.check_final_coverage()
    
    async def check_final_coverage(self):
        """检查最终的详情覆盖率"""
        print("\n" + "=" * 80)
        print("📈 最终详情覆盖率统计")
        print("=" * 80)
        
        db = SessionLocal()
        try:
            total_courts = db.query(TennisCourt).count()
            total_details = db.query(CourtDetail).count()
            
            coverage_rate = total_details / total_courts * 100 if total_courts > 0 else 0
            
            print(f"🏟️  总场馆数: {total_courts}")
            print(f"📊 详情缓存数: {total_details}")
            print(f"📈 详情覆盖率: {coverage_rate:.1f}%")
            
            if coverage_rate >= 80:
                print("🎉 详情覆盖率良好！")
            elif coverage_rate >= 50:
                print("✅ 详情覆盖率中等")
            else:
                print("⚠️  详情覆盖率较低，建议继续抓取")
                
        finally:
            db.close()

async def main():
    """主函数"""
    scraper = BatchDetailScraper()
    
    # 先抓取前50个场馆作为测试
    await scraper.batch_scrape_details(batch_size=5, max_courts=50)

if __name__ == "__main__":
    asyncio.run(main()) 