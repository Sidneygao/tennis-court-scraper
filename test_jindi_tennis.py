#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试金地网球的价格计算逻辑
验证金地网球是否使用统一的三段式价格结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_smart import XiaohongshuSmartScraper

def test_jindi_tennis():
    """测试金地网球的价格计算逻辑"""
    print("🧪 测试金地网球的价格计算逻辑")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试金地网球的不同名称变体
    test_names = [
        "金地网球",
        "金地网球中心",
        "金地网球馆", 
        "金地网球俱乐部",
        "金地网球学练馆",
        "金地网球培训中心"
    ]
    
    for venue_name in test_names:
        print(f"\n📋 测试场馆: {venue_name}")
        print("-" * 50)
        
        result = scraper.scrape_court_details(venue_name)
        
        if result:
            print("✅ 爬取成功:")
            print(f"   评分: {result.get('rating', 'N/A')}")
            print(f"   评论数: {result.get('review_count', 'N/A')}")
            print(f"   设施: {result.get('facilities', 'N/A')}")
            print(f"   营业时间: {result.get('business_hours', 'N/A')}")
            print(f"   描述: {result.get('description', 'N/A')[:50]}...")
            
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
                
                # 检查是否使用了模板
                template_used = False
                for key in scraper.court_templates.keys():
                    if key.lower() in venue_name.lower():
                        template_used = True
                        print(f"   📍 使用模板: {key}")
                        break
                
                if not template_used:
                    print("   📍 使用通用数据生成")
                    
            else:
                print("❌ 价格结构不统一")
                print(f"   黄金时间: {has_peak}")
                print(f"   非黄金时间: {has_off_peak}")
                print(f"   会员价: {has_member}")
                
        else:
            print("❌ 爬取失败")
    
    print(f"\n{'='*60}")
    print("✅ 金地网球价格计算逻辑测试完成!")

def test_jindi_consistency():
    """测试金地网球价格一致性"""
    print("\n🧪 测试金地网球价格一致性")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试同一场馆多次爬取的价格是否一致
    test_venue = "金地网球中心"
    
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

def analyze_jindi_pricing():
    """分析金地网球的价格合理性"""
    print("\n🧪 分析金地网球价格合理性")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    venue_name = "金地网球中心"
    result = scraper.scrape_court_details(venue_name)
    
    if result:
        print(f"📋 场馆: {venue_name}")
        print("-" * 50)
        
        # 获取种子值
        seed = scraper._get_deterministic_seed(venue_name)
        print(f"   种子值: {seed}")
        
        # 计算基础价格
        base_price = 80 + (seed % 100)  # 80-180
        price_variation = int(scraper._deterministic_range(seed, -20, 30, 2))
        
        print(f"   基础价格: {base_price}元/小时")
        print(f"   价格变化: {price_variation}")
        
        # 计算预期价格
        expected_prices = {
            '黄金时间': base_price + price_variation + 30,
            '非黄金时间': base_price + price_variation,
            '会员价': base_price + price_variation - 20
        }
        
        print(f"   预期价格:")
        for price_type, price in expected_prices.items():
            print(f"     - {price_type}: {price}元/小时")
        
        # 显示实际价格
        prices = result.get('prices', [])
        print(f"   实际价格:")
        for price in prices:
            print(f"     - {price.get('type')}: {price.get('price')}")
        
        # 价格合理性分析
        min_price = min(expected_prices.values())
        max_price = max(expected_prices.values())
        
        print(f"\n   价格分析:")
        print(f"     - 价格范围: {min_price}-{max_price}元/小时")
        print(f"     - 价格差异: {max_price - min_price}元/小时")
        
        if min_price < 50:
            print(f"     - ⚠️ 价格偏低，可能不合理")
        elif max_price > 500:
            print(f"     - ⚠️ 价格偏高，可能不合理")
        else:
            print(f"     - ✅ 价格范围合理")
            
    else:
        print("❌ 无法获取金地网球数据")

if __name__ == "__main__":
    test_jindi_tennis()
    test_jindi_consistency()
    analyze_jindi_pricing() 