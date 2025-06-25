#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing搜索Selenium测试脚本
使用Selenium模拟浏览器进行Bing搜索测试
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict

class BingSeleniumTester:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome浏览器启动成功")
        except Exception as e:
            print(f"❌ Chrome浏览器启动失败: {e}")
            print("请确保已安装Chrome浏览器和ChromeDriver")
    
    def search_bing(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        使用Bing搜索
        """
        if not self.driver:
            print("❌ 浏览器未启动")
            return []
        
        try:
            print(f"🔍 搜索查询: {query}")
            
            # 访问Bing搜索页面
            self.driver.get("https://www.bing.com")
            time.sleep(2)
            
            # 查找搜索框并输入查询
            search_box = self.driver.find_element(By.ID, "sb_form_q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "b_algo"))
            )
            
            time.sleep(2)
            
            # 提取搜索结果
            results = self.extract_search_results(max_results)
            
            print(f"📊 提取到 {len(results)} 个结果")
            return results
            
        except TimeoutException:
            print("❌ 搜索超时")
            return []
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def extract_search_results(self, max_results: int) -> List[Dict]:
        """
        提取搜索结果
        """
        results = []
        
        try:
            # 查找搜索结果元素
            search_results = self.driver.find_elements(By.CLASS_NAME, "b_algo")
            
            for i, result in enumerate(search_results[:max_results]):
                try:
                    # 提取标题和链接
                    title_elem = result.find_element(By.TAG_NAME, "h2")
                    link_elem = title_elem.find_element(By.TAG_NAME, "a")
                    
                    title = link_elem.text.strip()
                    url = link_elem.get_attribute("href")
                    
                    # 提取描述
                    try:
                        desc_elem = result.find_element(By.CLASS_NAME, "b_caption")
                        description = desc_elem.text.strip()
                    except NoSuchElementException:
                        description = ""
                    
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
                    
        except Exception as e:
            print(f"❌ 提取搜索结果失败: {e}")
        
        return results
    
    def test_price_search(self, court_name: str) -> List[Dict]:
        """
        测试价格搜索
        """
        queries = [
            f'"{court_name}" 北京 网球场 价格',
            f'"{court_name}" 网球 收费 费用',
            f'"{court_name}" 网球场 预约 价格表',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*60}")
            
            results = self.search_bing(query, max_results=3)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    if result['description']:
                        print(f"     描述: {result['description'][:100]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            time.sleep(3)
        
        return all_results
    
    def test_contact_search(self, court_name: str) -> List[Dict]:
        """
        测试联系方式搜索
        """
        queries = [
            f'"{court_name}" 北京 网球场 电话',
            f'"{court_name}" 网球 联系方式 预约',
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🔍 测试查询: {query}")
            print(f"{'='*60}")
            
            results = self.search_bing(query, max_results=3)
            
            if results:
                print("📋 搜索结果:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    if result['description']:
                        print(f"     描述: {result['description'][:100]}...")
                    print()
                
                all_results.extend(results)
            else:
                print("❌ 未找到结果")
            
            time.sleep(3)
        
        return all_results
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔒 浏览器已关闭")

def main():
    """
    主测试函数
    """
    print("🎾 Bing搜索Selenium测试工具")
    print("=" * 60)
    
    tester = BingSeleniumTester()
    
    if not tester.driver:
        print("❌ 无法启动浏览器，测试终止")
        return
    
    try:
        # 测试场馆列表
        test_courts = [
            "朝阳公园网球场",
            "金地网球",
            "嘉里中心网球场"
        ]
        
        for court in test_courts:
            print(f"\n{'🚀'*25} 测试场馆: {court} {'🚀'*25}")
            
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
            filename = f"bing_selenium_test_{court.replace(' ', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 结果已保存到: {filename}")
            print(f"📊 总计找到 {results['total_results']} 个结果")
            
            print(f"\n{'='*70}\n")
    
    finally:
        tester.close()

if __name__ == "__main__":
    main() 