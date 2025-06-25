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
from app.models import TennisCourt
from app.config import settings

class MissingAreasScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_missing_areas(self) -> List[str]:
        """获取缺失的区域列表"""
        db = SessionLocal()
        try:
            # 获取当前已有的区域
            existing_areas = db.query(TennisCourt.area).distinct().all()
            existing_areas = [area[0] for area in existing_areas if area[0]]
            
            # 找出缺失的区域
            missing_areas = [area for area in settings.target_areas if area not in existing_areas]
            
            print(f"📊 当前已有区域: {existing_areas}")
            print(f"❌ 缺失的区域: {missing_areas}")
            
            return missing_areas
        finally:
            db.close()
    
    async def scrape_area(self, area: str) -> Dict:
        """抓取单个区域的数据"""
        try:
            print(f"\n🌍 开始抓取区域: {area}")
            
            # 构建API请求
            url = f"http://localhost:8000/api/scraper/scrape/amap"
            params = {"area": area}
            
            print(f"📡 请求URL: {url}")
            print(f"📋 参数: {params}")
            
            # 发送请求
            response = self.session.post(url, params=params, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 抓取成功: {result.get('message', '')}")
                return result
            else:
                print(f"❌ 抓取失败: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ 抓取异常: {e}")
            return {"error": str(e)}
    
    async def scrape_all_missing_areas(self):
        """抓取所有缺失的区域"""
        print("🚀 开始抓取所有缺失区域")
        print("=" * 80)
        
        # 获取缺失的区域
        missing_areas = self.get_missing_areas()
        
        if not missing_areas:
            print("✅ 所有区域都已抓取完成！")
            return
        
        print(f"📋 需要抓取的区域: {missing_areas}")
        print(f"📊 预计新增场馆数: {len(missing_areas) * 50} (每个区域约50个场馆)")
        print("=" * 80)
        
        # 逐个抓取区域
        results = {}
        for i, area in enumerate(missing_areas, 1):
            print(f"\n🔄 进度: {i}/{len(missing_areas)}")
            
            result = await self.scrape_area(area)
            results[area] = result
            
            # 检查结果
            if "error" not in result:
                print(f"✅ {area} 抓取成功")
            else:
                print(f"❌ {area} 抓取失败: {result['error']}")
            
            # 等待一段时间再抓取下一个区域
            if i < len(missing_areas):
                print("⏳ 等待5秒后继续...")
                await asyncio.sleep(5)
        
        # 总结报告
        print("\n" + "=" * 80)
        print("📊 抓取总结报告")
        print("=" * 80)
        
        success_count = sum(1 for result in results.values() if "error" not in result)
        failed_count = len(results) - success_count
        
        print(f"✅ 成功抓取: {success_count} 个区域")
        print(f"❌ 抓取失败: {failed_count} 个区域")
        
        if failed_count > 0:
            print("\n❌ 失败的区域:")
            for area, result in results.items():
                if "error" in result:
                    print(f"  - {area}: {result['error']}")
        
        # 检查最终场馆数量
        await self.check_final_stats()
    
    async def check_final_stats(self):
        """检查最终的统计数据"""
        print("\n" + "=" * 80)
        print("📈 最终统计")
        print("=" * 80)
        
        db = SessionLocal()
        try:
            total_courts = db.query(TennisCourt).count()
            area_stats = {}
            
            for area in settings.target_areas:
                count = db.query(TennisCourt).filter(TennisCourt.area == area).count()
                area_stats[area] = count
            
            print(f"🏟️  总场馆数: {total_courts}")
            
            if total_courts >= 500:
                print(f"🎉 目标达成！场馆数量: {total_courts}")
            else:
                print(f"⚠️  还需努力，当前场馆数: {total_courts}/500")
            
            print("\n📍 各区域分布:")
            for area, count in area_stats.items():
                print(f"  {area}: {count}个场馆")
                
        finally:
            db.close()

async def main():
    """主函数"""
    scraper = MissingAreasScraper()
    await scraper.scrape_all_missing_areas()

if __name__ == "__main__":
    asyncio.run(main()) 