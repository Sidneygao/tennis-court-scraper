#!/usr/bin/env python3
"""
测试详情API功能的脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_detail_api():
    """测试详情API功能"""
    print("🧪 开始测试详情API功能...")
    
    # 1. 获取场馆列表
    print("\n1. 获取场馆列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/courts?limit=3")
        if response.status_code == 200:
            courts = response.json()
            print(f"✅ 获取到 {len(courts)} 个场馆")
            if courts:
                court_id = courts[0]['id']
                court_name = courts[0]['name']
                print(f"   使用场馆: {court_name} (ID: {court_id})")
            else:
                print("❌ 没有场馆数据")
                return
        else:
            print(f"❌ 获取场馆列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 测试预览详情（应该没有数据）
    print(f"\n2. 测试预览详情 (场馆ID: {court_id})...")
    try:
        response = requests.get(f"{BASE_URL}/api/details/{court_id}/preview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 预览详情成功")
            print(f"   场馆名称: {data['court_name']}")
            print(f"   是否有详情: {data['has_detail']}")
            if not data['has_detail']:
                print(f"   提示信息: {data['message']}")
        else:
            print(f"❌ 预览详情失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试更新详情
    print(f"\n3. 测试更新详情 (场馆ID: {court_id})...")
    try:
        response = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 更新详情成功: {data['message']}")
        else:
            print(f"❌ 更新详情失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 4. 再次测试预览详情（应该有数据了）
    print(f"\n4. 再次测试预览详情 (场馆ID: {court_id})...")
    try:
        response = requests.get(f"{BASE_URL}/api/details/{court_id}/preview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 预览详情成功")
            print(f"   场馆名称: {data['court_name']}")
            print(f"   是否有详情: {data['has_detail']}")
            if data['has_detail']:
                detail = data['detail']
                print(f"   描述: {detail['description'][:50]}...")
                print(f"   评分: {detail['rating']}")
                print(f"   营业时间: {detail['business_hours']}")
                print(f"   设施: {detail['facilities'][:50]}...")
                print(f"   价格数量: {len(detail['prices'])}")
                print(f"   评论数量: {len(detail['reviews'])}")
        else:
            print(f"❌ 预览详情失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 5. 测试获取完整详情
    print(f"\n5. 测试获取完整详情 (场馆ID: {court_id})...")
    try:
        response = requests.get(f"{BASE_URL}/api/details/{court_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取完整详情成功")
            print(f"   详情ID: {data['id']}")
            print(f"   场馆ID: {data['court_id']}")
            print(f"   融合描述: {data['merged_description'][:50]}...")
            print(f"   点评评分: {data['dianping_rating']}")
            print(f"   美团评分: {data['meituan_rating']}")
            print(f"   融合评分: {data['merged_rating']}")
        else:
            print(f"❌ 获取完整详情失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n🎉 详情API功能测试完成！")

if __name__ == "__main__":
    test_detail_api() 