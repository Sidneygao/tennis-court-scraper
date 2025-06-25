#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网球场馆价格抓取测试 - 使用更智能的反反爬技术
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import random

class AdvancedPriceScraperTest:
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
            r'(\d+)[\s\-]*元/?小时?',
            r'(\d+)[\s\-]*元/?场',
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend(matches)
        
        return list(set(prices))  # 去重
    
    def test_ledongli_advanced(self, court_name):
        """测试乐动力价格抓取 - 高级版本"""
        print(f"\n🔍 测试乐动力: {court_name}")
        try:
            # 尝试多个搜索关键词
            search_keywords = [
                f"{court_name}网球",
                f"{court_name}价格",
                f"{court_name}收费",
                "网球" + court_name
            ]
            
            for keyword in search_keywords:
                search_url = f"https://www.ledongli.cn/search?keyword={quote(keyword)}"
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
            print(f"❌ 乐动力抓取异常: {e}")
            return None
    
    def test_quyundong_advanced(self, court_name):
        """测试趣运动价格抓取 - 高级版本"""
        print(f"\n🔍 测试趣运动: {court_name}")
        try:
            # 趣运动可能使用不同的URL结构
            search_urls = [
                f"https://www.quyundong.com/search?q={quote(court_name + '网球')}",
                f"https://www.quyundong.com/search?keyword={quote(court_name)}",
                f"https://www.quyundong.com/venue/search?q={quote(court_name + '网球')}"
            ]
            
            for search_url in search_urls:
                print(f"尝试URL: {search_url}")
                
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
            print(f"❌ 趣运动抓取异常: {e}")
            return None
    
    def test_douban_advanced(self, court_name):
        """测试豆瓣价格抓取 - 高级版本"""
        print(f"\n🔍 测试豆瓣: {court_name}")
        try:
            # 豆瓣搜索
            search_url = f"https://www.douban.com/search?cat=1005&q={quote(court_name + '网球')}"
            print(f"搜索URL: {search_url}")
            
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
            else:
                print(f"❌ 请求失败: {response.status_code}")
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 豆瓣抓取异常: {e}")
            return None
    
    def test_zhihu_advanced(self, court_name):
        """测试知乎价格抓取 - 高级版本"""
        print(f"\n🔍 测试知乎: {court_name}")
        try:
            # 知乎搜索 - 尝试不同的搜索策略
            search_urls = [
                f"https://www.zhihu.com/search?type=content&q={quote(court_name + '网球价格')}",
                f"https://www.zhihu.com/search?type=content&q={quote(court_name + '收费')}",
                f"https://www.zhihu.com/search?type=content&q={quote('北京' + court_name + '网球')}"
            ]
            
            for search_url in search_urls:
                print(f"尝试URL: {search_url}")
                
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
            print(f"❌ 知乎抓取异常: {e}")
            return None
    
    def test_baidu_search(self, court_name):
        """测试百度搜索价格抓取"""
        print(f"\n🔍 测试百度搜索: {court_name}")
        try:
            search_url = f"https://www.baidu.com/s?wd={quote(court_name + '网球价格收费')}"
            print(f"搜索URL: {search_url}")
            
            response = self.session.get(search_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取所有文本内容
                text_content = soup.get_text()
                prices = self.extract_prices_from_text(text_content)
                
                if prices:
                    print(f"✅ 找到价格信息: {prices}")
                    return prices
            
            print("❌ 未找到价格信息")
            return None
                
        except Exception as e:
            print(f"❌ 百度搜索抓取异常: {e}")
            return None
    
    def test_all_platforms_advanced(self, court_name):
        """测试所有平台 - 高级版本"""
        print(f"\n🎾 开始测试场馆: {court_name}")
        print("=" * 50)
        
        results = {}
        
        # 测试乐动力
        results['ledongli'] = self.test_ledongli_advanced(court_name)
        time.sleep(random.uniform(3, 5))
        
        # 测试趣运动
        results['quyundong'] = self.test_quyundong_advanced(court_name)
        time.sleep(random.uniform(3, 5))
        
        # 测试豆瓣
        results['douban'] = self.test_douban_advanced(court_name)
        time.sleep(random.uniform(3, 5))
        
        # 测试知乎
        results['zhihu'] = self.test_zhihu_advanced(court_name)
        time.sleep(random.uniform(3, 5))
        
        # 测试百度搜索
        results['baidu'] = self.test_baidu_search(court_name)
        time.sleep(random.uniform(3, 5))
        
        # 汇总结果
        print(f"\n📊 测试结果汇总:")
        print("=" * 50)
        for platform, result in results.items():
            status = "✅ 成功" if result else "❌ 失败"
            print(f"{platform:12}: {status}")
            if result:
                print(f"           价格: {result}")
        
        return results

def main():
    """主函数"""
    print("🎾 高级网球场馆价格抓取测试")
    print("=" * 50)
    
    # 测试场馆列表
    test_courts = [
        "嘉里中心网球场",
        "金地网球中心", 
        "WoowTennis网球俱乐部"
    ]
    
    scraper = AdvancedPriceScraperTest()
    
    all_results = {}
    
    for court in test_courts:
        results = scraper.test_all_platforms_advanced(court)
        all_results[court] = results
        print("\n" + "=" * 60 + "\n")
    
    # 保存测试结果
    with open('price_test_results_advanced.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("📁 测试结果已保存到 price_test_results_advanced.json")
    
    # 统计成功率
    total_tests = len(test_courts) * 5  # 5个平台
    successful_tests = sum(1 for court_results in all_results.values() 
                          for result in court_results.values() if result)
    
    print(f"\n📈 测试统计:")
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {successful_tests/total_tests*100:.1f}%")

if __name__ == "__main__":
    main() 