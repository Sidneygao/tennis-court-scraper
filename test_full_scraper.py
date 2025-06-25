#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.scrapers.detail_scraper import DetailScraper

def test_full_scraper():
    """测试完整的详情抓取流程"""
    scraper = DetailScraper()
    
    # 测试场馆
    test_court = "SOLOTennis网球俱乐部"
    
    print("🎾 完整详情抓取测试")
    print("=" * 50)
    print(f"测试场馆: {test_court}")
    print("-" * 30)
    
    try:
        # 调用完整的详情抓取方法
        merged_data = scraper.xiaohongshu_scraper.scrape_court_details(test_court)
        
        print("✅ 详情抓取完成:")
        print(f"   描述: {merged_data.get('description', '无')}")
        print(f"   设施: {merged_data.get('facilities', '无')}")
        print(f"   营业时间: {merged_data.get('business_hours', '无')}")
        print(f"   评分: {merged_data.get('rating', '无')}")
        print(f"   价格: {len(merged_data.get('prices', []))} 项")
        print(f"   评论: {len(merged_data.get('reviews', []))} 条")
        print(f"   图片: {len(merged_data.get('images', []))} 张")
        
        # 显示详细的价格信息
        if merged_data.get('prices'):
            print("\n   价格详情:")
            for price in merged_data['prices']:
                print(f"     - {price.get('type', '未知')}: {price.get('price', '未知')}")
        
        # 显示详细的评论信息
        if merged_data.get('reviews'):
            print("\n   评论详情:")
            for i, review in enumerate(merged_data['reviews'][:3], 1):  # 只显示前3条
                print(f"     {i}. {review.get('user', '用户')} - {review.get('rating', 0)}星")
                print(f"        {review.get('content', '无内容')}")
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_full_scraper() 