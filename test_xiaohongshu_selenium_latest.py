#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小红书Selenium爬虫测试脚本
测试最新的小红书爬虫功能
"""

import sys
import os
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_selenium import XiaohongshuSeleniumScraper

def test_xiaohongshu_scraper():
    """测试小红书爬虫"""
    print("🎾 小红书Selenium爬虫测试")
    print("=" * 50)
    
    # 测试场馆列表
    test_courts = [
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆",
        "球星网球汇(合生汇球星运动中心店)",
        "茂华UHN国际村-网球场"
    ]
    
    scraper = None
    try:
        # 创建单个爬虫实例用于所有测试
        print("🚀 初始化小红书爬虫...")
        scraper = XiaohongshuSeleniumScraper()
        print("✅ 爬虫初始化成功")
        
        results = {}
        
        for i, court_name in enumerate(test_courts, 1):
            print(f"\n📋 测试 {i}/{len(test_courts)}: {court_name}")
            print("-" * 40)
            
            try:
                # 记录开始时间
                start_time = time.time()
                
                # 执行爬取
                data = scraper.scrape_court_details(court_name)
                
                # 记录结束时间
                end_time = time.time()
                duration = end_time - start_time
                
                # 保存结果
                results[court_name] = {
                    "success": True,
                    "duration": round(duration, 2),
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                
                # 打印结果摘要
                print(f"✅ 爬取成功 (耗时: {duration:.2f}秒)")
                print(f"   评分: {data.get('rating', 'N/A')}")
                print(f"   评论数: {data.get('review_count', 'N/A')}")
                print(f"   价格数量: {len(data.get('prices', []))}")
                print(f"   评论数量: {len(data.get('reviews', []))}")
                print(f"   描述: {data.get('description', 'N/A')[:50]}...")
                
            except Exception as e:
                print(f"❌ 爬取失败: {e}")
                results[court_name] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            
            # 添加延迟避免过于频繁
            if i < len(test_courts):
                print("⏳ 等待5秒...")
                time.sleep(5)
        
        # 保存测试结果
        with open('xiaohongshu_selenium_latest_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 统计结果
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_count = len(results)
        
        print(f"\n📊 测试结果统计")
        print("=" * 50)
        print(f"总测试数: {total_count}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        if success_count > 0:
            avg_duration = sum(r.get('duration', 0) for r in results.values() if r.get('success', False)) / success_count
            print(f"平均耗时: {avg_duration:.2f}秒")
        
        print(f"\n📄 详细结果已保存到: xiaohongshu_selenium_latest_test_results.json")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        
    finally:
        # 确保关闭浏览器
        if scraper:
            try:
                scraper.close()
                print("\n🔒 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    test_xiaohongshu_scraper() 