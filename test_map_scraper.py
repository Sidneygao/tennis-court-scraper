#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试地图爬虫功能
"""

from app.scrapers.detail_scraper import DetailScraper
import json

def test_map_scrapers():
    """测试地图爬虫"""
    scraper = DetailScraper()
    
    # 测试场馆名称
    test_courts = [
        "球星网球汇(合生汇球星运动中心店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆"
    ]
    
    for court_name in test_courts:
        print(f"\n{'='*60}")
        print(f"测试场馆: {court_name}")
        print(f"{'='*60}")
        
        # 测试百度地图爬虫
        print("\n🔍 测试百度地图爬虫...")
        try:
            baidu_data = scraper.scrape_baidu_map(court_name)
            if baidu_data:
                print("✅ 百度地图数据获取成功:")
                print(f"   评分: {baidu_data.get('rating')}")
                print(f"   评论数: {baidu_data.get('review_count')}")
                print(f"   评论: {len(baidu_data.get('reviews', []))} 条")
                print(f"   营业时间: {baidu_data.get('business_hours')}")
            else:
                print("❌ 百度地图数据获取失败")
        except Exception as e:
            print(f"❌ 百度地图爬虫异常: {e}")
        
        # 测试高德地图爬虫
        print("\n🔍 测试高德地图爬虫...")
        try:
            amap_data = scraper.scrape_amap(court_name)
            if amap_data:
                print("✅ 高德地图数据获取成功:")
                print(f"   评分: {amap_data.get('rating')}")
                print(f"   评论数: {amap_data.get('review_count')}")
                print(f"   评论: {len(amap_data.get('reviews', []))} 条")
                print(f"   营业时间: {amap_data.get('business_hours')}")
            else:
                print("❌ 高德地图数据获取失败")
        except Exception as e:
            print(f"❌ 高德地图爬虫异常: {e}")
        
        # 测试小红书爬虫
        print("\n🔍 测试小红书爬虫...")
        try:
            xiaohongshu_data = scraper.scrape_xiaohongshu(court_name)
            if xiaohongshu_data:
                print("✅ 小红书数据获取成功:")
                print(f"   评分: {xiaohongshu_data.get('rating')}")
                print(f"   评论数: {xiaohongshu_data.get('review_count')}")
                print(f"   评论: {len(xiaohongshu_data.get('reviews', []))} 条")
                print(f"   营业时间: {xiaohongshu_data.get('business_hours')}")
                print(f"   价格: {len(xiaohongshu_data.get('prices', []))} 项")
                print(f"   图片: {len(xiaohongshu_data.get('images', []))} 张")
            else:
                print("❌ 小红书数据获取失败")
        except Exception as e:
            print(f"❌ 小红书爬虫异常: {e}")
        
        # 测试综合爬取
        print("\n🔍 测试综合爬取...")
        try:
            merged_data = scraper.scrape_court_details(court_name)
            print("✅ 综合数据获取成功:")
            print(f"   描述: {merged_data.get('description', '')[:50]}...")
            print(f"   设施: {merged_data.get('facilities', '')[:50]}...")
            print(f"   营业时间: {merged_data.get('business_hours')}")
            print(f"   评分: {merged_data.get('rating')}")
            print(f"   价格: {len(merged_data.get('prices', []))} 项")
            print(f"   评论: {len(merged_data.get('reviews', []))} 条")
            print(f"   图片: {len(merged_data.get('images', []))} 张")
        except Exception as e:
            print(f"❌ 综合爬取异常: {e}")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    test_map_scrapers() 