#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.scrapers.detail_scraper import DetailScraper

def test_xiaohongshu_scraper():
    """测试小红书爬虫"""
    scraper = DetailScraper()
    
    # 测试场馆列表
    test_courts = [
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆",
        "球星网球汇(合生汇球星运动中心店)"
    ]
    
    print("🎾 小红书爬虫测试")
    print("=" * 50)
    
    for i, court_name in enumerate(test_courts, 1):
        print(f"\n{i}. 测试场馆: {court_name}")
        print("-" * 30)
        
        try:
            # 直接调用小红书爬虫
            xiaohongshu_data = scraper.scrape_xiaohongshu(court_name)
            
            if xiaohongshu_data:
                print("✅ 小红书数据获取成功:")
                print(f"   描述: {xiaohongshu_data.get('description', '无')}")
                print(f"   评分: {xiaohongshu_data.get('rating', '无')}")
                print(f"   评论数: {xiaohongshu_data.get('review_count', '无')}")
                print(f"   营业时间: {xiaohongshu_data.get('business_hours', '无')}")
                print(f"   设施: {xiaohongshu_data.get('facilities', '无')}")
                print(f"   价格: {len(xiaohongshu_data.get('prices', []))} 项")
                print(f"   评论: {len(xiaohongshu_data.get('reviews', []))} 条")
                print(f"   图片: {len(xiaohongshu_data.get('images', []))} 张")
            else:
                print("❌ 小红书数据获取失败")
                
        except Exception as e:
            print(f"❌ 测试出错: {e}")
        
        print()
    
    print("=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_xiaohongshu_scraper() 