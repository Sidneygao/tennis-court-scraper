#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理诊断脚本
检查CLASH代理状态和Python代理配置
"""

import requests
import socket
import time
from urllib.parse import quote

def test_local_proxy_connection():
    """测试本地代理端口连接"""
    print("🔍 测试本地代理端口连接...")
    print("=" * 50)
    
    proxy_host = "127.0.0.1"
    proxy_ports = [1086, 1087, 7890, 7891]  # 常见CLASH端口
    
    for port in proxy_ports:
        print(f"\n🌐 测试端口 {proxy_host}:{port}")
        try:
            # 测试TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((proxy_host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口 {port} 可连接")
                
                # 尝试HTTP代理
                try:
                    http_proxies = {
                        "http": f"http://{proxy_host}:{port}",
                        "https": f"http://{proxy_host}:{port}"
                    }
                    response = requests.get("http://httpbin.org/ip", proxies=http_proxies, timeout=5)
                    print(f"   ✅ HTTP代理工作正常")
                except Exception as e:
                    print(f"   ❌ HTTP代理测试失败: {e}")
                
                # 尝试SOCKS5代理
                try:
                    socks5_proxies = {
                        "http": f"socks5h://{proxy_host}:{port}",
                        "https": f"socks5h://{proxy_host}:{port}"
                    }
                    response = requests.get("http://httpbin.org/ip", proxies=socks5_proxies, timeout=5)
                    print(f"   ✅ SOCKS5代理工作正常")
                except Exception as e:
                    print(f"   ❌ SOCKS5代理测试失败: {e}")
                    
            else:
                print(f"❌ 端口 {port} 不可连接")
                
        except Exception as e:
            print(f"❌ 测试端口 {port} 时出错: {e}")

def test_different_proxy_formats():
    """测试不同的代理格式"""
    print("\n🔍 测试不同的代理格式...")
    print("=" * 50)
    
    proxy_host = "127.0.0.1"
    proxy_port = "1086"
    
    proxy_formats = [
        {
            "name": "SOCKS5 (socks5h://)",
            "proxies": {
                "http": f"socks5h://{proxy_host}:{proxy_port}",
                "https": f"socks5h://{proxy_host}:{proxy_port}"
            }
        },
        {
            "name": "SOCKS5 (socks5://)",
            "proxies": {
                "http": f"socks5://{proxy_host}:{proxy_port}",
                "https": f"socks5://{proxy_host}:{proxy_port}"
            }
        },
        {
            "name": "HTTP代理",
            "proxies": {
                "http": f"http://{proxy_host}:{proxy_port}",
                "https": f"http://{proxy_host}:{proxy_port}"
            }
        },
        {
            "name": "HTTPS代理",
            "proxies": {
                "http": f"https://{proxy_host}:{proxy_port}",
                "https": f"https://{proxy_host}:{proxy_port}"
            }
        }
    ]
    
    test_url = "http://httpbin.org/ip"  # 简单的IP检测服务
    
    for format_config in proxy_formats:
        print(f"\n🌐 测试 {format_config['name']}...")
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=format_config['proxies'], timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)
            
            print(f"✅ 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            print(f"   响应内容: {response.text[:200]}")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")

def test_google_with_different_headers():
    """使用不同请求头测试Google"""
    print("\n🔍 使用不同请求头测试Google...")
    print("=" * 50)
    
    proxies = {
        "http": "socks5h://127.0.0.1:1086",
        "https": "socks5h://127.0.0.1:1086"
    }
    
    headers_list = [
        {
            "name": "Chrome浏览器",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        },
        {
            "name": "简单请求",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        },
        {
            "name": "无请求头",
            "headers": {}
        }
    ]
    
    test_url = "https://www.google.com"
    
    for header_config in headers_list:
        print(f"\n🌐 测试 {header_config['name']}...")
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, headers=header_config['headers'], timeout=10)
            end_time = time.time()
            
            status_code = response.status_code
            response_time = round((end_time - start_time) * 1000, 2)
            content_length = len(response.text)
            
            print(f"✅ 连接成功!")
            print(f"   状态码: {status_code}")
            print(f"   响应时间: {response_time}ms")
            print(f"   内容长度: {content_length} 字符")
            
            if "google" in response.text.lower():
                print(f"   ✅ 内容验证: 包含Google相关内容")
            else:
                print(f"   ⚠️  内容验证: 未检测到Google内容")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")

def check_clash_status():
    """检查CLASH状态"""
    print("\n🔍 检查CLASH状态...")
    print("=" * 50)
    
    print("请确认以下CLASH设置:")
    print("1. CLASH客户端是否正在运行?")
    print("2. 代理模式是否为 'RULES' 或 'GLOBAL'?")
    print("3. 端口1086是否在CLASH的代理设置中启用?")
    print("4. 是否有可用的代理节点?")
    print("5. 浏览器设置为127.0.0.1:1086代理后能否访问Google?")
    
    print("\n💡 可能的解决方案:")
    print("1. 重启CLASH客户端")
    print("2. 检查CLASH配置文件中的代理端口设置")
    print("3. 尝试使用其他端口(如7890, 7891)")
    print("4. 检查防火墙是否阻止了Python进程")
    print("5. 尝试使用HTTP代理而不是SOCKS5代理")

def main():
    """主函数"""
    print("🎾 代理诊断工具")
    print("=" * 50)
    print("诊断CLASH代理和Python代理配置问题")
    print("=" * 50)
    
    # 测试本地代理端口连接
    test_local_proxy_connection()
    
    # 测试不同的代理格式
    test_different_proxy_formats()
    
    # 使用不同请求头测试Google
    test_google_with_different_headers()
    
    # 检查CLASH状态
    check_clash_status()
    
    print("\n📊 诊断完成")
    print("=" * 50)
    print("请根据上述测试结果检查CLASH配置")

if __name__ == "__main__":
    main() 