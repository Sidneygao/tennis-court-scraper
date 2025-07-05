#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试详情API的价格数据
"""

import requests
import json

def test_detail_api():
    url = "https://tennis-court-scraper.onrender.com"
    
    print("测试详情API...")
    
    # 先获取场馆列表
    try:
        response = requests.get(f"{url}/api/courts/", timeout=15)
        if response.status_code == 200:
            courts = response.json()
            if courts:
                # 测试第一个场馆的详情
                court_id = courts[0]['id']
                print(f"测试场馆ID: {court_id}, 名称: {courts[0]['name']}")
                
                # 获取详情
                detail_response = requests.get(f"{url}/api/details/{court_id}/preview", timeout=15)
                print(f"详情API状态码: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"详情数据: {json.dumps(detail_data, ensure_ascii=False, indent=2)}")
                    
                    # 检查价格相关字段
                    if detail_data.get('has_detail'):
                        detail = detail_data['detail']
                        print(f"\n价格相关字段:")
                        print(f"  manual_prices: {detail.get('manual_prices')}")
                        print(f"  merged_prices: {detail.get('merged_prices')}")
                        print(f"  predict_prices: {detail.get('predict_prices')}")
                    else:
                        print("没有详情数据")
                else:
                    print(f"详情API失败: {detail_response.status_code}")
                    print(f"响应: {detail_response.text}")
            else:
                print("场馆列表为空")
        else:
            print(f"场馆列表API失败: {response.status_code}")
    except Exception as e:
        print(f"测试异常: {e}")

if __name__ == "__main__":
    test_detail_api() 