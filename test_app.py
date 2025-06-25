#!/usr/bin/env python3
"""
网球场地信息抓取系统测试脚本
"""

import requests
import json
import time
from pathlib import Path

# 应用配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_app_info():
    """测试应用信息"""
    print("🔍 测试应用信息...")
    try:
        response = requests.get(f"{API_BASE}/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 应用信息: {data}")
            return True
        else:
            print(f"❌ 应用信息获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 应用信息异常: {e}")
        return False

def test_courts_api():
    """测试场馆API"""
    print("🔍 测试场馆API...")
    try:
        # 测试获取场馆列表
        response = requests.get(f"{API_BASE}/courts", timeout=10)
        if response.status_code == 200:
            courts = response.json()
            print(f"✅ 获取场馆列表成功: {len(courts)} 个场馆")
            
            # 测试获取区域列表
            response = requests.get(f"{API_BASE}/courts/areas/list", timeout=10)
            if response.status_code == 200:
                areas = response.json()
                print(f"✅ 获取区域列表成功: {len(areas['areas'])} 个区域")
            
            # 测试获取统计信息
            response = requests.get(f"{API_BASE}/courts/stats/summary", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 获取统计信息成功: {stats}")
            
            return True
        else:
            print(f"❌ 场馆API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 场馆API异常: {e}")
        return False

def test_scraper_api():
    """测试爬虫API"""
    print("🔍 测试爬虫API... POST /api/scraper/scrape/amap")
    try:
        response = requests.post(f"{API_BASE}/scraper/scrape/amap", timeout=20)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_frontend():
    """测试前端页面"""
    print("🔍 测试前端页面...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面访问成功")
            return True
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🎾 网球场地信息抓取系统测试")
    print("=" * 50)
    
    # 等待应用启动
    print("等待应用启动...")
    time.sleep(3)
    
    # 执行测试
    tests = [
        test_health_check,
        test_app_info,
        test_courts_api,
        test_scraper_api,
        test_frontend
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        print()
    
    # 输出测试结果
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用运行正常。")
        print(f"🌐 访问地址: {BASE_URL}")
        print(f"📚 API文档: {BASE_URL}/api/docs")
    else:
        print("⚠️  部分测试失败，请检查应用状态。")

if __name__ == "__main__":
    main() 