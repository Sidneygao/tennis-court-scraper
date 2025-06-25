#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_detail_api():
    try:
        # 测试获取完整详情接口
        response = requests.get("http://localhost:8000/api/details/1")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取详情数据")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

if __name__ == "__main__":
    test_detail_api() 