#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def check_detail_format():
    try:
        response = requests.get('http://localhost:8000/api/details/1/preview')
        data = response.json()
        
        print("=== 详情数据格式检查 ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        if data.get('has_detail') and data.get('detail', {}).get('prices'):
            print("\n=== 价格数据 ===")
            prices = data['detail']['prices']
            for price in prices:
                print(f"类型: {price.get('type')}, 价格: {price.get('price')}")
        else:
            print("\n❌ 没有价格数据")
            
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_detail_format() 