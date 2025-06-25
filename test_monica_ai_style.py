#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monica AI 风格关键词搜索测试
模拟Monica AI的智能搜索和价格提取功能
支持多个搜索引擎：搜狗、Bing、DuckDuckGo等
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import random
from datetime import datetime
import os

class MonicaAIStyleSearch:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
            'Cache-Control': 'max-age=0',
        })
        
        # 搜索引擎配置
        self.search_engines = {
            'sogou': {
                'url': 'https://www.sogou.com/web',
                'params': {'query': ''},
                'result_selector': '.vrwrap, .rb',
                'title_selector': 'h3 a, .vr-title a',
                'snippet_selector': '.text, .vr-snippet'
            },
            'bing': {
                'url': 'https://cn.bing.com/search',
                'params': {'q': ''},
                'result_selector': '.b_algo',
                'title_selector': 'h2 a',
                'snippet_selector': '.b_caption p'
            },
            'duckduckgo': {
                'url': 'https://duckduckgo.com/html',
                'params': {'q': ''},
                'result_selector': '.result',
                'title_selector': '.result__title a',
                'snippet_selector': '.result__snippet'
            }
        }
    
    def extract_prices_from_text(self, text):
        """智能价格提取 - 类似Monica AI的文本分析"""
        # 更全面的价格模式
        price_patterns = [
            # 标准价格格式
            r'(\d+)[\s\-]*元/?小时?',
            r'(\d+)[\s\-]*元/?场',
            r'(\d+)[\s\-]*元/?次',
            r'(\d+)[\s\-]*元/?人',
            r'(\d+)[\s\-]*元/?天',
            r'(\d+)[\s\-]*元/?月',
            r'(\d+)[\s\-]*元/?年',
            
            # 带描述的价格
            r'价格[：:]\s*(\d+)[\s\-]*元',
            r'收费[：:]\s*(\d+)[\s\-]*元',
            r'费用[：:]\s*(\d+)[\s\-]*元',
            r'平日价[：:]\s*(\d+)[\s\-]*元',
            r'周末价[：:]\s*(\d+)[\s\-]*元',
            r'高峰价[：:]\s*(\d+)[\s\-]*元',
            r'淡季价[：:]\s*(\d+)[\s\-]*元',
            r'旺季价[：:]\s*(\d+)[\s\-]*元',
            
            # 价格范围
            r'(\d+)[\s\-]*到[\s\-]*(\d+)[\s\-]*元',
            r'(\d+)[\s\-]*-\s*(\d+)[\s\-]*元',
            r'(\d+)[\s\-]*~[\s\-]*(\d+)[\s\-]*元',
            
            # 特殊格式
            r'￥(\d+)',
            r'RMB(\d+)',
            r'CNY(\d+)',
            r'(\d+)[\s\-]*块',
            r'(\d+)[\s\-]*块钱'
        ]
        
        prices = []
        price_contexts = []
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 处理价格范围
                    if len(match) == 2:
                        try:
                            start_price = int(match[0])
                            end_price = int(match[1])
                            prices.extend([start_price, end_price])
                            # 提取上下文
                            context = self.extract_context(text, match[0], 100)
                            price_contexts.append({
                                'price_range': f"{start_price}-{end_price}元",
                                'context': context
                            })
                        except ValueError:
                            continue
                else:
                    try:
                        price = int(match)
                        prices.append(price)
                        # 提取上下文
                        context = self.extract_context(text, match, 100)
                        price_contexts.append({
                            'price': f"{price}元",
                            'context': context
                        })
                    except ValueError:
                        continue
        
        return list(set(prices)), price_contexts
    
    def extract_context(self, text, price, context_length=100):
        """提取价格上下文"""
        try:
            price_index = text.find(str(price))
            if price_index != -1:
                start = max(0, price_index - context_length // 2)
                end = min(len(text), price_index + context_length // 2)
                context = text[start:end].strip()
                return context
        except:
            pass
        return ""
    
    def search_engine_query(self, engine_name, keyword, max_results=10):
        """执行搜索引擎查询"""
        if engine_name not in self.search_engines:
            return None
        
        engine = self.search_engines[engine_name]
        params = engine['params'].copy()
        params[list(params.keys())[0]] = keyword
        
        try:
            print(f"🔍 搜索 {engine_name}: {keyword}")
            response = self.session.get(engine['url'], params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # 查找搜索结果
                result_elements = soup.select(engine['result_selector'])
                
                for element in result_elements[:max_results]:
                    try:
                        # 提取标题
                        title_elem = element.select_one(engine['title_selector'])
                        title = title_elem.get_text().strip() if title_elem else ""
                        
                        # 提取链接
                        link = title_elem.get('href') if title_elem else ""
                        if link and not link.startswith('http'):
                            link = urljoin(engine['url'], link)
                        
                        # 提取摘要
                        snippet_elem = element.select_one(engine['snippet_selector'])
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        # 提取价格信息
                        text_content = title + " " + snippet
                        prices, contexts = self.extract_prices_from_text(text_content)
                        
                        if title or snippet:
                            results.append({
                                'title': title,
                                'url': link,
                                'snippet': snippet,
                                'prices': prices,
                                'price_contexts': contexts,
                                'engine': engine_name
                            })
                    
                    except Exception as e:
                        print(f"⚠️ 解析结果时出错: {e}")
                        continue
                
                return results
            
        except Exception as e:
            print(f"❌ {engine_name} 搜索失败: {e}")
            return None
    
    def monica_ai_style_search(self, court_name, keywords=None):
        """Monica AI 风格的智能搜索"""
        if keywords is None:
            keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 网球 价格",
                f"{court_name} 网球场 价格",
                f"{court_name} 收费标准",
                f"北京 {court_name} 价格",
                f"{court_name} 场地费",
                f"{court_name} 预订价格"
            ]
        
        print(f"\n🤖 Monica AI 风格搜索: {court_name}")
        print("=" * 60)
        
        all_results = []
        engine_results = {}
        
        # 遍历所有搜索引擎
        for engine_name in self.search_engines.keys():
            engine_results[engine_name] = []
            
            for keyword in keywords:
                results = self.search_engine_query(engine_name, keyword, max_results=5)
                if results:
                    engine_results[engine_name].extend(results)
                    all_results.extend(results)
                
                # 随机延迟，避免被反爬
                time.sleep(random.uniform(1, 3))
        
        # 分析结果
        analysis = self.analyze_monica_results(all_results, court_name)
        
        return {
            'court_name': court_name,
            'search_keywords': keywords,
            'total_results': len(all_results),
            'engine_results': engine_results,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_monica_results(self, results, court_name):
        """Monica AI 风格的结果分析"""
        if not results:
            return {
                'status': 'no_results',
                'message': f'未找到 {court_name} 的价格信息'
            }
        
        # 收集所有价格
        all_prices = []
        price_sources = {}
        engine_stats = {}
        
        for result in results:
            engine = result.get('engine', 'unknown')
            prices = result.get('prices', [])
            
            if engine not in engine_stats:
                engine_stats[engine] = {'count': 0, 'prices': []}
            
            engine_stats[engine]['count'] += 1
            engine_stats[engine]['prices'].extend(prices)
            
            for price in prices:
                all_prices.append(price)
                if price not in price_sources:
                    price_sources[price] = []
                price_sources[price].append({
                    'engine': engine,
                    'title': result.get('title', ''),
                    'url': result.get('url', '')
                })
        
        # 价格统计
        if all_prices:
            unique_prices = sorted(list(set(all_prices)))
            price_frequency = {price: all_prices.count(price) for price in unique_prices}
            
            # 智能价格推荐
            recommended_price = self.get_recommended_price(unique_prices, price_frequency)
            
            analysis = {
                'status': 'success',
                'total_results': len(results),
                'total_prices': len(all_prices),
                'unique_prices': unique_prices,
                'price_frequency': price_frequency,
                'price_range': f"{min(all_prices)}-{max(all_prices)}元" if all_prices else "无",
                'average_price': sum(all_prices) / len(all_prices) if all_prices else 0,
                'recommended_price': recommended_price,
                'engine_stats': engine_stats,
                'price_sources': price_sources,
                'confidence_score': self.calculate_confidence_score(results, all_prices)
            }
        else:
            analysis = {
                'status': 'no_prices',
                'message': f'找到 {len(results)} 个结果，但未提取到价格信息',
                'total_results': len(results)
            }
        
        return analysis
    
    def get_recommended_price(self, unique_prices, price_frequency):
        """智能推荐价格"""
        if not unique_prices:
            return None
        
        # 按频率排序
        sorted_prices = sorted(price_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # 取出现频率最高的价格
        most_frequent = sorted_prices[0]
        
        # 如果有多个价格，计算加权平均
        if len(sorted_prices) > 1:
            total_weight = sum(freq for _, freq in sorted_prices)
            weighted_avg = sum(price * freq for price, freq in sorted_prices) / total_weight
            
            return {
                'most_frequent': most_frequent[0],
                'frequency': most_frequent[1],
                'weighted_average': round(weighted_avg, 2),
                'all_prices': sorted_prices
            }
        else:
            return {
                'most_frequent': most_frequent[0],
                'frequency': most_frequent[1],
                'all_prices': sorted_prices
            }
    
    def calculate_confidence_score(self, results, prices):
        """计算置信度分数"""
        if not results or not prices:
            return 0
        
        # 基础分数
        base_score = min(len(results) / 10, 1.0) * 0.3
        
        # 价格一致性分数
        unique_prices = len(set(prices))
        total_prices = len(prices)
        consistency_score = (1 - unique_prices / total_prices) * 0.4 if total_prices > 0 else 0
        
        # 搜索引擎多样性分数
        engines = set(result.get('engine', '') for result in results)
        diversity_score = min(len(engines) / 3, 1.0) * 0.3
        
        total_score = base_score + consistency_score + diversity_score
        return round(total_score, 2)
    
    def save_results(self, results, filename=None):
        """保存搜索结果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monica_ai_search_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
            return None
    
    def print_monica_analysis(self, results):
        """打印Monica AI风格的分析结果"""
        court_name = results['court_name']
        analysis = results['analysis']
        
        print(f"\n📊 Monica AI 分析报告: {court_name}")
        print("=" * 60)
        
        if analysis['status'] == 'success':
            print(f"✅ 搜索成功")
            print(f"📈 总结果数: {analysis['total_results']}")
            print(f"💰 价格数量: {analysis['total_prices']}")
            print(f"🎯 唯一价格: {analysis['unique_prices']}")
            print(f"📊 价格范围: {analysis['price_range']}")
            print(f"📊 平均价格: {analysis['average_price']:.2f}元")
            print(f"🎯 推荐价格: {analysis['recommended_price']}")
            print(f"🎯 置信度: {analysis['confidence_score']}")
            
            print(f"\n🔍 搜索引擎统计:")
            for engine, stats in analysis['engine_stats'].items():
                print(f"  {engine}: {stats['count']} 结果, {len(stats['prices'])} 价格")
        
        elif analysis['status'] == 'no_prices':
            print(f"⚠️ {analysis['message']}")
        
        else:
            print(f"❌ {analysis['message']}")

def main():
    """主函数 - 测试Monica AI风格搜索"""
    monica = MonicaAIStyleSearch()
    
    # 测试场馆列表
    test_courts = [
        "朝阳公园网球场",
        "金地网球",
        "嘉里中心网球场",
        "国家网球中心"
    ]
    
    print("🤖 Monica AI 风格关键词搜索测试")
    print("=" * 60)
    
    all_results = []
    
    for court in test_courts:
        try:
            results = monica.monica_ai_style_search(court)
            all_results.append(results)
            
            # 打印分析结果
            monica.print_monica_analysis(results)
            
            # 保存单个结果
            monica.save_results(results, f"monica_{court.replace(' ', '_')}.json")
            
            print("\n" + "-" * 40)
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"❌ 搜索 {court} 时出错: {e}")
            continue
    
    # 保存所有结果
    if all_results:
        monica.save_results(all_results, "monica_ai_all_results.json")
        print(f"\n✅ 完成所有搜索，共处理 {len(all_results)} 个场馆")

if __name__ == "__main__":
    main() 