#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试Render部署
"""

import requests
import time

BASE_URL = "https://tennis-court-scraper.onrender.com"

def quick_test():
    """快速测试"""
    print("🔍 快速测试Render部署...")
    print(f"URL: {BASE_URL}")
    
    # 测试首页
    print("\n1. 测试首页...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if "网球场爬虫" in content:
                print("   ✅ 首页正常")
            elif "FastAPI" in content:
                print("   ❌ 显示FastAPI默认页面")
            else:
                print("   ⚠️  页面内容异常")
        else:
            print(f"   ❌ 首页请求失败")
    except Exception as e:
        print(f"   ❌ 首页请求异常: {e}")
    
    # 测试健康检查
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 健康检查正常")
        else:
            print(f"   ❌ 健康检查失败")
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
    
    # 测试区域列表
    print("\n3. 测试区域列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/courts/areas/list", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            areas = data.get('areas', [])
            print(f"   ✅ 获取到 {len(areas)} 个区域")
        else:
            print(f"   ❌ 区域列表失败")
    except Exception as e:
        print(f"   ❌ 区域列表异常: {e}")

if __name__ == "__main__":
    quick_test() 