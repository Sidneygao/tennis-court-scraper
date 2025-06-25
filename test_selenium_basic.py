#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Selenium测试脚本
测试基本网络连接和其他网站
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_chrome_driver(use_proxy=True):
    """设置Chrome浏览器驱动"""
    print("🔧 设置Chrome浏览器驱动...")
    
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 模拟真实浏览器
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # 禁用自动化检测
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 代理设置
    if use_proxy:
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:7890")
        print("   ✅ 已启用代理设置 (socks5://127.0.0.1:7890)")
    else:
        print("   ⚠️  未启用代理设置")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 执行JavaScript来隐藏自动化特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("   ✅ Chrome驱动设置完成")
        return driver
        
    except Exception as e:
        print(f"   ❌ Chrome驱动设置失败: {e}")
        return None

def test_website_access(driver, url, name):
    """测试网站访问"""
    print(f"\n🌐 测试 {name} ({url})...")
    
    try:
        start_time = time.time()
        driver.get(url)
        end_time = time.time()
        
        load_time = round((end_time - start_time) * 1000, 2)
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ {name} 访问成功!")
        print(f"   加载时间: {load_time}ms")
        print(f"   当前URL: {current_url}")
        print(f"   页面标题: {page_title}")
        print(f"   页面长度: {len(driver.page_source)} 字符")
        
        return {
            "status": "success",
            "load_time": load_time,
            "url": current_url,
            "title": page_title
        }
        
    except Exception as e:
        print(f"❌ {name} 访问失败: {e}")
        return {"status": "error", "error": str(e)}

def test_bing_search(driver):
    """测试Bing搜索"""
    print(f"\n🔍 测试Bing搜索...")
    
    try:
        # 访问Bing
        driver.get("https://www.bing.com")
        time.sleep(2)
        
        # 等待搜索框出现
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        
        # 输入搜索词
        search_query = "朝阳公园网球场 价格"
        search_box.clear()
        search_box.send_keys(search_query)
        
        # 模拟真实用户行为
        time.sleep(1)
        
        # 按回车键搜索
        from selenium.webdriver.common.keys import Keys
        search_box.send_keys(Keys.RETURN)
        
        # 等待搜索结果加载
        wait.until(EC.presence_of_element_located((By.ID, "b_results")))
        
        # 获取搜索结果
        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        
        print(f"✅ Bing搜索成功!")
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        print(f"   搜索结果数量: {len(search_results)}")
        
        # 显示前3个搜索结果
        if search_results:
            print(f"   📋 前3个搜索结果:")
            for i, result in enumerate(search_results[:3], 1):
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                    title = title_element.text
                    print(f"      {i}. {title}")
                except:
                    print(f"      {i}. [无法获取标题]")
        
        return {
            "status": "success",
            "url": driver.current_url,
            "title": driver.title,
            "results_count": len(search_results)
        }
        
    except Exception as e:
        print(f"❌ Bing搜索失败: {e}")
        return {"status": "error", "error": str(e)}

def main():
    """主函数"""
    print("🎾 Selenium基本网络测试")
    print("=" * 50)
    
    # 测试网站列表
    test_sites = [
        {"url": "https://www.baidu.com", "name": "百度"},
        {"url": "https://www.bing.com", "name": "Bing"},
        {"url": "https://www.yahoo.com", "name": "Yahoo"},
        {"url": "https://httpbin.org/ip", "name": "HTTPBin IP检测"}
    ]
    
    print("\n📋 测试1: 使用代理访问其他网站")
    driver = setup_chrome_driver(use_proxy=True)
    if driver:
        for site in test_sites:
            test_website_access(driver, site["url"], site["name"])
            time.sleep(2)  # 避免请求过快
        
        # 测试Bing搜索
        test_bing_search(driver)
        driver.quit()
    
    print("\n📋 测试2: 不使用代理访问其他网站")
    driver = setup_chrome_driver(use_proxy=False)
    if driver:
        for site in test_sites:
            test_website_access(driver, site["url"], site["name"])
            time.sleep(2)
        driver.quit()
    
    print("\n📊 测试完成")
    print("=" * 50)
    print("通过对比代理和非代理的测试结果，可以判断网络连接问题")

if __name__ == "__main__":
    main() 