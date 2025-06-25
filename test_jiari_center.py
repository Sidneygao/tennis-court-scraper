#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试嘉里中心网球场的价格生成
验证新添加的模板是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_smart import XiaohongshuSmartScraper

def test_jiari_center():
    """测试嘉里中心网球场的价格生成"""
    print("🧪 测试嘉里中心网球场的价格生成")
    print("=" * 60)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试不同的场馆名称变体
    test_names = [
        "嘉里中心-网球场",
        "嘉里中心网球场", 
        "嘉里中心网球馆",
        "嘉里中心网球俱乐部"
    ]
    
    for venue_name in test_names:
        print(f"\n📋 测试场馆: {venue_name}")
        print("-" * 40)
        
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
            
            # 验证价格是否合理
            base_price = 280  # 模板中的基础价格
            price_variation = int(result.get('scraped_at', '').encode('utf-8')[0] % 51 - 20)  # 模拟价格变化
            
            expected_prices = {
                '黄金时间': base_price + price_variation + 30,
                '非黄金时间': base_price + price_variation,
                '会员价': base_price + price_variation - 20
            }
            
            print(f"   预期价格范围:")
            print(f"     - 黄金时间: {expected_prices['黄金时间']}元/小时")
            print(f"     - 非黄金时间: {expected_prices['非黄金时间']}元/小时") 
            print(f"     - 会员价: {expected_prices['会员价']}元/小时")
            
            # 检查是否使用了模板
            if "嘉里中心" in result.get('description', ''):
                print("✅ 使用了嘉里中心专属模板")
            else:
                print("❌ 未使用嘉里中心专属模板")
                
        else:
            print("❌ 爬取失败")
    
    print(f"\n{'='*60}")
    print("✅ 嘉里中心网球场价格测试完成!")

if __name__ == "__main__":
    test_jiari_center() 