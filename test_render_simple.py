#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试Render服务
"""

import requests
import time

def test_render():
    url = "https://tennis-court-scraper.onrender.com"
    
    print("测试Render服务...")
    print(f"URL: {url}")
    
    # 测试首页
    print("\n1. 测试首页...")
    try:
        response = requests.get(url, timeout=30)
        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        if response.status_code == 200:
            content = response.text[:300]
            print(f"   内容预览: {content}")
            
            if "网球场爬虫" in content:
                print("   ✅ 首页正常")
            elif "FastAPI" in content:
                print("   ❌ 显示FastAPI默认页面")
            else:
                print("   ⚠️ 页面内容异常")
        else:
            print(f"   ❌ 首页失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ 首页超时")
    except Exception as e:
        print(f"   ❌ 首页异常: {e}")
    
    # 测试API
    print("\n2. 测试API...")
    try:
        response = requests.get(f"{url}/api/health", timeout=15)
        print(f"   健康检查状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 健康检查正常")
            
            # 测试区域列表
            response = requests.get(f"{url}/api/courts/areas/list", timeout=15)
            print(f"   区域列表状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                areas = data.get('areas', [])
                print(f"   ✅ 获取到 {len(areas)} 个区域")
                
                # 测试场馆列表
                response = requests.get(f"{url}/api/courts/", timeout=15)
                print(f"   场馆列表状态码: {response.status_code}")
                
                if response.status_code == 200:
                    courts = response.json()
                    print(f"   ✅ 获取到 {len(courts)} 个场馆")
                else:
                    print(f"   ❌ 场馆列表失败: {response.status_code}")
            else:
                print(f"   ❌ 区域列表失败: {response.status_code}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ API超时")
    except Exception as e:
        print(f"   ❌ API异常: {e}")

if __name__ == "__main__":
    test_render() 