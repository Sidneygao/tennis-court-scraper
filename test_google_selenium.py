#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium测试Google访问
模拟真实浏览器行为，绕过反爬检测
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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
    
    # 禁用图片加载以提高速度
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 执行JavaScript来隐藏自动化特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("   ✅ Chrome驱动设置完成")
        return driver
        
    except WebDriverException as e:
        print(f"   ❌ Chrome驱动设置失败: {e}")
        print("   💡 请确保已安装Chrome浏览器和ChromeDriver")
        return None

def test_google_homepage(driver):
    """测试Google主页访问"""
    print("\n🔍 测试Google主页访问...")
    print("=" * 50)
    
    try:
        start_time = time.time()
        driver.get("https://www.google.com")
        end_time = time.time()
        
        load_time = round((end_time - start_time) * 1000, 2)
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ Google主页访问成功!")
        print(f"   加载时间: {load_time}ms")
        print(f"   当前URL: {current_url}")
        print(f"   页面标题: {page_title}")
        
        # 检查页面内容
        page_source = driver.page_source.lower()
        if "google" in page_source:
            print(f"   ✅ 确认是Google页面")
        else:
            print(f"   ⚠️  可能不是Google页面")
        
        # 检查是否有验证码或反爬提示
        anti_bot_keywords = ["captcha", "robot", "bot", "automated", "blocked", "suspicious", "验证码"]
        found_anti_bot = []
        for keyword in anti_bot_keywords:
            if keyword in page_source:
                found_anti_bot.append(keyword)
        
        if found_anti_bot:
            print(f"   ⚠️  检测到反爬关键词: {found_anti_bot}")
        else:
            print(f"   ✅ 未检测到明显的反爬提示")
        
        return {
            "status": "success",
            "load_time": load_time,
            "url": current_url,
            "title": page_title,
            "has_anti_bot": len(found_anti_bot) > 0
        }
        
    except Exception as e:
        print(f"❌ Google主页访问失败: {e}")
        return {"status": "error", "error": str(e)}

def test_google_search(driver, search_query):
    """测试Google搜索功能"""
    print(f"\n🔍 测试Google搜索功能...")
    print("=" * 50)
    print(f"搜索关键词: {search_query}")
    
    try:
        # 等待搜索框出现
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        
        # 清空搜索框并输入搜索词
        search_box.clear()
        search_box.send_keys(search_query)
        
        # 模拟真实用户行为 - 短暂停顿
        time.sleep(1)
        
        # 按回车键搜索
        search_box.send_keys(Keys.RETURN)
        
        # 等待搜索结果加载
        wait.until(EC.presence_of_element_located((By.ID, "search")))
        
        # 获取搜索结果
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        print(f"✅ 搜索成功!")
        print(f"   当前URL: {driver.current_url}")
        print(f"   页面标题: {driver.title}")
        print(f"   搜索结果数量: {len(search_results)}")
        
        # 分析搜索结果
        if search_results:
            print(f"   📋 前3个搜索结果:")
            for i, result in enumerate(search_results[:3], 1):
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text
                    print(f"      {i}. {title}")
                except:
                    print(f"      {i}. [无法获取标题]")
        
        # 检查是否包含搜索关键词
        page_source = driver.page_source
        if search_query.split()[0] in page_source:  # 检查第一个关键词
            print(f"   ✅ 搜索结果包含相关关键词")
        else:
            print(f"   ⚠️  搜索结果可能不相关")
        
        return {
            "status": "success",
            "url": driver.current_url,
            "title": driver.title,
            "results_count": len(search_results)
        }
        
    except TimeoutException:
        print(f"❌ 搜索超时")
        return {"status": "timeout", "error": "搜索超时"}
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return {"status": "error", "error": str(e)}

def test_google_with_different_proxies():
    """测试不同代理设置"""
    print("\n🔍 测试不同代理设置...")
    print("=" * 50)
    
    proxy_configs = [
        {
            "name": "SOCKS5代理 (7890)",
            "proxy": "socks5://127.0.0.1:7890",
            "enabled": True
        },
        {
            "name": "HTTP代理 (7890)",
            "proxy": "http://127.0.0.1:7890",
            "enabled": True
        },
        {
            "name": "无代理",
            "proxy": None,
            "enabled": False
        }
    ]
    
    results = {}
    
    for config in proxy_configs:
        print(f"\n🌐 测试 {config['name']}...")
        
        try:
            driver = setup_chrome_driver(use_proxy=config['enabled'])
            if driver is None:
                print(f"   ❌ 无法创建驱动")
                results[config['name']] = {"status": "driver_error"}
                continue
            
            # 测试Google主页
            homepage_result = test_google_homepage(driver)
            
            # 如果主页访问成功，测试搜索
            if homepage_result.get("status") == "success":
                search_result = test_google_search(driver, "朝阳公园网球场")
                results[config['name']] = {
                    "homepage": homepage_result,
                    "search": search_result
                }
            else:
                results[config['name']] = {
                    "homepage": homepage_result,
                    "search": {"status": "skipped"}
                }
            
            driver.quit()
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            results[config['name']] = {"status": "error", "error": str(e)}
    
    return results

def test_google_anti_bot_detection():
    """测试Google反爬虫检测"""
    print("\n🔍 测试Google反爬虫检测...")
    print("=" * 50)
    
    try:
        driver = setup_chrome_driver(use_proxy=True)
        if driver is None:
            return {"status": "driver_error"}
        
        # 访问Google
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # 检查是否有验证码
        captcha_elements = driver.find_elements(By.CSS_SELECTOR, "form#captcha-form, .g-recaptcha, .recaptcha")
        
        if captcha_elements:
            print(f"⚠️  检测到验证码!")
            print(f"   验证码元素数量: {len(captcha_elements)}")
            return {"status": "captcha_detected", "captcha_count": len(captcha_elements)}
        
        # 检查是否有其他反爬提示
        page_source = driver.page_source.lower()
        anti_bot_indicators = [
            "unusual traffic", "automated requests", "robot", "bot",
            "suspicious activity", "blocked", "rate limit"
        ]
        
        found_indicators = []
        for indicator in anti_bot_indicators:
            if indicator in page_source:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"⚠️  检测到反爬指示器: {found_indicators}")
            return {"status": "anti_bot_detected", "indicators": found_indicators}
        
        print(f"✅ 未检测到明显的反爬机制")
        driver.quit()
        return {"status": "clean"}
        
    except Exception as e:
        print(f"❌ 反爬检测测试失败: {e}")
        return {"status": "error", "error": str(e)}

def save_test_results(results, filename="selenium_google_test_results.json"):
    """保存测试结果"""
    print(f"\n💾 保存测试结果到 {filename}...")
    
    test_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "Selenium Google访问测试",
        "results": results,
        "summary": {
            "total_tests": len(results),
            "successful_tests": sum(1 for r in results.values() if r.get("status") != "error"),
            "failed_tests": sum(1 for r in results.values() if r.get("status") == "error")
        }
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 测试结果已保存")

def main():
    """主函数"""
    print("🎾 Selenium Google访问测试工具")
    print("=" * 50)
    print("使用Selenium模拟真实浏览器访问Google")
    print("=" * 50)
    
    all_results = {}
    
    # 测试1: 基本Google访问
    print("\n📋 测试1: 基本Google访问")
    driver = setup_chrome_driver(use_proxy=True)
    if driver:
        all_results["basic_access"] = test_google_homepage(driver)
        driver.quit()
    
    # 测试2: Google搜索
    print("\n📋 测试2: Google搜索")
    driver = setup_chrome_driver(use_proxy=True)
    if driver:
        all_results["search_test"] = test_google_search(driver, "朝阳公园网球场 价格")
        driver.quit()
    
    # 测试3: 不同代理配置
    print("\n📋 测试3: 不同代理配置")
    all_results["proxy_tests"] = test_google_with_different_proxies()
    
    # 测试4: 反爬检测
    print("\n📋 测试4: 反爬检测")
    all_results["anti_bot_test"] = test_google_anti_bot_detection()
    
    # 保存结果
    save_test_results(all_results)
    
    # 生成总结
    print("\n📊 测试总结")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(all_results)
    
    for test_name, result in all_results.items():
        if isinstance(result, dict) and result.get("status") == "success":
            successful_tests += 1
            print(f"✅ {test_name}: 成功")
        else:
            print(f"❌ {test_name}: 失败")
    
    print(f"\n📈 成功率: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    print("\n📊 测试完成")
    print("=" * 50)
    print("请查看生成的测试结果文件了解详细信息")

if __name__ == "__main__":
    main() 