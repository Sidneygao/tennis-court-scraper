#!/usr/bin/env python3
"""
调试地图生成器，检查高德地图API的响应
"""

import os
import requests
import json

def debug_amap_api():
    """调试高德地图API"""
    print("🔍 调试高德地图API...")
    
    # 使用您提供的API Key
    AMAP_KEY = "213dd87b21e5e3d8eab72f1a62da1a8e"
    
    # 测试参数
    latitude = 39.913837
    longitude = 116.458604
    court_name = "SOLOTennis网球俱乐部"
    
    url = "https://restapi.amap.com/v3/staticmap"
    params = {
        'location': f"{longitude},{latitude}",
        'zoom': 16,
        'size': '600*300',
        'key': AMAP_KEY,
        'markers': f"{longitude},{latitude},red"
    }
    
    print(f"🔗 请求URL: {url}")
    print(f"📋 参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📏 响应内容长度: {len(response.content)} 字节")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            print(f"📋 内容类型: {content_type}")
            
            if 'image' in content_type:
                print("✅ 响应是图片格式")
                # 保存测试图片
                test_file = "test_map.png"
                with open(test_file, 'wb') as f:
                    f.write(response.content)
                print(f"💾 测试图片已保存: {test_file}")
            else:
                print("❌ 响应不是图片格式")
                print(f"📄 响应内容: {response.text[:200]}...")
        else:
            print(f"❌ API返回错误状态码")
            print(f"📄 错误响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def check_amap_key():
    """检查高德地图API Key是否有效"""
    print("\n🔑 检查高德地图API Key...")
    
    AMAP_KEY = "213dd87b21e5e3d8eab72f1a62da1a8e"
    
    # 使用地理编码API测试Key
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        'address': '北京市朝阳区国贸',
        'key': AMAP_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"📊 地理编码API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('status') == '1':
                print("✅ API Key有效")
            else:
                print(f"❌ API Key无效: {data.get('info', '未知错误')}")
        else:
            print(f"❌ 地理编码API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查API Key失败: {e}")

if __name__ == "__main__":
    debug_amap_api()
    check_amap_key() 