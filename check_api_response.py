#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查API返回的数据结构，确认真实价格字段内容
"""

import requests

def check_api_response():
    """检查API返回的数据"""
    base_url = "http://127.0.0.1:8000"
    # 只查前100个场馆
    for court_id in range(1, 101):
        url = f"{base_url}/api/details/{court_id}"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                prices = data.get('prices', [])
                if prices:
                    print(f"ID: {court_id}  名称: {data.get('name')}  真实价格条数: {len(prices)}")
                    for p in prices:
                        print(f"  {p}")
        except Exception as e:
            print(f"ID: {court_id} 请求失败: {e}")

if __name__ == "__main__":
    check_api_response() 