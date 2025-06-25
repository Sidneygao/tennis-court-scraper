#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试缓存比较功能
验证只有在数据发生变化时才更新数据库
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"

def test_cache_comparison():
    """测试缓存比较功能"""
    print("🧪 开始测试缓存比较功能...")
    print("=" * 60)
    
    # 1. 获取第一个场馆进行测试
    try:
        response = requests.get(f"{BASE_URL}/api/courts")
        if response.status_code != 200:
            print("❌ 无法获取场馆列表")
            return
        
        courts = response.json()
        if not courts:
            print("❌ 没有找到场馆数据")
            return
        
        test_court = courts[0]
        court_id = test_court['id']
        court_name = test_court['name']
        
        print(f"📋 测试场馆: {court_name} (ID: {court_id})")
        print()
        
    except Exception as e:
        print(f"❌ 获取场馆列表失败: {e}")
        return
    
    # 2. 第一次更新（应该会更新数据）
    print("🔄 第一次更新（应该会更新数据）:")
    try:
        response = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
        if response.status_code == 200:
            result = response.json()
            print(f"  状态码: {response.status_code}")
            print(f"  消息: {result.get('message', '')}")
            print(f"  变化: {result.get('changes', {})}")
            print(f"  更新字段: {result.get('updated_fields', [])}")
        else:
            print(f"  ❌ 更新失败: {response.status_code}")
            return
    except Exception as e:
        print(f"  ❌ 更新异常: {e}")
        return
    
    print()
    
    # 3. 等待一秒
    print("⏳ 等待1秒...")
    time.sleep(1)
    print()
    
    # 4. 第二次更新（应该不会更新数据）
    print("🔄 第二次更新（应该不会更新数据）:")
    try:
        response = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
        if response.status_code == 200:
            result = response.json()
            print(f"  状态码: {response.status_code}")
            print(f"  消息: {result.get('message', '')}")
            print(f"  变化: {result.get('changes', {})}")
            print(f"  更新字段: {result.get('updated_fields', [])}")
        else:
            print(f"  ❌ 更新失败: {response.status_code}")
            return
    except Exception as e:
        print(f"  ❌ 更新异常: {e}")
        return
    
    print()
    
    # 5. 强制更新（应该会更新数据）
    print("🔄 强制更新（应该会更新数据）:")
    try:
        response = requests.get(f"{BASE_URL}/api/details/{court_id}?force_update=true")
        if response.status_code == 200:
            result = response.json()
            print(f"  状态码: {response.status_code}")
            print(f"  数据获取成功")
            print(f"  描述: {result.get('merged_description', 'N/A')[:50]}...")
            print(f"  评分: {result.get('merged_rating', 'N/A')}")
            print(f"  价格数量: {len(result.get('merged_prices', []))}")
        else:
            print(f"  ❌ 获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"  ❌ 获取异常: {e}")
        return
    
    print()
    
    # 6. 测试数据哈希比较
    print("🔍 测试数据哈希比较功能:")
    try:
        from app.scrapers.detail_scraper import DetailScraper
        
        scraper = DetailScraper()
        
        # 测试相同数据
        data1 = {"name": "test", "price": 100, "items": [1, 2, 3]}
        data2 = {"name": "test", "price": 100, "items": [1, 2, 3]}
        hash1 = scraper.generate_data_hash(data1)
        hash2 = scraper.generate_data_hash(data2)
        
        print(f"  相同数据哈希比较: {hash1 == hash2} (应该为True)")
        
        # 测试不同数据
        data3 = {"name": "test", "price": 200, "items": [1, 2, 3]}
        hash3 = scraper.generate_data_hash(data3)
        print(f"  不同数据哈希比较: {hash1 == hash3} (应该为False)")
        
        # 测试数据比较
        changes = scraper.compare_data(data1, data3)
        print(f"  数据变化检测: {changes}")
        
    except Exception as e:
        print(f"  ❌ 哈希比较测试失败: {e}")
    
    print()
    print("✅ 缓存比较功能测试完成!")

def test_batch_cache():
    """测试批量缓存更新"""
    print("\n🧪 开始测试批量缓存更新...")
    print("=" * 60)
    
    try:
        # 获取前3个场馆进行测试
        response = requests.get(f"{BASE_URL}/api/courts")
        if response.status_code != 200:
            print("❌ 无法获取场馆列表")
            return
        
        courts = response.json()[:3]  # 只取前3个
        print(f"📋 测试 {len(courts)} 个场馆的批量更新")
        
        for i, court in enumerate(courts, 1):
            court_id = court['id']
            court_name = court['name']
            
            print(f"\n[{i}/{len(courts)}] 测试场馆: {court_name}")
            
            # 第一次更新
            response1 = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
            if response1.status_code == 200:
                result1 = response1.json()
                updated_fields1 = result1.get('updated_fields', [])
                print(f"  第一次更新: {'有变化' if updated_fields1 else '无变化'}")
            
            # 第二次更新
            response2 = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
            if response2.status_code == 200:
                result2 = response2.json()
                updated_fields2 = result2.get('updated_fields', [])
                print(f"  第二次更新: {'有变化' if updated_fields2 else '无变化'}")
                
                # 验证第二次应该无变化
                if not updated_fields2:
                    print(f"  ✅ 缓存机制正常")
                else:
                    print(f"  ⚠️  可能存在问题")
        
    except Exception as e:
        print(f"❌ 批量测试失败: {e}")

if __name__ == "__main__":
    # 检查后端是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/courts")
        if response.status_code != 200:
            print("❌ 后端服务未运行或无法访问")
            print("请先启动后端服务: python run.py")
            exit(1)
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("请先启动后端服务: python run.py")
        exit(1)
    
    # 运行测试
    test_cache_comparison()
    test_batch_cache() 