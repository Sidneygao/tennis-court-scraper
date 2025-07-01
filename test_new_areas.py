#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试丰台区东部、西部和亦庄三个新区域的功能
"""
import requests
import json

def test_new_areas():
    print("🔍 测试新区域功能...")
    base_url = "http://localhost:8000"
    
    # 1. 测试区域列表API
    print("\n📊 测试区域列表API:")
    try:
        response = requests.get(f"{base_url}/api/courts/areas/list")
        if response.status_code == 200:
            areas = response.json()["areas"]
            print(f"总区域数: {len(areas)}")
            
            # 查找新区域
            new_areas = []
            for area in areas:
                if area["key"] in ["fengtai_east", "fengtai_west", "yizhuang"]:
                    new_areas.append(area)
                    print(f"  ✅ {area['key']}: {area['name']}")
            
            if len(new_areas) == 3:
                print("✅ 三个新区域都已正确添加")
            else:
                print(f"❌ 新区域数量不正确: {len(new_areas)}")
        else:
            print(f"❌ 区域列表API请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 区域列表API测试失败: {e}")
    
    # 2. 测试统计信息API
    print("\n📈 测试统计信息API:")
    try:
        response = requests.get(f"{base_url}/api/courts/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"总场馆数: {stats['total_courts']}")
            
            # 检查新区域的统计
            for area_key in ["fengtai_east", "fengtai_west", "yizhuang"]:
                if area_key in stats["area_stats"]:
                    area_stat = stats["area_stats"][area_key]
                    print(f"  {area_stat['name']}: {area_stat['count']} 个场馆")
                else:
                    print(f"  ❌ {area_key} 区域统计缺失")
        else:
            print(f"❌ 统计信息API请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息API测试失败: {e}")
    
    # 3. 测试各区域的场馆列表
    print("\n🏟️ 测试各区域场馆列表:")
    for area_key in ["fengtai_east", "fengtai_west", "yizhuang"]:
        try:
            response = requests.get(f"{base_url}/api/courts/?area={area_key}&limit=10")
            if response.status_code == 200:
                courts = response.json()
                print(f"\n{area_key} 区域场馆 ({len(courts)} 个):")
                for court in courts[:5]:  # 只显示前5个
                    print(f"  - {court['name']} (经度: {court.get('longitude', 'N/A')})")
                if len(courts) > 5:
                    print(f"  ... 还有 {len(courts) - 5} 个场馆")
            else:
                print(f"❌ {area_key} 区域API请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {area_key} 区域测试失败: {e}")
    
    # 4. 验证丰台区场馆的经度分布
    print("\n🔍 验证丰台区场馆经度分布:")
    try:
        # 获取所有丰台区场馆
        response = requests.get(f"{base_url}/api/courts/?area=fengtai_east&limit=100")
        fengtai_east = response.json() if response.status_code == 200 else []
        
        response = requests.get(f"{base_url}/api/courts/?area=fengtai_west&limit=100")
        fengtai_west = response.json() if response.status_code == 200 else []
        
        print(f"丰台区东部: {len(fengtai_east)} 个场馆")
        for court in fengtai_east:
            longitude = court.get('longitude', 0)
            if longitude <= 116.321:
                print(f"  ⚠️  错误: {court['name']} 经度 {longitude} 应该属于西部")
        
        print(f"丰台区西部: {len(fengtai_west)} 个场馆")
        for court in fengtai_west:
            longitude = court.get('longitude', 0)
            if longitude > 116.321:
                print(f"  ⚠️  错误: {court['name']} 经度 {longitude} 应该属于东部")
        
        print("✅ 丰台区场馆经度分布验证完成")
        
    except Exception as e:
        print(f"❌ 丰台区场馆验证失败: {e}")

if __name__ == "__main__":
    test_new_areas() 