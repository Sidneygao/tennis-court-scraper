#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的朝阳区场馆价格模板
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_smart import XiaohongshuSmartScraper
import json

def test_new_price_templates():
    """测试新增的价格模板"""
    print("🎾 测试新增朝阳区场馆价格模板")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试场馆列表
    test_venues = [
        "朝阳公园网球场",
        "国家网球中心",
        "北工大奥林匹克体育馆网球场",
        "朝阳体育中心网球场",
        "798艺术区网球场",
        "蓝色港湾网球场",
        "东枫国际体育园网球场"
    ]
    
    results = {}
    
    for venue_name in test_venues:
        print(f"\n🔍 测试场馆: {venue_name}")
        
        # 获取场馆详情
        details = scraper.scrape_court_details(venue_name)
        
        if details:
            print(f"✅ 成功获取详情")
            print(f"   评分: {details.get('rating', 'N/A')}")
            print(f"   位置: {details.get('location', 'N/A')}")
            print(f"   营业时间: {details.get('business_hours', 'N/A')}")
            
            # 显示价格信息
            prices = details.get('prices', [])
            if prices:
                print(f"   价格信息:")
                for price in prices:
                    print(f"     - {price.get('type', 'N/A')}: {price.get('price', 'N/A')} ({price.get('time_range', 'N/A')})")
            
            results[venue_name] = {
                "success": True,
                "rating": details.get('rating'),
                "prices": prices,
                "location": details.get('location')
            }
        else:
            print(f"❌ 获取详情失败")
            results[venue_name] = {
                "success": False
            }
    
    # 保存测试结果
    with open('new_price_templates_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 测试完成")
    print("=" * 60)
    print(f"总测试场馆: {len(test_venues)}")
    print(f"成功数: {sum(1 for r in results.values() if r.get('success', False))}")
    print(f"失败数: {sum(1 for r in results.values() if not r.get('success', False))}")
    print(f"📁 详细结果已保存到 new_price_templates_test_results.json")
    
    return results

if __name__ == "__main__":
    test_new_price_templates() 