#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的Bing搜索测试脚本
使用更精确的搜索策略和HTML解析
"""

import requests
import time
import json
from urllib.parse import quote
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class ImprovedBingSearchTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def search_bing_html(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        使用Bing搜索HTML页面并提取结果
        """
        try:
            # 构建搜索URL - 不使用RSS格式
            encoded_query = quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"
            
            print(f"🔍 搜索查询: {query}")
            print(f"📡 请求URL: {url}")
            
            # 发送请求
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            print(f"✅ 响应状态: {response.status_code}")
            print(f"📄 响应长度: {len(response.text)} 字符")
            
            # 解析HTML结果
            results = self._parse_html_response(response.text)
            
            print(f"📊 提取到 {len(results)} 个结果")
            return results[:max_results]
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {e}")
            return []
        except Exception as e:
            print(f"❌ 解析错误: {e}")
            return []
    
    def _parse_html_response(self, content: str) -> List[Dict]:
        """
        解析Bing HTML响应
        """
        results = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找搜索结果
            search_results = soup.find_all('li', class_='b_algo')
            
            for result in search_results:
                try:
                    # 提取标题和链接
                    title_elem = result.find('h2')
                    if title_elem:
                        link_elem = title_elem.find('a')
                        if link_elem:
                            title = link_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            # 提取描述
                            desc_elem = result.find('p')
                            description = desc_elem.get_text(strip=True) if desc_elem else ''
                            
                            if title and url:
                                result_data = {
                                    'title': title,
                                    'url': url,
                                    'description': description
                                }
                                results.append(result_data)
                                
                except Exception as e:
                    print(f"⚠️ 解析单个结果时出错: {e}")
                    continue
            
            # 如果上面的方法没有找到结果，尝试其他选择器
            if not results:
                print("🔍 尝试备用解析方法...")
                results = self._parse_html_fallback(content)
                
        except Exception as e:
            print(f"❌ HTML解析错误: {e}")
            # 使用正则表达式作为备用方案
            results = self._parse_html_regex(content)
        
        return results
    
    def _parse_html_fallback(self, content: str) -> List[Dict]:
        """
        备用HTML解析方法
        """
        results = []
        
        # 查找所有可能的搜索结果链接
        link_pattern = r'<h2[^>]*><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a></h2>'
        desc_pattern = r'<p[^>]*>([^<]*)</p>'
        
        links = re.findall(link_pattern, content)
        descriptions = re.findall(desc_pattern, content)
        
        for i, (url, title) in enumerate(links):
            if i < len(descriptions):
                description = descriptions[i]
            else:
                description = ""
            
            if title.strip() and url.startswith('http'):
                results.append({
                    'title': title.strip(),
                    'url': url,
                    'description': description.strip()
                })
        
        return results
    
    def _parse_html_regex(self, content: str) -> List[Dict]:
        """
        使用正则表达式解析HTML
        """
        results = []
        
        # 更简单的正则表达式模式
        pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(pattern, content)
        
        for url, title in matches:
            if (url.startswith('http') and 
                len(title.strip()) > 10 and 
                not title.strip().startswith('http')):
                results.append({
                    'title': title.strip(),
                    'url': url,
                    'description': ''
                })
        
        return results[:10]  # 限制结果数量
    
    def test_price_search_improved(self, court_name: str) -> List[Dict]:
        """
        改进的价格搜索测试
        """
        queries = [
            f'"{court_name}" 北京 网球场 价格 收费',
            f'"{court_name}" 北京 网球 费用 价格表',
            f'"{court_name}" 网球场 预约 价格',
            f'"{court_name}" 网球 场地 收费',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*60}")
            
            results = self.search_bing_html(query, max_results=5)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    if result['description']:
                        print(f"     描述: {result['description'][:150]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            # 避免请求过快
            time.sleep(3)
        
        return all_results
    
    def test_contact_search_improved(self, court_name: str) -> List[Dict]:
        """
        改进的联系方式搜索测试
        """
        queries = [
            f'"{court_name}" 北京 网球场 电话 联系方式',
            f'"{court_name}" 网球 预约 电话',
            f'"{court_name}" 网球场 联系 咨询',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*60}")
            
            results = self.search_bing_html(query, max_results=5)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    if result['description']:
                        print(f"     描述: {result['description'][:150]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            time.sleep(3)
        
        return all_results
    
    def test_specific_sources(self, court_name: str) -> List[Dict]:
        """
        测试特定来源的搜索
        """
        sources = [
            f'site:baidu.com "{court_name}" 网球场 价格',
            f'site:zhihu.com "{court_name}" 网球',
            f'site:weibo.com "{court_name}" 网球场',
            f'site:dianping.com "{court_name}" 网球',
        ]
        
        all_results = []
        
        for query in sources:
            print(f"\n{'='*60}")
            print(f"🔍 特定来源查询: {query}")
            print(f"{'='*60}")
            
            results = self.search_bing_html(query, max_results=3)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    if result['description']:
                        print(f"     描述: {result['description'][:150]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            time.sleep(3)
        
        return all_results

def main():
    """
    主测试函数
    """
    print("🎾 改进的Bing搜索测试工具")
    print("=" * 60)
    
    tester = ImprovedBingSearchTester()
    
    # 测试场馆列表
    test_courts = [
        "朝阳公园网球场",
        "金地网球",
        "嘉里中心网球场"
    ]
    
    for court in test_courts:
        print(f"\n{'🚀'*25} 测试场馆: {court} {'🚀'*25}")
        
        # 测试特定来源搜索
        print(f"\n🎯 特定来源搜索测试:")
        source_results = tester.test_specific_sources(court)
        
        # 测试改进的价格搜索
        print(f"\n💰 改进价格搜索测试:")
        price_results = tester.test_price_search_improved(court)
        
        # 测试改进的联系方式搜索
        print(f"\n📞 改进联系方式搜索测试:")
        contact_results = tester.test_contact_search_improved(court)
        
        # 保存结果
        results = {
            'court_name': court,
            'source_results': source_results,
            'price_results': price_results,
            'contact_results': contact_results,
            'total_results': len(source_results) + len(price_results) + len(contact_results)
        }
        
        # 保存到文件
        filename = f"bing_improved_test_{court.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {filename}")
        print(f"📊 总计找到 {results['total_results']} 个结果")
        
        print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main() 