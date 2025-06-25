#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狗搜索深度价格抓取测试 - 基于成功的小范围测试
专门针对搜狗搜索进行更深入的朝阳公园网球场价格抓取
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import random

class SogouAdvancedPriceTest:
    def __init__(self):
        self.session = requests.Session()
        # 使用随机UA
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def extract_prices_from_text(self, text):
        """从文本中提取价格信息"""
        # 更精确的价格正则表达式
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
    
    def extract_price_context(self, text, prices):
        """提取价格上下文信息"""
        context_info = []
        for price in prices:
            # 在价格前后50个字符范围内查找上下文
            price_pattern = re.compile(rf'.{{0,50}}{price}元?.{{0,50}}')
            matches = price_pattern.findall(text)
            if matches:
                context_info.append({
                    'price': price,
                    'context': matches[0].strip()
                })
        return context_info
    
    def test_sogou_search_advanced(self, court_name):
        """测试搜狗搜索价格抓取 - 高级版本"""
        print(f"\n🔍 深度测试搜狗搜索: {court_name}")
        try:
            # 使用更多关键词组合
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格",
                f"{court_name} 网球场 价格",
                f"{court_name} 收费标准",
                f"{court_name} 收费价格",
                f"北京 {court_name} 价格",
                f"{court_name} 场地费",
                f"{court_name} 预订价格"
            ]
            
            all_results = []
            
            for keyword in search_keywords:
                search_url = f"https://www.sogou.com/web?query={quote(keyword)}"
                print(f"尝试搜索: {keyword}")
                
                response = self.session.get(search_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取所有文本内容
                    text_content = soup.get_text()
                    prices = self.extract_prices_from_text(text_content)
                    
                    if prices:
                        print(f"✅ 找到价格信息: {prices}")
                        
                        # 提取价格上下文
                        context_info = self.extract_price_context(text_content, prices)
                        
                        result = {
                            'keyword': keyword,
                            'prices': prices,
                            'context_info': context_info,
                            'url': search_url
                        }
                        all_results.append(result)
                    
                    # 查找特定元素
                    price_elements = soup.find_all(string=re.compile(r'\d+元'))
                    if price_elements:
                        prices = [elem.strip() for elem in price_elements if '元' in elem]
                        print(f"✅ 找到价格元素: {prices[:3]}")
                        
                        result = {
                            'keyword': keyword,
                            'prices': prices[:3],
                            'context_info': [],
                            'url': search_url
                        }
                        all_results.append(result)
                
                time.sleep(random.uniform(2, 4))
            
            if all_results:
                print(f"✅ 总共找到 {len(all_results)} 个搜索结果")
                return all_results
            else:
                print("❌ 未找到价格信息")
                return None
                
        except Exception as e:
            print(f"❌ 搜狗搜索抓取异常: {e}")
            return None
    
    def analyze_price_data(self, results):
        """分析价格数据"""
        if not results:
            return None
        
        all_prices = []
        price_sources = {}
        
        for result in results:
            keyword = result['keyword']
            prices = result['prices']
            
            for price in prices:
                try:
                    # 尝试提取数字价格
                    if isinstance(price, str):
                        # 处理包含文字的字符串，提取数字
                        price_match = re.search(r'(\d+)', price)
                        if price_match:
                            price_num = int(price_match.group(1))
                            all_prices.append(price_num)
                            if price not in price_sources:
                                price_sources[price] = []
                            price_sources[price].append(keyword)
                    else:
                        # 直接是数字
                        all_prices.append(int(price))
                        if price not in price_sources:
                            price_sources[price] = []
                        price_sources[price].append(keyword)
                except (ValueError, TypeError):
                    # 跳过无法解析的价格
                    continue
        
        if not all_prices:
            return None
        
        # 统计价格分布
        price_stats = {
            'total_prices': len(all_prices),
            'unique_prices': len(set(all_prices)),
            'price_range': f"{min(all_prices)}-{max(all_prices)}元" if all_prices else "无",
            'average_price': sum(all_prices) / len(all_prices) if all_prices else 0,
            'most_common_prices': sorted(set(all_prices), key=lambda x: all_prices.count(x), reverse=True)[:5],
            'price_sources': price_sources
        }
        
        return price_stats
    
    def test_all_courts(self):
        """测试所有朝阳公园相关场馆"""
        print("🎾 搜狗搜索深度价格抓取测试")
        print("=" * 60)
        
        # 测试场馆列表
        test_courts = [
            "朝阳公园网球场",
            "朝阳公园体育中心网球场",
            "朝阳公园网球中心",
            "朝阳公园体育中心",
            "朝阳公园网球",
            "朝阳公园体育中心网球"
        ]
        
        all_results = {}
        
        for court_name in test_courts:
            print(f"\n🏟️ 测试场馆: {court_name}")
            results = self.test_sogou_search_advanced(court_name)
            
            if results:
                # 分析价格数据
                price_stats = self.analyze_price_data(results)
                all_results[court_name] = {
                    'raw_results': results,
                    'price_stats': price_stats
                }
                
                # 输出分析结果
                if price_stats:
                    print(f"\n📊 {court_name} 价格分析:")
                    print(f"  总价格数: {price_stats['total_prices']}")
                    print(f"  唯一价格数: {price_stats['unique_prices']}")
                    print(f"  价格范围: {price_stats['price_range']}")
                    print(f"  平均价格: {price_stats['average_price']:.1f}元")
                    print(f"  最常见价格: {price_stats['most_common_prices']}")
            else:
                all_results[court_name] = None
            
            # 场馆间延迟
            time.sleep(random.uniform(3, 5))
        
        # 保存结果
        with open("sogou_advanced_price_test_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到: sogou_advanced_price_test_results.json")
        
        # 总结
        print(f"\n📈 测试总结")
        print("=" * 60)
        
        success_count = sum(1 for result in all_results.values() if result is not None)
        total_count = len(all_results)
        
        print(f"成功场馆数: {success_count}/{total_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        # 汇总所有价格
        all_prices = []
        for court_name, result in all_results.items():
            if result and result['price_stats']:
                prices = [int(p) for p in result['price_stats']['price_sources'].keys()]
                all_prices.extend(prices)
                print(f"{court_name}: {len(prices)}个价格")
        
        if all_prices:
            print(f"\n🎯 总体价格统计:")
            print(f"  总价格数: {len(all_prices)}")
            print(f"  唯一价格数: {len(set(all_prices))}")
            print(f"  价格范围: {min(all_prices)}-{max(all_prices)}元")
            print(f"  平均价格: {sum(all_prices)/len(all_prices):.1f}元")
        
        return all_results

def main():
    """主函数"""
    scraper = SogouAdvancedPriceTest()
    results = scraper.test_all_courts()
    
    print(f"\n✅ 测试完成！")

if __name__ == "__main__":
    main() 