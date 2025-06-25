#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google代理连接测试脚本 (端口7890)
测试CLASH代理(127.0.0.1:7890)是否能正常访问Google
"""

import requests
import time
from urllib.parse import quote

def test_google_with_port_7890():
    """使用端口7890测试Google连接"""
    print("🔍 使用端口7890测试Google代理连接...")
    print("=" * 50)
    
    # 代理配置 - 使用端口7890
    proxies = {
        "http": "socks5h://127.0.0.1:7890",
        "https": "socks5h://127.0.0.1:7890"
    }
    
    # 测试目标
    test_urls = [
        "https://www.google.com",
        "https://www.google.com/search?q=test",
        "https://www.bing.com",
        "https://www.duckduckgo.com"
    ]
    
    results = {}
    
    for url in test_urls:
        print(f"\n🌐 测试URL: {url}")
        try:
            start_time = time.time()
            response = requests.get(url, proxies=proxies, timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)  # 毫秒
            content_length = len(response.text)
            
            print(f"✅ 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            print(f"   内容长度: {content_length} 字符")
            
            # 检查内容是否包含预期关键词
            if "google" in url.lower():
                if "google" in response.text.lower():
                    print(f"   ✅ 内容验证: 包含Google相关内容")
                else:
                    print(f"   ⚠️  内容验证: 未检测到Google内容")
            elif "bing" in url.lower():
                if "bing" in response.text.lower():
                    print(f"   ✅ 内容验证: 包含Bing相关内容")
                else:
                    print(f"   ⚠️  内容验证: 未检测到Bing内容")
            
            results[url] = {
                "status": "success",
                "status_code": status_code,
                "response_time": response_time,
                "content_length": content_length
            }
            
        except requests.exceptions.ProxyError as e:
            print(f"❌ 代理连接失败: {e}")
            results[url] = {"status": "proxy_error", "error": str(e)}
        except requests.exceptions.Timeout as e:
            print(f"❌ 连接超时: {e}")
            results[url] = {"status": "timeout", "error": str(e)}
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            results[url] = {"status": "connection_error", "error": str(e)}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            results[url] = {"status": "unknown_error", "error": str(e)}
    
    return results

def test_google_search_7890():
    """使用端口7890测试Google搜索功能"""
    print("\n🔍 使用端口7890测试Google搜索功能...")
    print("=" * 50)
    
    proxies = {
        "http": "socks5h://127.0.0.1:7890",
        "https": "socks5h://127.0.0.1:7890"
    }
    
    # 测试搜索关键词
    search_query = "朝阳公园网球场 价格 2024"
    encoded_query = quote(search_query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    print(f"🔍 搜索关键词: {search_query}")
    print(f"🌐 搜索URL: {search_url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        start_time = time.time()
        response = requests.get(search_url, proxies=proxies, headers=headers, timeout=15)
        end_time = time.time()
        
        status_code = response.status_code
        response_time = round((end_time - start_time) * 1000, 2)
        content_length = len(response.text)
        
        print(f"✅ 搜索成功!")
        print(f"   状态码: {status_code}")
        print(f"   响应时间: {response_time}ms")
        print(f"   内容长度: {content_length} 字符")
        
        # 检查搜索结果
        if "朝阳公园" in response.text or "网球场" in response.text:
            print(f"   ✅ 搜索结果验证: 包含相关关键词")
        else:
            print(f"   ⚠️  搜索结果验证: 未检测到相关关键词")
        
        # 检查是否有价格相关信息
        price_keywords = ["价格", "收费", "元", "￥", "price", "cost", "RMB", "¥"]
        found_price_info = any(keyword in response.text for keyword in price_keywords)
        
        if found_price_info:
            print(f"   ✅ 价格信息: 检测到价格相关内容")
            # 提取价格信息片段
            price_snippets = []
            lines = response.text.split('\n')
            for line in lines:
                if any(keyword in line for keyword in price_keywords):
                    price_snippets.append(line.strip()[:100])
                    if len(price_snippets) >= 3:  # 只显示前3个
                        break
            if price_snippets:
                print(f"   📝 价格信息片段:")
                for i, snippet in enumerate(price_snippets, 1):
                    print(f"      {i}. {snippet}")
        else:
            print(f"   ⚠️  价格信息: 未检测到价格相关内容")
        
        return {
            "status": "success",
            "status_code": status_code,
            "response_time": response_time,
            "content_length": content_length,
            "has_price_info": found_price_info
        }
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return {"status": "error", "error": str(e)}

def test_alternative_proxies_7890():
    """测试端口7890的其他代理协议"""
    print("\n🔍 测试端口7890的其他代理协议...")
    print("=" * 50)
    
    proxy_configs = [
        {
            "name": "SOCKS5代理 (socks5h://)",
            "proxies": {
                "http": "socks5h://127.0.0.1:7890",
                "https": "socks5h://127.0.0.1:7890"
            }
        },
        {
            "name": "SOCKS5代理 (socks5://)",
            "proxies": {
                "http": "socks5://127.0.0.1:7890",
                "https": "socks5://127.0.0.1:7890"
            }
        },
        {
            "name": "HTTP代理",
            "proxies": {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890"
            }
        }
    ]
    
    test_url = "https://www.google.com"
    results = {}
    
    for config in proxy_configs:
        print(f"\n🌐 测试 {config['name']}...")
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=config['proxies'], timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"✅ {config['name']} 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            
            results[config['name']] = {
                "status": "success",
                "status_code": status_code,
                "response_time": response_time
            }
            
        except Exception as e:
            print(f"❌ {config['name']} 连接失败: {e}")
            results[config['name']] = {"status": "error", "error": str(e)}
    
    return results

def main():
    """主函数"""
    print("🎾 Google代理连接测试工具 (端口7890)")
    print("=" * 50)
    print("测试CLASH代理(127.0.0.1:7890)是否能正常访问Google")
    print("=" * 50)
    
    # 测试基本连接
    basic_results = test_google_with_port_7890()
    
    # 测试搜索功能
    search_results = test_google_search_7890()
    
    # 测试其他代理协议
    proxy_results = test_alternative_proxies_7890()
    
    # 总结报告
    print("\n📊 测试总结报告")
    print("=" * 50)
    
    # 基本连接成功率
    success_count = sum(1 for result in basic_results.values() if result.get("status") == "success")
    total_count = len(basic_results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"🌐 基本连接测试: {success_count}/{total_count} 成功 ({success_rate:.1f}%)")
    
    # 搜索功能测试
    if search_results.get("status") == "success":
        print(f"🔍 搜索功能测试: ✅ 成功")
        if search_results.get("has_price_info"):
            print(f"💰 价格信息检测: ✅ 发现价格相关内容")
        else:
            print(f"💰 价格信息检测: ⚠️  未发现价格相关内容")
    else:
        print(f"🔍 搜索功能测试: ❌ 失败")
    
    # 代理协议测试
    proxy_success_count = sum(1 for result in proxy_results.values() if result.get("status") == "success")
    proxy_total_count = len(proxy_results)
    proxy_success_rate = (proxy_success_count / proxy_total_count) * 100 if proxy_total_count > 0 else 0
    
    print(f"🔧 代理协议测试: {proxy_success_count}/{proxy_total_count} 成功 ({proxy_success_rate:.1f}%)")
    
    # 最终建议
    print("\n💡 建议:")
    if success_rate >= 75:
        print("✅ 代理连接正常，可以用于Google搜索和爬虫")
        print("✅ 建议在爬虫脚本中使用端口7890而不是1086")
    elif success_rate >= 50:
        print("⚠️  代理连接部分正常，建议检查CLASH配置")
    else:
        print("❌ 代理连接异常，请检查CLASH是否正常运行")
    
    if search_results.get("status") == "success":
        print("✅ Google搜索功能正常，可以用于价格信息抓取")
    else:
        print("❌ Google搜索功能异常，可能需要调整请求参数")

if __name__ == "__main__":
    main() 