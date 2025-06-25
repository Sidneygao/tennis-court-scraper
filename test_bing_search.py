#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing搜索测试脚本
用于小范围测试关键字搜索方法的有效性
"""

import requests
import time
import json
from urllib.parse import quote
import re
from typing import List, Dict, Optional

class BingSearchTester:
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
        
    def search_bing(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        使用Bing搜索并提取结果
        """
        try:
            # 构建搜索URL
            encoded_query = quote(query)
            url = f"https://www.bing.com/search?q={encoded_query}&format=rss"
            
            print(f"🔍 搜索查询: {query}")
            print(f"📡 请求URL: {url}")
            
            # 发送请求
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            print(f"✅ 响应状态: {response.status_code}")
            print(f"📄 响应长度: {len(response.text)} 字符")
            
            # 解析RSS结果
            results = self._parse_rss_response(response.text)
            
            print(f"📊 提取到 {len(results)} 个结果")
            return results[:max_results]
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {e}")
            return []
        except Exception as e:
            print(f"❌ 解析错误: {e}")
            return []
    
    def _parse_rss_response(self, content: str) -> List[Dict]:
        """
        解析Bing RSS响应
        """
        results = []
        
        # 简单的RSS解析
        item_pattern = r'<item>(.*?)</item>'
        title_pattern = r'<title>(.*?)</title>'
        link_pattern = r'<link>(.*?)</link>'
        description_pattern = r'<description>(.*?)</description>'
        
        items = re.findall(item_pattern, content, re.DOTALL)
        
        for item in items:
            title_match = re.search(title_pattern, item, re.DOTALL)
            link_match = re.search(link_pattern, item, re.DOTALL)
            desc_match = re.search(description_pattern, item, re.DOTALL)
            
            if title_match and link_match:
                result = {
                    'title': self._clean_text(title_match.group(1)),
                    'url': self._clean_text(link_match.group(1)),
                    'description': self._clean_text(desc_match.group(1)) if desc_match else ''
                }
                results.append(result)
        
        return results
    
    def _clean_text(self, text: str) -> str:
        """
        清理HTML标签和特殊字符
        """
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 解码HTML实体
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def test_price_search(self, court_name: str) -> List[Dict]:
        """
        测试价格搜索
        """
        queries = [
            f'"{court_name}" 网球场 价格',
            f'"{court_name}" 网球 收费',
            f'"{court_name}" 网球场 费用',
            f'"{court_name}" 网球 价格表',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*50}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*50}")
            
            results = self.search_bing(query, max_results=5)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    print(f"     描述: {result['description'][:100]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            # 避免请求过快
            time.sleep(2)
        
        return all_results
    
    def test_contact_search(self, court_name: str) -> List[Dict]:
        """
        测试联系方式搜索
        """
        queries = [
            f'"{court_name}" 网球场 电话',
            f'"{court_name}" 网球 联系方式',
            f'"{court_name}" 网球场 联系',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*50}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*50}")
            
            results = self.search_bing(query, max_results=5)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    print(f"     描述: {result['description'][:100]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            time.sleep(2)
        
        return all_results

def main():
    """
    主测试函数
    """
    print("🎾 Bing搜索测试工具")
    print("=" * 50)
    
    tester = BingSearchTester()
    
    # 测试场馆列表
    test_courts = [
        "朝阳公园网球场",
        "金地网球",
        "嘉里中心网球场"
    ]
    
    for court in test_courts:
        print(f"\n{'🚀'*20} 测试场馆: {court} {'🚀'*20}")
        
        # 测试价格搜索
        print(f"\n💰 价格搜索测试:")
        price_results = tester.test_price_search(court)
        
        # 测试联系方式搜索
        print(f"\n📞 联系方式搜索测试:")
        contact_results = tester.test_contact_search(court)
        
        # 保存结果
        results = {
            'court_name': court,
            'price_results': price_results,
            'contact_results': contact_results,
            'total_results': len(price_results) + len(contact_results)
        }
        
        # 保存到文件
        filename = f"bing_test_{court.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {filename}")
        print(f"📊 总计找到 {results['total_results']} 个结果")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main() 