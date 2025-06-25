#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Google爬取测试脚本
专门测试Google搜索功能，模拟真实浏览器行为
"""

import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import quote

class GoogleSeleniumCrawler:
    """Google Selenium爬虫类"""
    
    def __init__(self, use_proxy=True):
        self.use_proxy = use_proxy
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        print("🔧 设置Chrome浏览器驱动...")
        
        chrome_options = Options()
        
        # 基本设置
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 模拟真实浏览器
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 禁用自动化检测
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 代理设置
        if self.use_proxy:
            chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:7890")
            print("   ✅ 已启用代理设置 (socks5://127.0.0.1:7890)")
        else:
            print("   ⚠️  未启用代理设置")
        
        # 禁用图片和CSS加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # 执行JavaScript来隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("   ✅ Chrome驱动设置完成")
            return True
            
        except Exception as e:
            print(f"   ❌ Chrome驱动设置失败: {e}")
            return False
    
    def simulate_human_behavior(self):
        """模拟人类行为"""
        # 随机滚动
        scroll_amount = random.randint(300, 800)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))
        
        # 随机移动鼠标（模拟）
        time.sleep(random.uniform(0.3, 0.8))
    
    def test_google_access(self):
        """测试Google访问"""
        print("\n🔍 测试Google主页访问...")
        print("=" * 50)
        
        try:
            start_time = time.time()
            self.driver.get("https://www.google.com")
            end_time = time.time()
            
            load_time = round((end_time - start_time) * 1000, 2)
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"✅ Google主页访问成功!")
            print(f"   加载时间: {load_time}ms")
            print(f"   当前URL: {current_url}")
            print(f"   页面标题: {page_title}")
            
            # 检查页面内容
            page_source = self.driver.page_source.lower()
            if "google" in page_source:
                print(f"   ✅ 确认是Google页面")
            else:
                print(f"   ⚠️  可能不是Google页面")
            
            # 检查是否有验证码
            captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, "form#captcha-form, .g-recaptcha, .recaptcha")
            if captcha_elements:
                print(f"   ⚠️  检测到验证码!")
                return {"status": "captcha_detected"}
            
            # 检查是否有反爬提示
            anti_bot_keywords = ["unusual traffic", "automated requests", "robot", "bot", "suspicious"]
            found_anti_bot = []
            for keyword in anti_bot_keywords:
                if keyword in page_source:
                    found_anti_bot.append(keyword)
            
            if found_anti_bot:
                print(f"   ⚠️  检测到反爬关键词: {found_anti_bot}")
                return {"status": "anti_bot_detected", "keywords": found_anti_bot}
            
            print(f"   ✅ 未检测到明显的反爬提示")
            return {
                "status": "success",
                "load_time": load_time,
                "url": current_url,
                "title": page_title
            }
            
        except Exception as e:
            print(f"❌ Google主页访问失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def search_google(self, query):
        """Google搜索"""
        print(f"\n🔍 执行Google搜索: {query}")
        print("=" * 50)
        
        try:
            # 等待搜索框出现
            search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
            
            # 模拟人类输入行为
            search_box.clear()
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # 短暂停顿
            time.sleep(random.uniform(0.5, 1.0))
            
            # 按回车键搜索
            search_box.send_keys(Keys.RETURN)
            
            # 等待搜索结果加载
            self.wait.until(EC.presence_of_element_located((By.ID, "search")))
            
            # 模拟人类浏览行为
            self.simulate_human_behavior()
            
            # 获取搜索结果
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            print(f"✅ Google搜索成功!")
            print(f"   当前URL: {self.driver.current_url}")
            print(f"   页面标题: {self.driver.title}")
            print(f"   搜索结果数量: {len(search_results)}")
            
            # 分析搜索结果
            results_data = []
            if search_results:
                print(f"   📋 前5个搜索结果:")
                for i, result in enumerate(search_results[:5], 1):
                    try:
                        title_element = result.find_element(By.CSS_SELECTOR, "h3")
                        title = title_element.text
                        
                        # 尝试获取链接
                        try:
                            link_element = result.find_element(By.CSS_SELECTOR, "a")
                            link = link_element.get_attribute("href")
                        except:
                            link = "无链接"
                        
                        # 尝试获取摘要
                        try:
                            snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                            snippet = snippet_element.text
                        except:
                            snippet = "无摘要"
                        
                        print(f"      {i}. {title}")
                        print(f"         URL: {link}")
                        print(f"         摘要: {snippet[:100]}...")
                        
                        results_data.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet
                        })
                        
                    except Exception as e:
                        print(f"      {i}. [无法获取标题: {e}]")
            
            # 检查是否包含搜索关键词
            page_source = self.driver.page_source
            query_words = query.split()
            found_keywords = [word for word in query_words if word in page_source]
            
            if found_keywords:
                print(f"   ✅ 搜索结果包含关键词: {found_keywords}")
            else:
                print(f"   ⚠️  搜索结果可能不相关")
            
            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "results_count": len(search_results),
                "results": results_data,
                "found_keywords": found_keywords
            }
            
        except TimeoutException:
            print(f"❌ 搜索超时")
            return {"status": "timeout", "error": "搜索超时"}
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def search_tennis_court_prices(self):
        """搜索网球场价格信息"""
        search_queries = [
            "朝阳公园网球场 价格 2024",
            "北京网球场价格",
            "金地网球价格",
            "嘉里中心网球场价格"
        ]
        
        all_results = {}
        
        for query in search_queries:
            print(f"\n🎾 搜索网球场价格: {query}")
            
            # 先访问Google主页
            homepage_result = self.test_google_access()
            if homepage_result.get("status") != "success":
                print(f"❌ 无法访问Google主页，跳过搜索: {query}")
                all_results[query] = {"status": "homepage_failed", "result": homepage_result}
                continue
            
            # 执行搜索
            search_result = self.search_google(query)
            all_results[query] = search_result
            
            # 随机等待，避免请求过快
            time.sleep(random.uniform(2, 4))
        
        return all_results
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")
    
    def save_results(self, results, filename="selenium_google_results.json"):
        """保存测试结果"""
        print(f"\n💾 保存测试结果到 {filename}...")
        
        test_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "Selenium Google爬取测试",
            "use_proxy": self.use_proxy,
            "results": results
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 测试结果已保存")

def main():
    """主函数"""
    print("🎾 Selenium Google爬取测试工具")
    print("=" * 50)
    print("专门测试Google搜索功能，模拟真实浏览器行为")
    print("=" * 50)
    
    # 测试1: 使用代理
    print("\n📋 测试1: 使用代理访问Google")
    crawler1 = GoogleSeleniumCrawler(use_proxy=True)
    
    if crawler1.setup_driver():
        try:
            # 测试Google访问
            homepage_result = crawler1.test_google_access()
            
            if homepage_result.get("status") == "success":
                # 测试网球场价格搜索
                search_results = crawler1.search_tennis_court_prices()
                crawler1.save_results(search_results, "selenium_google_proxy_results.json")
            else:
                print(f"❌ Google访问失败: {homepage_result}")
                crawler1.save_results({"homepage": homepage_result}, "selenium_google_proxy_failed.json")
        finally:
            crawler1.close()
    
    # 测试2: 不使用代理
    print("\n📋 测试2: 不使用代理访问Google")
    crawler2 = GoogleSeleniumCrawler(use_proxy=False)
    
    if crawler2.setup_driver():
        try:
            # 测试Google访问
            homepage_result = crawler2.test_google_access()
            
            if homepage_result.get("status") == "success":
                # 测试网球场价格搜索
                search_results = crawler2.search_tennis_court_prices()
                crawler2.save_results(search_results, "selenium_google_no_proxy_results.json")
            else:
                print(f"❌ Google访问失败: {homepage_result}")
                crawler2.save_results({"homepage": homepage_result}, "selenium_google_no_proxy_failed.json")
        finally:
            crawler2.close()
    
    print("\n📊 测试完成")
    print("=" * 50)
    print("请查看生成的测试结果文件了解详细信息")

if __name__ == "__main__":
    main() 