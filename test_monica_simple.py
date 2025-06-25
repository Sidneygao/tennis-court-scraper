#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 Monica AI 关键词搜索测试
专门测试单个关键词的价格提取效果
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import random

def test_monica_style_search(keyword):
    """测试Monica AI风格的关键词搜索"""
    print(f"🤖 Monica AI 风格搜索测试")
    print(f"🔍 关键词: {keyword}")
    print("=" * 50)
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # 测试搜狗搜索
    print("🔍 测试搜狗搜索...")
    try:
        search_url = f"https://www.sogou.com/web?query={quote(keyword)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取所有文本
            text_content = soup.get_text()
            
            # 提取价格信息
            prices = extract_prices(text_content)
            
            if prices:
                print(f"✅ 找到价格: {prices}")
                
                # 提取价格上下文
                contexts = extract_price_contexts(text_content, prices)
                
                result = {
                    'keyword': keyword,
                    'engine': 'sogou',
                    'prices': prices,
                    'contexts': contexts,
                    'url': search_url,
                    'status': 'success'
                }
            else:
                print("❌ 未找到价格信息")
                result = {
                    'keyword': keyword,
                    'engine': 'sogou',
                    'prices': [],
                    'contexts': [],
                    'url': search_url,
                    'status': 'no_prices'
                }
        else:
            print(f"❌ 搜狗搜索失败: {response.status_code}")
            result = {
                'keyword': keyword,
                'engine': 'sogou',
                'prices': [],
                'contexts': [],
                'url': search_url,
                'status': 'failed'
            }
            
    except Exception as e:
        print(f"❌ 搜狗搜索异常: {e}")
        result = {
            'keyword': keyword,
            'engine': 'sogou',
            'prices': [],
            'contexts': [],
            'url': search_url,
            'status': 'error',
            'error': str(e)
        }
    
    return result

def extract_prices(text):
    """提取价格信息"""
    price_patterns = [
        r'(\d+)[\s\-]*元/?小时?',
        r'(\d+)[\s\-]*元/?场',
        r'(\d+)[\s\-]*元/?次',
        r'(\d+)[\s\-]*元/?人',
        r'价格[：:]\s*(\d+)[\s\-]*元',
        r'收费[：:]\s*(\d+)[\s\-]*元',
        r'平日价[：:]\s*(\d+)[\s\-]*元',
        r'周末价[：:]\s*(\d+)[\s\-]*元',
        r'高峰价[：:]\s*(\d+)[\s\-]*元',
        r'(\d+)[\s\-]*元/?小时?',
        r'(\d+)[\s\-]*元/?场',
    ]
    
    prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        prices.extend(matches)
    
    return list(set(prices))  # 去重

def extract_price_contexts(text, prices):
    """提取价格上下文"""
    contexts = []
    for price in prices:
        try:
            # 在价格前后50个字符范围内查找上下文
            price_pattern = re.compile(rf'.{{0,50}}{price}元?.{{0,50}}')
            matches = price_pattern.findall(text)
            if matches:
                contexts.append({
                    'price': price,
                    'context': matches[0].strip()
                })
        except:
            continue
    return contexts

def main():
    """主函数"""
    # 测试关键词
    test_keywords = [
        "朝阳公园网球场 价格 2024",
        "金地网球 价格 2024",
        "嘉里中心网球场 价格 2024"
    ]
    
    all_results = []
    
    for keyword in test_keywords:
        print(f"\n{'='*60}")
        result = test_monica_style_search(keyword)
        all_results.append(result)
        
        # 打印结果摘要
        if result['status'] == 'success':
            print(f"📊 结果摘要:")
            print(f"  价格数量: {len(result['prices'])}")
            print(f"  价格列表: {result['prices']}")
            if result['contexts']:
                print(f"  价格上下文: {result['contexts'][:2]}")  # 只显示前2个
        
        time.sleep(random.uniform(2, 4))  # 随机延迟
    
    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"monica_simple_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")
    
    # 打印总结
    print(f"\n📈 测试总结:")
    print(f"  测试关键词: {len(test_keywords)} 个")
    print(f"  成功搜索: {len([r for r in all_results if r['status'] == 'success'])} 个")
    print(f"  找到价格: {len([r for r in all_results if r['prices']])} 个")
    
    total_prices = sum(len(r['prices']) for r in all_results)
    print(f"  总价格数: {total_prices} 个")

if __name__ == "__main__":
    main() 