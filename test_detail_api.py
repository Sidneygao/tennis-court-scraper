#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试详情API
"""

import requests
import json

def test_detail_api():
    print("测试详情API...")
    
    # 测试有地图图片的场馆ID=2
    court_id = 2
    court_name = "北京嘉里健身室内网球场-室内游泳池"
    
    print(f"测试场馆ID: {court_id}, 名称: {court_name}")
    
    # 测试详情API
    url = f"https://tennis-court-scraper.onrender.com/api/details/{court_id}/preview"
    response = requests.get(url, timeout=10)
    
    print(f"详情API状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"详情数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get('has_detail'):
            print("✅ 有详情数据")
            detail = data.get('detail', {})
            if detail.get('map_image'):
                print(f"✅ 有地图图片: {detail['map_image']}")
            else:
                print("❌ 没有地图图片")
        else:
            print("❌ 没有详情数据")
    else:
        print(f"❌ API请求失败: {response.text}")

if __name__ == "__main__":
    test_detail_api() 