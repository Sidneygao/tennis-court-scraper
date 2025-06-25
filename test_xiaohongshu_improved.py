#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改进的小红书爬虫测试脚本
测试真实的小红书数据爬取功能
"""

import sys
import os
import time
import json
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_selenium import XiaohongshuSeleniumScraper

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xiaohongshu_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def test_xiaohongshu_scraper():
    """测试小红书爬虫"""
    print("🎾 改进的小红书爬虫测试")
    print("=" * 50)
    
    # 测试场馆列表
    test_courts = [
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆",
        "球星网球汇(合生汇球星运动中心店)",
        "茂华UHN国际村-网球场"
    ]
    
    results = {}
    
    for i, court_name in enumerate(test_courts, 1):
        print(f"\n📋 测试 {i}/{len(test_courts)}: {court_name}")
        print("-" * 40)
        
        scraper = None
        try:
            # 为每个测试创建新的爬虫实例
            scraper = XiaohongshuSeleniumScraper()
            
            # 记录开始时间
            start_time = time.time()
            
            # 执行爬取
            data = scraper.scrape_court_details(court_name)
            
            # 记录结束时间
            end_time = time.time()
            duration = end_time - start_time
            
            if data:
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
                
                # 打印价格信息
                if data.get('prices'):
                    print("   价格信息:")
                    for price in data['prices']:
                        print(f"     {price.get('type', 'N/A')}: {price.get('price', 'N/A')}")
                
            else:
                print(f"❌ 爬取失败: 未获取到数据")
                results[court_name] = {
                    "success": False,
                    "error": "未获取到数据",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            results[court_name] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # 确保关闭浏览器
            if scraper:
                try:
                    scraper.close()
                    print("🔒 浏览器已关闭")
                except:
                    pass
        
        # 添加延迟避免过于频繁
        if i < len(test_courts):
            print("⏳ 等待10秒...")
            time.sleep(10)
    
    # 保存测试结果
    result_file = f'xiaohongshu_improved_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
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
    
    print(f"\n📄 详细结果已保存到: {result_file}")
    
    # 打印成功案例的详细信息
    if success_count > 0:
        print(f"\n📋 成功案例详情:")
        print("-" * 30)
        for court_name, result in results.items():
            if result.get('success'):
                data = result.get('data', {})
                print(f"\n🏟️ {court_name}:")
                print(f"   评分: {data.get('rating', 'N/A')}")
                print(f"   评论数: {data.get('review_count', 'N/A')}")
                print(f"   营业时间: {data.get('business_hours', 'N/A')}")
                print(f"   设施: {data.get('facilities', 'N/A')}")
                if data.get('prices'):
                    print("   价格:")
                    for price in data['prices']:
                        print(f"     {price.get('type', 'N/A')}: {price.get('price', 'N/A')}")

def test_single_court():
    """测试单个场馆"""
    print("🎾 单个场馆测试")
    print("=" * 30)
    
    court_name = "乾坤体育网球学练馆(望京SOHOT1商场店)"
    print(f"测试场馆: {court_name}")
    
    scraper = None
    try:
        scraper = XiaohongshuSeleniumScraper()
        
        start_time = time.time()
        data = scraper.scrape_court_details(court_name)
        end_time = time.time()
        
        if data:
            print(f"✅ 爬取成功 (耗时: {end_time - start_time:.2f}秒)")
            print("\n📋 详细数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("❌ 爬取失败")
            
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='小红书爬虫测试')
    parser.add_argument('--single', action='store_true', help='测试单个场馆')
    parser.add_argument('--court', type=str, help='指定场馆名称')
    
    args = parser.parse_args()
    
    if args.single:
        if args.court:
            # 测试指定场馆
            court_name = args.court
            print(f"🎾 测试指定场馆: {court_name}")
            print("=" * 30)
            
            scraper = None
            try:
                scraper = XiaohongshuSeleniumScraper()
                
                start_time = time.time()
                data = scraper.scrape_court_details(court_name)
                end_time = time.time()
                
                if data:
                    print(f"✅ 爬取成功 (耗时: {end_time - start_time:.2f}秒)")
                    print("\n📋 详细数据:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    print("❌ 爬取失败")
                    
            except Exception as e:
                print(f"❌ 爬取失败: {e}")
            finally:
                if scraper:
                    scraper.close()
        else:
            test_single_court()
    else:
        test_xiaohongshu_scraper() 