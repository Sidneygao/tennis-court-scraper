#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
测试后端API是否正常工作
"""

import requests
import json
import time

def test_backend():
    """测试后端API"""
    base_url = "http://localhost:8000"
    
    print("🧪 开始系统测试")
    print("=" * 50)
    
    # 测试1: 健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 测试2: 获取场馆列表
    print("\n2. 测试获取场馆列表...")
    try:
        response = requests.get(f"{base_url}/api/courts?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取场馆列表成功: 找到 {len(data)} 个场馆")
            if data:
                print(f"   示例场馆: {data[0]['name']}")
        else:
            print(f"❌ 获取场馆列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取场馆列表异常: {e}")
        return False
    
    # 测试3: 获取统计信息
    print("\n3. 测试获取统计信息...")
    try:
        response = requests.get(f"{base_url}/api/courts/stats/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取统计信息成功: 总场馆数 {data.get('total_courts', 0)}")
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取统计信息异常: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 系统测试完成")
    return True

if __name__ == "__main__":
    print("🎾 北京网球场馆信息抓取系统 - 测试脚本")
    print("=" * 60)
    
    # 等待后端启动
    print("⏳ 等待后端启动...")
    time.sleep(3)
    
    # 测试后端
    backend_ok = test_backend()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    
    if backend_ok:
        print("\n🎉 测试通过！系统运行正常")
    else:
        print("\n⚠️ 测试失败，请检查系统状态") 