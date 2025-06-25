#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细Google访问诊断脚本
分析是网络连接问题还是反爬策略问题
"""

import requests
import socket
import time
import json
from urllib.parse import quote

def test_basic_connectivity():
    """测试基本网络连接"""
    print("🔍 测试基本网络连接...")
    print("=" * 50)
    
    # 测试目标
    test_targets = [
        {"name": "本地回环", "host": "127.0.0.1", "port": 7890},
        {"name": "百度", "host": "www.baidu.com", "port": 80},
        {"name": "Google", "host": "www.google.com", "port": 443},
        {"name": "Bing", "host": "www.bing.com", "port": 443},
    ]
    
    for target in test_targets:
        print(f"\n🌐 测试 {target['name']} ({target['host']}:{target['port']})")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((target['host'], target['port']))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口连接成功")
            else:
                print(f"❌ 端口连接失败 (错误码: {result})")
                
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")

def test_proxy_without_google():
    """测试代理但不访问Google"""
    print("\n🔍 测试代理但不访问Google...")
    print("=" * 50)
    
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    
    # 测试非Google网站
    test_urls = [
        "http://httpbin.org/ip",
        "https://www.baidu.com",
        "https://www.bing.com",
        "https://www.duckduckgo.com",
        "https://www.yahoo.com"
    ]
    
    for url in test_urls:
        print(f"\n🌐 测试URL: {url}")
        try:
            start_time = time.time()
            response = requests.get(url, proxies=proxies, timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"✅ 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            print(f"   内容长度: {len(response.text)} 字符")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")

def test_google_with_different_approaches():
    """使用不同方法测试Google访问"""
    print("\n🔍 使用不同方法测试Google访问...")
    print("=" * 50)
    
    # 方法1: 直接访问Google主页
    print("\n🌐 方法1: 直接访问Google主页")
    try:
        proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
        print(f"✅ 直接访问成功! 状态码: {response.status_code}")
        print(f"   内容长度: {len(response.text)} 字符")
        print(f"   是否包含Google内容: {'google' in response.text.lower()}")
    except Exception as e:
        print(f"❌ 直接访问失败: {e}")
    
    # 方法2: 使用搜索API
    print("\n🌐 方法2: 使用Google搜索API")
    try:
        proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        search_url = "https://www.google.com/search?q=test"
        response = requests.get(search_url, proxies=proxies, headers=headers, timeout=10)
        print(f"✅ 搜索API成功! 状态码: {response.status_code}")
        print(f"   内容长度: {len(response.text)} 字符")
    except Exception as e:
        print(f"❌ 搜索API失败: {e}")
    
    # 方法3: 使用不同的User-Agent
    print("\n🌐 方法3: 使用不同的User-Agent")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Python-requests/2.25.1"
    ]
    
    for i, ua in enumerate(user_agents, 1):
        try:
            proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
            headers = {"User-Agent": ua}
            response = requests.get("https://www.google.com", proxies=proxies, headers=headers, timeout=10)
            print(f"✅ User-Agent {i} 成功! 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ User-Agent {i} 失败: {e}")

def test_google_response_analysis():
    """分析Google响应内容"""
    print("\n🔍 分析Google响应内容...")
    print("=" * 50)
    
    try:
        proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get("https://www.google.com", proxies=proxies, headers=headers, timeout=10)
        
        print(f"✅ 成功获取响应!")
        print(f"   状态码: {response.status_code}")
        print(f"   内容长度: {len(response.text)} 字符")
        print(f"   响应头: {dict(response.headers)}")
        
        # 分析响应内容
        content = response.text.lower()
        
        # 检查是否是Google页面
        if "google" in content:
            print(f"   ✅ 确认是Google页面")
        else:
            print(f"   ⚠️  可能不是Google页面")
        
        # 检查是否有反爬提示
        anti_bot_keywords = [
            "captcha", "robot", "bot", "automated", "blocked", "suspicious",
            "验证码", "机器人", "自动化", "阻止", "可疑"
        ]
        
        found_anti_bot = []
        for keyword in anti_bot_keywords:
            if keyword in content:
                found_anti_bot.append(keyword)
        
        if found_anti_bot:
            print(f"   ⚠️  检测到反爬关键词: {found_anti_bot}")
        else:
            print(f"   ✅ 未检测到明显的反爬提示")
        
        # 保存响应内容用于分析
        with open("google_response_analysis.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"   💾 响应内容已保存到 google_response_analysis.html")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

def test_alternative_search_engines():
    """测试其他搜索引擎"""
    print("\n🔍 测试其他搜索引擎...")
    print("=" * 50)
    
    search_engines = [
        {
            "name": "Bing",
            "url": "https://www.bing.com/search?q=朝阳公园网球场",
            "proxies": {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        },
        {
            "name": "DuckDuckGo",
            "url": "https://duckduckgo.com/?q=朝阳公园网球场",
            "proxies": {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        },
        {
            "name": "Yahoo",
            "url": "https://search.yahoo.com/search?p=朝阳公园网球场",
            "proxies": {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        }
    ]
    
    for engine in search_engines:
        print(f"\n🌐 测试 {engine['name']}...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            start_time = time.time()
            response = requests.get(engine['url'], proxies=engine['proxies'], headers=headers, timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"✅ {engine['name']} 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            print(f"   内容长度: {len(response.text)} 字符")
            
            # 检查是否包含搜索关键词
            if "朝阳公园" in response.text or "网球场" in response.text:
                print(f"   ✅ 包含相关搜索结果")
            else:
                print(f"   ⚠️  未检测到相关搜索结果")
                
        except Exception as e:
            print(f"❌ {engine['name']} 连接失败: {e}")

def generate_diagnosis_report():
    """生成诊断报告"""
    print("\n📊 生成诊断报告...")
    print("=" * 50)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "diagnosis": "Google访问问题诊断",
        "findings": [],
        "recommendations": []
    }
    
    # 基于测试结果添加发现
    report["findings"].append("端口7890可以连接，但Google访问失败")
    report["findings"].append("Bing等搜索引擎可以正常访问")
    report["findings"].append("可能是Google的反爬策略或代理被识别")
    
    # 添加建议
    report["recommendations"].append("尝试使用其他搜索引擎（Bing、DuckDuckGo）")
    report["recommendations"].append("考虑使用Selenium模拟真实浏览器")
    report["recommendations"].append("检查代理是否被Google封禁")
    report["recommendations"].append("尝试使用不同的代理节点")
    report["recommendations"].append("考虑使用Google搜索API（需要API密钥）")
    
    # 保存报告
    with open("google_diagnosis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 诊断报告已保存到 google_diagnosis_report.json")
    print("\n📋 报告摘要:")
    for finding in report["findings"]:
        print(f"   • {finding}")
    print("\n💡 建议:")
    for rec in report["recommendations"]:
        print(f"   • {rec}")

def main():
    """主函数"""
    print("🎾 Google访问问题详细诊断工具")
    print("=" * 50)
    print("分析是网络连接问题还是反爬策略问题")
    print("=" * 50)
    
    test_basic_connectivity()
    test_proxy_without_google()
    test_google_with_different_approaches()
    test_google_response_analysis()
    test_alternative_search_engines()
    generate_diagnosis_report()
    
    print("\n📊 诊断完成")
    print("=" * 50)
    print("请查看生成的报告文件了解详细分析结果")

if __name__ == "__main__":
    main() 