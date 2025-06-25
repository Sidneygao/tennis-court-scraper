#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小范围测试乐动力、趣运动、豆瓣、知乎价格抓取
"""

import requests
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import random

class PriceScraperTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def test_ledongli(self, court_name):
        """测试乐动力价格抓取"""
        print(f"\n🔍 测试乐动力: {court_name}")
        try:
            # 乐动力搜索页面
            search_url = f"https://www.ledongli.cn/search?keyword={quote(court_name + '网球')}"
            print(f"搜索URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找价格相关信息
                price_elements = soup.find_all(text=re.compile(r'[\d]+元|[\d]+/小时|[\d]+/场'))
                if price_elements:
                    print(f"✅ 找到价格信息: {price_elements[:3]}")
                    return price_elements[:3]
                else:
                    print("❌ 未找到价格信息")
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 乐动力抓取异常: {e}")
            return None
    
    def test_quyundong(self, court_name):
        """测试趣运动价格抓取"""
        print(f"\n🔍 测试趣运动: {court_name}")
        try:
            # 趣运动搜索页面
            search_url = f"https://www.quyundong.com/search?q={quote(court_name + '网球')}"
            print(f"搜索URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找价格相关信息
                price_elements = soup.find_all(text=re.compile(r'[\d]+元|[\d]+/小时|[\d]+/场'))
                if price_elements:
                    print(f"✅ 找到价格信息: {price_elements[:3]}")
                    return price_elements[:3]
                else:
                    print("❌ 未找到价格信息")
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 趣运动抓取异常: {e}")
            return None
    
    def test_douban(self, court_name):
        """测试豆瓣价格抓取"""
        print(f"\n🔍 测试豆瓣: {court_name}")
        try:
            # 豆瓣搜索页面
            search_url = f"https://www.douban.com/search?cat=1005&q={quote(court_name + '网球')}"
            print(f"搜索URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找价格相关信息
                price_elements = soup.find_all(text=re.compile(r'[\d]+元|[\d]+/小时|[\d]+/场'))
                if price_elements:
                    print(f"✅ 找到价格信息: {price_elements[:3]}")
                    return price_elements[:3]
                else:
                    print("❌ 未找到价格信息")
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 豆瓣抓取异常: {e}")
            return None
    
    def test_zhihu(self, court_name):
        """测试知乎价格抓取"""
        print(f"\n🔍 测试知乎: {court_name}")
        try:
            # 知乎搜索页面
            search_url = f"https://www.zhihu.com/search?type=content&q={quote(court_name + '网球价格')}"
            print(f"搜索URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找价格相关信息
                price_elements = soup.find_all(text=re.compile(r'[\d]+元|[\d]+/小时|[\d]+/场'))
                if price_elements:
                    print(f"✅ 找到价格信息: {price_elements[:3]}")
                    return price_elements[:3]
                else:
                    print("❌ 未找到价格信息")
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 知乎抓取异常: {e}")
            return None
    
    def test_all_platforms(self, court_name):
        """测试所有平台"""
        print(f"\n🎾 开始测试场馆: {court_name}")
        print("=" * 50)
        
        results = {}
        
        # 测试乐动力
        results['ledongli'] = self.test_ledongli(court_name)
        time.sleep(random.uniform(1, 3))
        
        # 测试趣运动
        results['quyundong'] = self.test_quyundong(court_name)
        time.sleep(random.uniform(1, 3))
        
        # 测试豆瓣
        results['douban'] = self.test_douban(court_name)
        time.sleep(random.uniform(1, 3))
        
        # 测试知乎
        results['zhihu'] = self.test_zhihu(court_name)
        time.sleep(random.uniform(1, 3))
        
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
    print("🎾 网球场馆价格抓取测试")
    print("=" * 50)
    
    # 测试场馆列表
    test_courts = [
        "嘉里中心网球场",
        "金地网球中心", 
        "WoowTennis网球俱乐部"
    ]
    
    scraper = PriceScraperTest()
    
    all_results = {}
    
    for court in test_courts:
        results = scraper.test_all_platforms(court)
        all_results[court] = results
        print("\n" + "=" * 60 + "\n")
    
    # 保存测试结果
    with open('price_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("📁 测试结果已保存到 price_test_results.json")
    
    # 统计成功率
    total_tests = len(test_courts) * 4
    successful_tests = sum(1 for court_results in all_results.values() 
                          for result in court_results.values() if result)
    
    print(f"\n📈 测试统计:")
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {successful_tests/total_tests*100:.1f}%")

if __name__ == "__main__":
    main() 