#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能小红书爬虫测试脚本
测试智能爬虫功能
"""

import sys
import os
import time
import json
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.xiaohongshu_smart import XiaohongshuSmartScraper

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xiaohongshu_smart_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def test_xiaohongshu_smart_scraper():
    """测试智能小红书爬虫"""
    print("🎾 智能小红书爬虫测试")
    print("=" * 50)
    
    # 测试场馆列表
    test_courts = [
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆",
        "球星网球汇(合生汇球星运动中心店)",
        "茂华UHN国际村-网球场",
        "其他网球馆"  # 测试通用模板
    ]
    
    scraper = XiaohongshuSmartScraper()
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
                print(f"   位置: {data.get('location', 'N/A')}")
                
                # 打印价格信息
                if data.get('prices'):
                    print("   价格信息:")
                    for price in data['prices']:
                        print(f"     {price.get('type', 'N/A')}: {price.get('price', 'N/A')} ({price.get('time_range', 'N/A')})")
                
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
        
        # 添加短暂延迟
        if i < len(test_courts):
            print("⏳ 等待1秒...")
            time.sleep(1)
    
    # 保存测试结果
    result_file = f'xiaohongshu_smart_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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
                print(f"   位置: {data.get('location', 'N/A')}")
                if data.get('prices'):
                    print("   价格:")
                    for price in data['prices']:
                        print(f"     {price.get('type', 'N/A')}: {price.get('price', 'N/A')}")

def test_single_court():
    """测试单个场馆"""
    print("🎾 单个场馆智能测试")
    print("=" * 30)
    
    court_name = "乾坤体育网球学练馆(望京SOHOT1商场店)"
    print(f"测试场馆: {court_name}")
    
    scraper = XiaohongshuSmartScraper()
    
    try:
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

def test_search_function():
    """测试搜索功能"""
    print("🔍 测试搜索功能")
    print("=" * 30)
    
    scraper = XiaohongshuSmartScraper()
    keyword = "网球"
    
    try:
        print(f"搜索关键词: {keyword}")
        result = scraper.search_notes(keyword, page=1, page_size=5)
        
        if result:
            notes = result.get('data', {}).get('notes', [])
            print(f"✅ 搜索成功，获取到 {len(notes)} 条笔记")
            
            for i, note in enumerate(notes[:3], 1):
                print(f"\n笔记 {i}:")
                print(f"  标题: {note.get('title', 'N/A')}")
                print(f"  内容: {note.get('desc', 'N/A')[:100]}...")
                print(f"  作者: {note.get('user', {}).get('nickname', 'N/A')}")
                print(f"  点赞: {note.get('likes', 'N/A')}")
                print(f"  评论: {note.get('comments', 'N/A')}")
                print(f"  收藏: {note.get('collects', 'N/A')}")
        else:
            print("❌ 搜索失败")
            
    except Exception as e:
        print(f"❌ 搜索失败: {e}")

def test_template_matching():
    """测试模板匹配功能"""
    print("🔍 测试模板匹配功能")
    print("=" * 30)
    
    scraper = XiaohongshuSmartScraper()
    
    # 测试不同的场馆名称
    test_names = [
        "乾坤体育网球学练馆",
        "SOLOTennis俱乐部",
        "动之光网球馆",
        "球星网球汇",
        "茂华UHN网球场",
        "其他网球馆"
    ]
    
    for name in test_names:
        print(f"\n测试场馆: {name}")
        template = scraper._find_matching_template(name)
        
        if template:
            print(f"✅ 匹配到模板: {template['location']}")
            print(f"   基础评分: {template['base_rating']}")
            print(f"   基础价格: {template['base_price']}元")
            print(f"   设施: {', '.join(template['facilities'])}")
        else:
            print("⚠️ 未匹配到模板，将使用通用数据")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='智能小红书爬虫测试')
    parser.add_argument('--single', action='store_true', help='测试单个场馆')
    parser.add_argument('--search', action='store_true', help='测试搜索功能')
    parser.add_argument('--template', action='store_true', help='测试模板匹配功能')
    parser.add_argument('--court', type=str, help='指定场馆名称')
    
    args = parser.parse_args()
    
    if args.template:
        test_template_matching()
    elif args.search:
        test_search_function()
    elif args.single:
        if args.court:
            # 测试指定场馆
            court_name = args.court
            print(f"🎾 测试指定场馆: {court_name}")
            print("=" * 30)
            
            scraper = XiaohongshuSmartScraper()
            
            try:
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
        else:
            test_single_court()
    else:
        test_xiaohongshu_smart_scraper() 