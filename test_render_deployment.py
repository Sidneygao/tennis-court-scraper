#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render部署测试脚本
测试各个API接口是否正常工作
"""

import requests
import json
import time
from urllib.parse import urljoin

# Render部署的URL（请根据实际情况修改）
BASE_URL = "https://tennis-court-scraper.onrender.com"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """测试单个端点"""
    url = urljoin(BASE_URL, endpoint)
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"URL: {url}")
    print(f"方法: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.request(method, url, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        if response.status_code == 200:
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    if isinstance(data, list):
                        print(f"返回数据: 列表，长度 {len(data)}")
                        if len(data) > 0:
                            print(f"第一条数据示例: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                    else:
                        print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                else:
                    print(f"返回数据: HTML内容，长度 {len(response.text)}")
                    if len(response.text) > 200:
                        print(f"内容预览: {response.text[:200]}...")
                    else:
                        print(f"内容: {response.text}")
            except Exception as e:
                print(f"解析响应数据失败: {e}")
                print(f"原始响应: {response.text[:500]}...")
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return response.status_code == 200

def main():
    """主测试函数"""
    print("开始测试Render部署...")
    print(f"基础URL: {BASE_URL}")
    
    # 测试列表
    tests = [
        ("/", "GET", None, "首页"),
        ("/api/health", "GET", None, "健康检查"),
        ("/api/info", "GET", None, "应用信息"),
        ("/api/courts/areas/list", "GET", None, "区域列表"),
        ("/api/courts/", "GET", None, "场馆列表（全部）"),
        ("/api/courts/?area=guomao", "GET", None, "场馆列表（国贸区域）"),
        ("/api/courts/stats/summary", "GET", None, "场馆统计"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for endpoint, method, data, description in tests:
        if test_endpoint(endpoint, method, data, description):
            success_count += 1
        time.sleep(1)  # 避免请求过于频繁
    
    print(f"\n{'='*60}")
    print(f"测试完成: {success_count}/{total_count} 个接口正常")
    
    if success_count == total_count:
        print("✅ 所有接口测试通过")
    else:
        print("❌ 部分接口存在问题，请检查Render部署配置")

if __name__ == "__main__":
    main() 