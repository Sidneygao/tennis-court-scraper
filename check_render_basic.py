#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本检查Render部署
"""

import requests
import time

def basic_check():
    url = "https://tennis-court-scraper.onrender.com"
    
    print("基本检查Render部署...")
    print(f"URL: {url}")
    
    # 测试多个端点
    endpoints = [
        ("/", "首页"),
        ("/api/health", "健康检查"),
        ("/api/info", "应用信息"),
    ]
    
    for endpoint, name in endpoints:
        print(f"\n测试 {name}...")
        try:
            full_url = url + endpoint
            response = requests.get(full_url, timeout=20)
            print(f"  状态码: {response.status_code}")
            print(f"  响应时间: {response.elapsed.total_seconds():.2f}秒")
            
            if response.status_code == 200:
                print(f"  ✅ {name} 正常")
                if endpoint == "/":
                    content = response.text[:200]
                    if "网球场爬虫" in content:
                        print("  ✅ 首页内容正确")
                    else:
                        print(f"  ⚠️ 首页内容: {content}")
            else:
                print(f"  ❌ {name} 失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ {name} 超时")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {name} 连接错误")
        except Exception as e:
            print(f"  ❌ {name} 异常: {e}")
        
        time.sleep(2)  # 等待2秒

if __name__ == "__main__":
    basic_check() 