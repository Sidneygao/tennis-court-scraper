#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单检查Render部署状态
"""

import requests

def check_render():
    url = "https://tennis-court-scraper.onrender.com"
    
    print("检查Render部署状态...")
    print(f"URL: {url}")
    
    try:
        # 测试首页
        print("\n测试首页...")
        response = requests.get(url, timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            content = response.text[:500]
            print(f"内容预览: {content}")
            
            if "网球场爬虫" in content:
                print("✅ 首页正常显示")
            elif "FastAPI" in content:
                print("❌ 显示FastAPI默认页面")
            else:
                print("⚠️ 页面内容异常")
        else:
            print(f"❌ 首页请求失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    check_render() 