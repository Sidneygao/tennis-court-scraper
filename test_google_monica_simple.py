#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 Google Monica AI 关键词搜索测试
支持Google、Bing、DuckDuckGo等多个搜索引擎
配置Clash代理支持
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import random

def test_google_monica_search(keyword):
    """测试Google Monica AI风格的关键词搜索"""
    print(f"🤖 Google Monica AI 风格搜索测试")
    print(f"🔍 关键词: {keyword}")
    print("=" * 60)
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Clash代理配置 - 端口1086
    proxies = {
        "http": "socks5h://127.0.0.1:1086",
        "https": "socks5h://127.0.0.1:1086"
    }
    
    print(f"🔧 使用Clash代理: socks5h://127.0.0.1:1086")
    
    # 价格提取正则表达式
    price_patterns = [
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
    
    def extract_prices(text):
        """从文本中提取价格"""
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        prices.append(f"{match[0]}-{match[1]}元")
                    else:
                        prices.append(f"{match[0]}元")
                else:
                    prices.append(f"{match}元")
        return list(set(prices))
    
    # 搜索引擎列表
    search_engines = [
        {
            'name': 'Google',
            'url': f'https://www.google.com/search?q={quote(keyword)}&num=5&hl=zh-CN',
            'parser': 'google'
        },
        {
            'name': 'Bing',
            'url': f'https://www.bing.com/search?q={quote(keyword)}&count=5',
            'parser': 'bing'
        },
        {
            'name': 'DuckDuckGo',
            'url': f'https://duckduckgo.com/html/?q={quote(keyword)}',
            'parser': 'duckduckgo'
        }
    ]
    
    all_results = []
    
    for engine in search_engines:
        print(f"\n🔍 尝试 {engine['name']} 搜索...")
        
        try:
            # 添加延迟
            time.sleep(random.uniform(2, 4))
            
            # 使用代理发送请求
            response = requests.get(engine['url'], headers=headers, proxies=proxies, timeout=15)
            response.raise_for_status()
            
            print(f"✅ {engine['name']} 搜索成功")
            
            # 解析搜索结果
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if engine['parser'] == 'google':
                # Google搜索结果解析
                results = soup.find_all('div', class_='g')
                for i, result in enumerate(results[:5], 1):
                    try:
                        title_elem = result.find('h3')
                        title = title_elem.get_text().strip() if title_elem else "无标题"
                        
                        link_elem = result.find('a')
                        url = link_elem.get('href') if link_elem else ""
                        
                        snippet_elem = result.find('div', class_='VwiC3b')
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        if title and url and url.startswith('http'):
                            # 提取价格
                            snippet_prices = extract_prices(snippet)
                            
                            all_results.append({
                                'engine': engine['name'],
                                'rank': i,
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'prices': snippet_prices
                            })
                            
                            print(f"  📄 {i}. {title}")
                            print(f"     💰 价格: {snippet_prices}")
                            
                    except Exception as e:
                        print(f"  ⚠️ 解析结果出错: {e}")
                        continue
            
            elif engine['parser'] == 'bing':
                # Bing搜索结果解析
                results = soup.find_all('li', class_='b_algo')
                for i, result in enumerate(results[:5], 1):
                    try:
                        title_elem = result.find('h2')
                        title = title_elem.get_text().strip() if title_elem else "无标题"
                        
                        link_elem = result.find('a')
                        url = link_elem.get('href') if link_elem else ""
                        
                        snippet_elem = result.find('p')
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        if title and url:
                            snippet_prices = extract_prices(snippet)
                            
                            all_results.append({
                                'engine': engine['name'],
                                'rank': i,
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'prices': snippet_prices
                            })
                            
                            print(f"  📄 {i}. {title}")
                            print(f"     💰 价格: {snippet_prices}")
                            
                    except Exception as e:
                        print(f"  ⚠️ 解析结果出错: {e}")
                        continue
            
            elif engine['parser'] == 'duckduckgo':
                # DuckDuckGo搜索结果解析
                results = soup.find_all('div', class_='result')
                for i, result in enumerate(results[:5], 1):
                    try:
                        title_elem = result.find('a', class_='result__a')
                        title = title_elem.get_text().strip() if title_elem else "无标题"
                        
                        url = title_elem.get('href') if title_elem else ""
                        
                        snippet_elem = result.find('a', class_='result__snippet')
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        if title and url:
                            snippet_prices = extract_prices(snippet)
                            
                            all_results.append({
                                'engine': engine['name'],
                                'rank': i,
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'prices': snippet_prices
                            })
                            
                            print(f"  📄 {i}. {title}")
                            print(f"     💰 价格: {snippet_prices}")
                            
                    except Exception as e:
                        print(f"  ⚠️ 解析结果出错: {e}")
                        continue
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ {engine['name']} 搜索失败: {e}")
            continue
    
    # 汇总结果
    all_prices = []
    for result in all_results:
        all_prices.extend(result['prices'])
    
    summary = {
        'keyword': keyword,
        'search_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_results': len(all_results),
        'total_prices_found': len(all_prices),
        'unique_prices': list(set(all_prices)),
        'results_by_engine': {},
        'proxy_used': 'socks5h://127.0.0.1:1086'
    }
    
    # 按搜索引擎分组
    for result in all_results:
        engine = result['engine']
        if engine not in summary['results_by_engine']:
            summary['results_by_engine'][engine] = []
        summary['results_by_engine'][engine].append(result)
    
    print(f"\n📊 搜索结果汇总:")
    print(f"  总结果数: {summary['total_results']}")
    print(f"  找到价格: {summary['total_prices_found']} 个")
    print(f"  唯一价格: {summary['unique_prices']}")
    
    return summary

if __name__ == "__main__":
    # 测试关键词
    keyword = "朝阳公园网球场 价格 2024"
    
    result = test_google_monica_search(keyword)
    
    # 保存结果
    filename = f"google_monica_clash_{keyword.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到: {filename}") 