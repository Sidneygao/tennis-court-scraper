#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朝阳公园网球场价格抓取测试 - 小范围测试
使用"朝阳公园网球场 价格 2024"等关键词格式
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import random

class ChaoyangParkPriceTest:
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
    
    def test_baidu_search(self, court_name):
        """测试百度搜索价格抓取"""
        print(f"\n🔍 测试百度搜索: {court_name}")
        try:
            # 使用您建议的关键词格式
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格",
                f"北京 {court_name} 价格",
                f"{court_name} 网球场 价格"
            ]
            
            for keyword in search_keywords:
                search_url = f"https://www.baidu.com/s?wd={quote(keyword)}"
                print(f"尝试搜索: {keyword}")
                
                response = self.session.get(search_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取所有文本内容
                    text_content = soup.get_text()
                    prices = self.extract_prices_from_text(text_content)
                    
                    if prices:
                        print(f"✅ 找到价格信息: {prices}")
                        return prices
                    
                    # 查找特定元素
                    price_elements = soup.find_all(string=re.compile(r'\d+元'))
                    if price_elements:
                        prices = [elem.strip() for elem in price_elements if '元' in elem]
                        print(f"✅ 找到价格元素: {prices[:3]}")
                        return prices[:3]
                
                time.sleep(random.uniform(2, 4))
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 百度搜索抓取异常: {e}")
            return None
    
    def test_sogou_search(self, court_name):
        """测试搜狗搜索价格抓取"""
        print(f"\n🔍 测试搜狗搜索: {court_name}")
        try:
            # 使用您建议的关键词格式
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格"
            ]
            
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
                        return prices
                
                time.sleep(random.uniform(2, 4))
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 搜狗搜索抓取异常: {e}")
            return None
    
    def test_360_search(self, court_name):
        """测试360搜索价格抓取"""
        print(f"\n🔍 测试360搜索: {court_name}")
        try:
            # 使用您建议的关键词格式
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格"
            ]
            
            for keyword in search_keywords:
                search_url = f"https://www.so.com/s?q={quote(keyword)}"
                print(f"尝试搜索: {keyword}")
                
                response = self.session.get(search_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取所有文本内容
                    text_content = soup.get_text()
                    prices = self.extract_prices_from_text(text_content)
                    
                    if prices:
                        print(f"✅ 找到价格信息: {prices}")
                        return prices
                
                time.sleep(random.uniform(2, 4))
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 360搜索抓取异常: {e}")
            return None
    
    def test_xiaohongshu_search(self, court_name):
        """测试小红书搜索价格抓取"""
        print(f"\n🔍 测试小红书搜索: {court_name}")
        try:
            # 使用您建议的关键词格式
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格"
            ]
            
            for keyword in search_keywords:
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}"
                print(f"尝试搜索: {keyword}")
                
                response = self.session.get(search_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取所有文本内容
                    text_content = soup.get_text()
                    prices = self.extract_prices_from_text(text_content)
                    
                    if prices:
                        print(f"✅ 找到价格信息: {prices}")
                        return prices
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                
                time.sleep(random.uniform(2, 4))
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 小红书搜索抓取异常: {e}")
            return None
    
    def test_douyin_search(self, court_name):
        """测试抖音搜索价格抓取"""
        print(f"\n🔍 测试抖音搜索: {court_name}")
        try:
            # 使用您建议的关键词格式
            search_keywords = [
                f"{court_name} 价格 2024",
                f"{court_name} 收费 2024",
                f"{court_name} 价格",
                f"{court_name} 网球 价格"
            ]
            
            for keyword in search_keywords:
                search_url = f"https://www.douyin.com/search/{quote(keyword)}"
                print(f"尝试搜索: {keyword}")
                
                response = self.session.get(search_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取所有文本内容
                    text_content = soup.get_text()
                    prices = self.extract_prices_from_text(text_content)
                    
                    if prices:
                        print(f"✅ 找到价格信息: {prices}")
                        return prices
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                
                time.sleep(random.uniform(2, 4))
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 抖音搜索抓取异常: {e}")
            return None
    
    def test_all_platforms(self, court_name):
        """测试所有平台"""
        print(f"🎾 开始测试朝阳公园网球场价格抓取")
        print(f"测试场馆: {court_name}")
        print("=" * 60)
        
        results = {}
        
        # 测试各个平台
        platforms = [
            ("百度搜索", self.test_baidu_search),
            ("搜狗搜索", self.test_sogou_search),
            ("360搜索", self.test_360_search),
            ("小红书搜索", self.test_xiaohongshu_search),
            ("抖音搜索", self.test_douyin_search),
        ]
        
        for platform_name, test_func in platforms:
            try:
                prices = test_func(court_name)
                results[platform_name] = prices
                time.sleep(random.uniform(3, 5))  # 平台间延迟
            except Exception as e:
                print(f"❌ {platform_name}测试异常: {e}")
                results[platform_name] = None
        
        # 输出结果
        print(f"\n📊 测试结果汇总")
        print("=" * 60)
        
        success_count = 0
        for platform, prices in results.items():
            if prices:
                print(f"✅ {platform}: {prices}")
                success_count += 1
            else:
                print(f"❌ {platform}: 未找到价格")
        
        print(f"\n🎯 成功率: {success_count}/{len(platforms)} ({success_count/len(platforms)*100:.1f}%)")
        
        return results

def main():
    """主函数"""
    print("🎾 朝阳公园网球场价格抓取测试")
    print("=" * 60)
    
    # 测试场馆
    test_courts = [
        "朝阳公园网球场",
        "朝阳公园体育中心网球场",
        "朝阳公园网球中心"
    ]
    
    scraper = ChaoyangParkPriceTest()
    
    all_results = {}
    
    for court_name in test_courts:
        print(f"\n🏟️ 测试场馆: {court_name}")
        results = scraper.test_all_platforms(court_name)
        all_results[court_name] = results
        
        # 场馆间延迟
        time.sleep(random.uniform(5, 8))
    
    # 保存结果
    with open("chaoyang_park_price_test_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: chaoyang_park_price_test_results.json")
    
    # 总结
    print(f"\n📈 测试总结")
    print("=" * 60)
    
    total_success = 0
    total_tests = 0
    
    for court_name, results in all_results.items():
        court_success = sum(1 for prices in results.values() if prices)
        court_total = len(results)
        total_success += court_success
        total_tests += court_total
        
        print(f"{court_name}: {court_success}/{court_total} 平台成功")
    
    print(f"\n🎯 总体成功率: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")

if __name__ == "__main__":
    main() 