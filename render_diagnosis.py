#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render部署诊断脚本
"""

import requests
import time
import json

def diagnose_render():
    """诊断Render部署问题"""
    url = "https://tennis-court-scraper.onrender.com"
    
    print("🔍 Render部署诊断")
    print(f"目标URL: {url}")
    print("=" * 60)
    
    # 1. 基本连接测试
    print("\n1. 基本连接测试...")
    try:
        response = requests.get(url, timeout=30)
        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {response.elapsed.total_seconds():.2f}秒")
        print(f"   内容类型: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            content = response.text[:500]
            if "网球场爬虫" in content:
                print("   ✅ 首页正常显示")
                return True
            elif "FastAPI" in content:
                print("   ❌ 显示FastAPI默认页面")
                print("   建议: 检查路由配置和模板文件")
            else:
                print("   ⚠️ 页面内容异常")
                print(f"   内容预览: {content}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时")
        print("   可能原因:")
        print("   - Render服务正在冷启动（等待30-60秒）")
        print("   - 服务启动失败")
        print("   - 网络连接问题")
    except requests.exceptions.ConnectionError:
        print("   ❌ 连接错误")
        print("   可能原因:")
        print("   - 服务未启动")
        print("   - 域名配置错误")
        print("   - 网络问题")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 2. 健康检查测试
    print("\n2. 健康检查测试...")
    try:
        response = requests.get(f"{url}/api/health", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   应用名称: {data.get('app_name', 'unknown')}")
            print(f"   版本: {data.get('version', 'unknown')}")
            print("   ✅ 健康检查正常")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
    
    # 3. 应用信息测试
    print("\n3. 应用信息测试...")
    try:
        response = requests.get(f"{url}/api/info", timeout=15)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   应用名称: {data.get('app_name', 'unknown')}")
            print(f"   目标区域数量: {len(data.get('target_areas', {}))}")
            print("   ✅ 应用信息正常")
        else:
            print(f"   ❌ 应用信息失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 应用信息异常: {e}")
    
    # 4. 建议和解决方案
    print("\n" + "=" * 60)
    print("💡 建议和解决方案:")
    print("1. 如果是冷启动问题:")
    print("   - 等待30-60秒后重试")
    print("   - 访问 https://tennis-court-scraper.onrender.com 触发启动")
    
    print("\n2. 如果是部署问题:")
    print("   - 检查Render控制台日志")
    print("   - 确认代码已推送到GitHub")
    print("   - 强制重新部署")
    
    print("\n3. 如果是配置问题:")
    print("   - 检查render.yaml配置")
    print("   - 确认启动命令正确")
    print("   - 检查环境变量设置")
    
    print("\n4. 如果是代码问题:")
    print("   - 检查本地启动是否正常")
    print("   - 查看是否有导入错误")
    print("   - 检查依赖是否完整")
    
    return False

if __name__ == "__main__":
    diagnose_render() 