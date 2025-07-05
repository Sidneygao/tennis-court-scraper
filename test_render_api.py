#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render API接口数据返回
"""

import requests
import json

def test_render_api():
    url = "https://tennis-court-scraper.onrender.com"
    
    print("测试Render API接口...")
    print(f"基础URL: {url}")
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{url}/api/health", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   应用名称: {data.get('app_name')}")
            print(f"   版本: {data.get('version')}")
            print("   ✅ 健康检查正常")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return
    
    # 测试区域列表
    print("\n2. 测试区域列表...")
    try:
        response = requests.get(f"{url}/api/courts/areas/list", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            areas = data.get('areas', [])
            print(f"   返回区域数量: {len(areas)}")
            if areas:
                print("   前3个区域:")
                for area in areas[:3]:
                    print(f"     - {area.get('name')} ({area.get('key')})")
            else:
                print("   ⚠️ 区域列表为空")
        else:
            print(f"   ❌ 区域列表失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"   ❌ 区域列表异常: {e}")
    
    # 测试场馆列表（全部）
    print("\n3. 测试场馆列表（全部）...")
    try:
        response = requests.get(f"{url}/api/courts/", timeout=20)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            courts = response.json()
            print(f"   返回场馆数量: {len(courts)}")
            if courts:
                print("   前3个场馆:")
                for court in courts[:3]:
                    print(f"     - {court.get('name')} (类型: {court.get('court_type')})")
            else:
                print("   ⚠️ 场馆列表为空")
        else:
            print(f"   ❌ 场馆列表失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"   ❌ 场馆列表异常: {e}")
    
    # 测试特定区域的场馆
    print("\n4. 测试特定区域场馆...")
    try:
        response = requests.get(f"{url}/api/courts/?area=guomao", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            courts = response.json()
            print(f"   国贸区域场馆数量: {len(courts)}")
            if courts:
                print("   前3个场馆:")
                for court in courts[:3]:
                    print(f"     - {court.get('name')} (类型: {court.get('court_type')})")
            else:
                print("   ⚠️ 国贸区域无场馆")
        else:
            print(f"   ❌ 国贸区域查询失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 国贸区域查询异常: {e}")
    
    # 测试应用信息
    print("\n5. 测试应用信息...")
    try:
        response = requests.get(f"{url}/api/info", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   应用名称: {data.get('app_name')}")
            print(f"   目标区域数量: {len(data.get('target_areas', {}))}")
            print("   ✅ 应用信息正常")
        else:
            print(f"   ❌ 应用信息失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 应用信息异常: {e}")

if __name__ == "__main__":
    test_render_api() 