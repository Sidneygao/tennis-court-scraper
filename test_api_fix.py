#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API接口修正
"""
import requests
import json

def test_api():
    """测试API接口"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 测试API接口修正...")
    
    # 测试丰台东部
    print("\n📊 测试丰台东部区域:")
    try:
        response = requests.get(f"{base_url}/api/courts/?area=fengtai_east&limit=10")
        if response.status_code == 200:
            courts = response.json()
            print(f"丰台东部场馆数: {len(courts)}")
            for i, court in enumerate(courts[:3]):
                print(f"  {i+1}. {court['name']}")
                print(f"     地址: {court['address']}")
                print(f"     区域: {court['area']}")
                print()
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试丰台西部
    print("\n📊 测试丰台西部区域:")
    try:
        response = requests.get(f"{base_url}/api/courts/?area=fengtai_west&limit=10")
        if response.status_code == 200:
            courts = response.json()
            print(f"丰台西部场馆数: {len(courts)}")
            for i, court in enumerate(courts[:3]):
                print(f"  {i+1}. {court['name']}")
                print(f"     地址: {court['address']}")
                print(f"     区域: {court['area']}")
                print()
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试亦庄
    print("\n📊 测试亦庄区域:")
    try:
        response = requests.get(f"{base_url}/api/courts/?area=yizhuang&limit=10")
        if response.status_code == 200:
            courts = response.json()
            print(f"亦庄场馆数: {len(courts)}")
            for i, court in enumerate(courts[:3]):
                print(f"  {i+1}. {court['name']}")
                print(f"     地址: {court['address']}")
                print(f"     区域: {court['area']}")
                print()
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试统计接口
    print("\n📊 测试统计接口:")
    try:
        response = requests.get(f"{base_url}/api/courts/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print("区域统计:")
            for area, data in stats['area_stats'].items():
                if area in ['fengtai_east', 'fengtai_west', 'yizhuang']:
                    print(f"  {data['name']}: {data['count']} 个场馆")
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_api() 