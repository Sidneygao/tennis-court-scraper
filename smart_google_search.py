#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能Google搜索脚本
使用更好的反检测策略访问Google
"""

import requests
import time
import random
from urllib.parse import quote
import json

class SmartGoogleSearcher:
    def __init__(self):
        self.proxies = {
            "http": "socks5h://127.0.0.1:7890",
            "https": "socks5h://127.0.0.1:7890"
        }
        
        # 多个User-Agent轮换
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # 会话保持
        self.session = requests.Session()
        self.session.proxies = self.proxies
        
    def get_random_headers(self):
        """获取随机请求头"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
    
    def search_google(self, query, max_retries=3):
        """搜索Google"""
        print(f"🔍 搜索Google: {query}")
        
        for attempt in range(max_retries):
            try:
                # 随机延迟
                time.sleep(random.uniform(1, 3))
                
                # 构建搜索URL
                encoded_query = quote(query)
                search_url = f"https://www.google.com/search?q={encoded_query}&hl=en&num=10"
                
                # 获取随机请求头
                headers = self.get_random_headers()
                
                print(f"   尝试 {attempt + 1}/{max_retries}...")
                
                # 发送请求
                response = self.session.get(
                    search_url, 
                    headers=headers, 
                    timeout=15,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    print(f"✅ 搜索成功!")
                    print(f"   状态码: {response.status_code}")
                    print(f"   内容长度: {len(response.text)} 字符")
                    
                    # 分析搜索结果
                    return self.analyze_search_results(response.text, query)
                else:
                    print(f"❌ 状态码异常: {response.status_code}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"❌ 连接错误 (尝试 {attempt + 1}): {e}")
                if "ConnectionResetError" in str(e):
                    print("   💡 Google检测到代理，尝试更换策略...")
                    time.sleep(random.uniform(2, 5))  # 更长延迟
            except requests.exceptions.Timeout as e:
                print(f"❌ 超时错误 (尝试 {attempt + 1}): {e}")
            except Exception as e:
                print(f"❌ 未知错误 (尝试 {attempt + 1}): {e}")
            
            # 重试前等待
            if attempt < max_retries - 1:
                wait_time = random.uniform(3, 8)
                print(f"   等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        
        print(f"❌ 所有尝试都失败了")
        return None
    
    def analyze_search_results(self, html_content, query):
        """分析搜索结果"""
        print(f"\n📊 分析搜索结果...")
        
        # 检查是否包含搜索关键词
        query_keywords = query.lower().split()
        found_keywords = []
        for keyword in query_keywords:
            if keyword in html_content.lower():
                found_keywords.append(keyword)
        
        print(f"   关键词匹配: {len(found_keywords)}/{len(query_keywords)}")
        if found_keywords:
            print(f"   匹配的关键词: {', '.join(found_keywords)}")
        
        # 检查价格信息
        price_keywords = ["价格", "收费", "元", "￥", "price", "cost", "RMB", "¥", "hour", "小时"]
        price_info = []
        
        # 简单的价格信息提取
        lines = html_content.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in price_keywords):
                # 清理HTML标签
                clean_line = self.clean_html(line)
                if clean_line and len(clean_line) > 10:
                    price_info.append(clean_line[:200])
                    if len(price_info) >= 5:  # 最多显示5个
                        break
        
        if price_info:
            print(f"   ✅ 发现价格相关信息 ({len(price_info)} 条):")
            for i, info in enumerate(price_info, 1):
                print(f"      {i}. {info}")
        else:
            print(f"   ⚠️  未发现明显的价格信息")
        
        # 检查是否被重定向到验证页面
        if "recaptcha" in html_content.lower() or "verify" in html_content.lower():
            print(f"   ⚠️  可能被重定向到验证页面")
        
        return {
            "success": True,
            "content_length": len(html_content),
            "keyword_match": len(found_keywords),
            "price_info_count": len(price_info),
            "price_info": price_info,
            "has_recaptcha": "recaptcha" in html_content.lower()
        }
    
    def clean_html(self, text):
        """简单清理HTML标签"""
        import re
        # 移除HTML标签
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # 移除多余空白
        text = ' '.join(text.split())
        return text
    
    def test_bing_search(self, query):
        """测试Bing搜索作为对比"""
        print(f"\n🔍 对比测试Bing搜索: {query}")
        
        try:
            encoded_query = quote(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}"
            
            headers = self.get_random_headers()
            
            response = self.session.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Bing搜索成功!")
                print(f"   状态码: {response.status_code}")
                print(f"   内容长度: {len(response.text)} 字符")
                
                # 分析Bing结果
                return self.analyze_search_results(response.text, query)
            else:
                print(f"❌ Bing搜索失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Bing搜索异常: {e}")
        
        return None

def main():
    """主函数"""
    print("🎾 智能Google搜索工具")
    print("=" * 50)
    print("使用反检测策略访问Google搜索")
    print("=" * 50)
    
    searcher = SmartGoogleSearcher()
    
    # 测试搜索
    test_queries = [
        "朝阳公园网球场 价格 2024",
        "北京网球场价格",
        "tennis court price beijing"
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 测试搜索: {query}")
        print(f"{'='*60}")
        
        # Google搜索
        google_result = searcher.search_google(query)
        results[f"google_{query}"] = google_result
        
        # Bing搜索对比
        bing_result = searcher.test_bing_search(query)
        results[f"bing_{query}"] = bing_result
        
        # 搜索间隔
        time.sleep(random.uniform(2, 5))
    
    # 总结报告
    print(f"\n{'='*60}")
    print("📊 搜索测试总结")
    print(f"{'='*60}")
    
    google_success = sum(1 for key, result in results.items() 
                        if key.startswith("google") and result and result.get("success"))
    bing_success = sum(1 for key, result in results.items() 
                      if key.startswith("bing") and result and result.get("success"))
    
    print(f"Google搜索成功率: {google_success}/{len(test_queries)} ({google_success/len(test_queries)*100:.1f}%)")
    print(f"Bing搜索成功率: {bing_success}/{len(test_queries)} ({bing_success/len(test_queries)*100:.1f}%)")
    
    # 价格信息统计
    total_price_info = 0
    for key, result in results.items():
        if result and result.get("price_info_count"):
            total_price_info += result["price_info_count"]
    
    print(f"发现价格信息总数: {total_price_info}")
    
    # 建议
    print(f"\n💡 建议:")
    if google_success > 0:
        print("✅ Google搜索部分成功，可以尝试更多反检测策略")
    else:
        print("❌ Google搜索完全失败，建议使用Bing或其他搜索引擎")
    
    if bing_success > 0:
        print("✅ Bing搜索可用，可以作为备选方案")
    
    if total_price_info > 0:
        print("✅ 发现价格信息，可以用于数据抓取")
    else:
        print("⚠️  未发现价格信息，可能需要调整搜索关键词")

if __name__ == "__main__":
    main() 