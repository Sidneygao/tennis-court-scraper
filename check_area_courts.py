#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查双井、国贸等区域的场馆数据
"""
import requests
import json

def check_area_courts():
    """检查各区域的场馆数据"""
    base_url = "http://127.0.0.1:8000"
    
    # 测试区域
    test_areas = ['shuangjing', 'guomao', 'sanyuanqiao', 'sanlitun']
    
    print("检查各区域场馆数据:")
    print("=" * 60)
    
    for area in test_areas:
        try:
            # 获取区域场馆列表
            courts_url = f"{base_url}/api/courts/?area={area}&limit=100"
            courts_response = requests.get(courts_url, timeout=5)
            
            print(f"\n区域: {area}")
            print(f"API状态: {courts_response.status_code}")
            
            if courts_response.status_code == 200:
                courts = courts_response.json()  # 直接是列表
                
                print(f"场馆数量: {len(courts)}")
                
                if courts:
                    print("前5个场馆:")
                    for i, court in enumerate(courts[:5]):
                        print(f"  {i+1}. ID: {court.get('id')} - {court.get('name')}")
                        print(f"     地址: {court.get('address')}")
                        print(f"     类型: {court.get('court_type')}")
                        print()
                else:
                    print("❌ 该区域没有场馆数据")
            else:
                print(f"❌ API请求失败: {courts_response.text}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"检查区域 {area} 失败: {e}")
    
    print("\n结论:")
    print("如果API返回200但前端不显示场馆，可能原因:")
    print("1. 前端JavaScript错误")
    print("2. 前端渲染逻辑问题")
    print("3. 浏览器缓存问题")

if __name__ == "__main__":
    check_area_courts() 