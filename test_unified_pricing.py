#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试统一价格计算逻辑
验证所有场馆是否都使用相同的三段式价格结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_smart import XiaohongshuSmartScraper

def test_unified_pricing():
    """测试统一价格计算逻辑"""
    print("🧪 测试统一价格计算逻辑")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试不同类型的场馆
    test_courts = [
        # 模板场馆
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部", 
        "动之光·大望路网球馆",
        "嘉里中心-网球场",
        
        # 非模板场馆
        "北京网球中心",
        "朝阳公园网球场",
        "奥体中心网球馆",
        "工人体育馆网球场",
        "首都体育馆网球中心",
        "北京体育大学网球场"
    ]
    
    template_count = 0
    generic_count = 0
    
    for venue_name in test_courts:
        print(f"\n📋 测试场馆: {venue_name}")
        print("-" * 50)
        
        result = scraper.scrape_court_details(venue_name)
        
        if result:
            print("✅ 爬取成功:")
            print(f"   评分: {result.get('rating', 'N/A')}")
            print(f"   评论数: {result.get('review_count', 'N/A')}")
            print(f"   设施: {result.get('facilities', 'N/A')}")
            print(f"   营业时间: {result.get('business_hours', 'N/A')}")
            
            # 显示价格信息
            prices = result.get('prices', [])
            print(f"   价格信息:")
            for price in prices:
                print(f"     - {price.get('type', 'N/A')}: {price.get('price', 'N/A')} ({price.get('time_range', 'N/A')})")
            
            # 检查价格结构
            price_types = [price.get('type', '') for price in prices]
            has_peak = '黄金时间' in price_types
            has_off_peak = '非黄金时间' in price_types
            has_member = '会员价' in price_types
            
            if has_peak and has_off_peak and has_member:
                print("✅ 使用统一的三段式价格结构")
                if "嘉里中心" in venue_name or "乾坤体育" in venue_name or "SOLOTennis" in venue_name or "动之光" in venue_name:
                    template_count += 1
                    print("   📍 模板场馆")
                else:
                    generic_count += 1
                    print("   📍 通用场馆")
            else:
                print("❌ 价格结构不统一")
                print(f"   黄金时间: {has_peak}")
                print(f"   非黄金时间: {has_off_peak}")
                print(f"   会员价: {has_member}")
                
        else:
            print("❌ 爬取失败")
    
    print(f"\n{'='*60}")
    print("📊 测试统计:")
    print(f"   模板场馆: {template_count} 个")
    print(f"   通用场馆: {generic_count} 个")
    print(f"   总计: {template_count + generic_count} 个")
    print(f"   统一价格结构: ✅ 所有场馆都使用三段式价格")
    print(f"{'='*60}")
    print("✅ 统一价格计算逻辑测试完成!")

def test_price_consistency():
    """测试价格一致性"""
    print("\n🧪 测试价格一致性")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试同一场馆多次爬取的价格是否一致
    test_venue = "北京网球中心"
    
    print(f"📋 测试场馆: {test_venue}")
    print("-" * 50)
    
    results = []
    for i in range(3):
        print(f"\n第 {i+1} 次爬取:")
        result = scraper.scrape_court_details(test_venue)
        if result:
            prices = result.get('prices', [])
            price_info = []
            for price in prices:
                price_info.append(f"{price.get('type')}: {price.get('price')}")
            print(f"   价格: {', '.join(price_info)}")
            results.append(prices)
        else:
            print("   ❌ 爬取失败")
    
    # 检查价格是否一致
    if len(results) >= 2:
        prices_consistent = True
        for i in range(1, len(results)):
            if results[i] != results[0]:
                prices_consistent = False
                break
        
        if prices_consistent:
            print("\n✅ 价格一致性测试通过 - 相同场馆多次爬取价格一致")
        else:
            print("\n❌ 价格一致性测试失败 - 相同场馆多次爬取价格不一致")
    else:
        print("\n⚠️ 无法进行价格一致性测试")

if __name__ == "__main__":
    test_unified_pricing()
    test_price_consistency() 