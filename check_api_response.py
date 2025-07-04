#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查API返回的predict_prices字段内容
"""

import requests
import json

def check_api_response():
    """检查WoowTennis网球俱乐部(国贸店)的API返回内容"""
    print("🔍 检查API返回内容...")
    
    try:
        # 获取WoowTennis网球俱乐部(国贸店)的详情 - 使用正确ID 9
        r = requests.get('http://localhost:8000/api/details/9/preview')
        data = r.json()
        
        print("=== API返回的完整内容 ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        print("\n=== 关键字段检查 ===")
        if 'detail' in data and data['detail']:
            detail = data['detail']
            print(f"predict_prices字段类型: {type(detail.get('predict_prices'))}")
            print(f"predict_prices字段内容: {detail.get('predict_prices')}")
            print(f"bing_prices字段内容: {detail.get('bing_prices')}")
            print(f"merged_prices字段内容: {detail.get('merged_prices')}")
            print(f"prices字段内容: {detail.get('prices')}")
            
            # 尝试解析predict_prices
            pred = detail.get('predict_prices')
            if pred:
                if isinstance(pred, str):
                    try:
                        parsed = json.loads(pred)
                        print(f"解析后的predict_prices: {parsed}")
                    except:
                        print("predict_prices字符串解析失败")
                else:
                    print(f"predict_prices不是字符串: {pred}")
            else:
                print("❌ predict_prices字段为空或None")
        else:
            print("API返回中没有detail字段")
            
    except Exception as e:
        print(f"检查API时出错: {e}")

if __name__ == "__main__":
    check_api_response() 