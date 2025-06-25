#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Monica AI 风格关键词搜索测试
支持Google搜索，抓取搜索结果快照和前5个结果页面
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin, urlparse
import random
from datetime import datetime
import os

class GoogleMonicaAISearch:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # 价格提取正则表达式
        self.price_patterns = [
            r'(\d+)\s*元/?小时',
            r'(\d+)\s*元/?场',
            r'价格[：:]\s*(\d+)\s*元',
            r'收费[：:]\s*(\d+)\s*元',
            r'平日价[：:]\s*(\d+)\s*元',
            r'周末价[：:]\s*(\d+)\s*元',
            r'(\d+)\s*-\s*(\d+)\s*元',
            r'(\d+)\s*到\s*(\d+)\s*元',
            r'￥(\d+)',
            r'(\d+)\s*块',
            r'(\d+)\s*元起',
            r'(\d+)\s*元/人',
            r'(\d+)\s*元/次'
        ]
    
    def search_google(self, keyword, max_results=5):
        """Google搜索，返回搜索结果"""
        print(f"🔍 Google搜索: {keyword}")
        
        # 构建Google搜索URL
        search_url = f"https://www.google.com/search?q={quote(keyword)}&num={max_results}&hl=zh-CN"
        
        try:
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            print(f"✅ Google搜索成功，状态码: {response.status_code}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Google搜索失败: {e}")
            return None
    
    def parse_google_results(self, html_content):
        """解析Google搜索结果"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 查找搜索结果
        search_results = soup.find_all('div', class_='g')
        
        for result in search_results[:5]:  # 只取前5个结果
            try:
                # 提取标题
                title_elem = result.find('h3')
                title = title_elem.get_text().strip() if title_elem else "无标题"
                
                # 提取链接
                link_elem = result.find('a')
                url = link_elem.get('href') if link_elem else ""
                
                # 提取摘要
                snippet_elem = result.find('div', class_='VwiC3b')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                if title and url and url.startswith('http'):
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                    
            except Exception as e:
                print(f"⚠️ 解析搜索结果出错: {e}")
                continue
        
        return results
    
    def extract_prices_from_text(self, text):
        """从文本中提取价格信息"""
        prices = []
        
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 处理价格范围
                    if len(match) == 2:
                        prices.append(f"{match[0]}-{match[1]}元")
                    else:
                        prices.append(f"{match[0]}元")
                else:
                    prices.append(f"{match}元")
        
        return list(set(prices))  # 去重
    
    def fetch_page_content(self, url):
        """获取页面内容"""
        try:
            # 添加随机延迟
            time.sleep(random.uniform(1, 2))
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 设置编码
            response.encoding = response.apparent_encoding
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取页面失败 {url}: {e}")
            return None
    
    def analyze_page_content(self, url, content):
        """分析页面内容，提取价格信息"""
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 提取页面文本
        text = soup.get_text()
        
        # 提取价格
        prices = self.extract_prices_from_text(text)
        
        # 提取包含价格的上下文
        price_contexts = []
        for pattern in self.price_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                price_contexts.append(context)
        
        return {
            'prices': prices,
            'contexts': price_contexts[:5]  # 只取前5个上下文
        }
    
    def search_and_extract(self, keyword):
        """执行完整的搜索和提取流程"""
        print(f"\n🤖 Google Monica AI 风格搜索")
        print(f"🔍 关键词: {keyword}")
        print("=" * 60)
        
        # 1. Google搜索
        search_html = self.search_google(keyword)
        if not search_html:
            return None
        
        # 2. 解析搜索结果
        search_results = self.parse_google_results(search_html)
        print(f"📊 找到 {len(search_results)} 个搜索结果")
        
        # 3. 分析每个结果页面
        detailed_results = []
        
        for i, result in enumerate(search_results, 1):
            print(f"\n📄 分析第 {i} 个结果: {result['title']}")
            print(f"🔗 URL: {result['url']}")
            
            # 获取页面内容
            page_content = self.fetch_page_content(result['url'])
            
            # 分析页面内容
            analysis = self.analyze_page_content(result['url'], page_content)
            
            detailed_result = {
                'rank': i,
                'title': result['title'],
                'url': result['url'],
                'snippet': result['snippet'],
                'prices': analysis['prices'],
                'price_contexts': analysis['contexts']
            }
            
            detailed_results.append(detailed_result)
            
            print(f"💰 提取到价格: {analysis['prices']}")
        
        # 4. 汇总结果
        all_prices = []
        for result in detailed_results:
            all_prices.extend(result['prices'])
        
        summary = {
            'keyword': keyword,
            'search_time': datetime.now().isoformat(),
            'total_results': len(detailed_results),
            'total_prices_found': len(all_prices),
            'unique_prices': list(set(all_prices)),
            'detailed_results': detailed_results
        }
        
        return summary

def main():
    """主函数"""
    searcher = GoogleMonicaAISearch()
    
    # 测试关键词
    test_keywords = [
        "朝阳公园网球场 价格 2024",
        "金地网球 价格 2024",
        "嘉里中心网球场 价格 2024"
    ]
    
    all_results = []
    
    for keyword in test_keywords:
        print(f"\n{'='*80}")
        result = searcher.search_and_extract(keyword)
        
        if result:
            all_results.append(result)
            
            # 保存单个关键词结果
            filename = f"google_monica_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {filename}")
    
    # 保存汇总结果
    summary_filename = f"google_monica_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 测试完成！汇总结果已保存到: {summary_filename}")
    
    # 打印汇总统计
    print(f"\n📊 汇总统计:")
    for result in all_results:
        print(f"关键词: {result['keyword']}")
        print(f"  搜索结果: {result['total_results']} 个")
        print(f"  找到价格: {result['total_prices_found']} 个")
        print(f"  唯一价格: {result['unique_prices']}")
        print()

if __name__ == "__main__":
    main() 