#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Clash代理端口配置
"""

import requests
import time

def test_proxy_connection(proxy_type, host, port):
    """测试代理连接"""
    print(f"🔍 测试 {proxy_type} 代理: {host}:{port}")
    
    if proxy_type == "socks5":
        proxies = {
            "http": f"socks5h://{host}:{port}",
            "https": f"socks5h://{host}:{port}"
        }
    else:  # http
        proxies = {
            "http": f"http://{host}:{port}",
            "https": f"http://{host}:{port}"
        }
    
    try:
        # 测试连接Google
        response = requests.get(
            "https://www.google.com", 
            proxies=proxies, 
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        print(f"✅ {proxy_type} 代理连接成功! 状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ {proxy_type} 代理连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Clash代理端口测试")
    print("=" * 50)
    
    # 常见的Clash端口
    common_ports = [7890, 7891, 1080, 1086, 1087, 8080, 8118]
    
    print("📋 测试常见Clash端口:")
    
    for port in common_ports:
        print(f"\n--- 测试端口 {port} ---")
        
        # 测试SOCKS5
        socks5_ok = test_proxy_connection("socks5", "127.0.0.1", port)
        
        # 测试HTTP
        http_ok = test_proxy_connection("http", "127.0.0.1", port)
        
        if socks5_ok or http_ok:
            print(f"🎉 端口 {port} 可用!")
            if socks5_ok:
                print(f"   SOCKS5: socks5h://127.0.0.1:{port}")
            if http_ok:
                print(f"   HTTP: http://127.0.0.1:{port}")
            break
    
    print("\n💡 如果以上端口都不可用，请检查:")
    print("   1. Clash是否正在运行")
    print("   2. 查看Clash设置中的代理端口")
    print("   3. 确认Clash模式是否为'全局模式'或'规则模式'")

if __name__ == "__main__":
    main() 