#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile

def setup_driver():
    """设置Chrome浏览器驱动"""
    chrome_options = Options()
    
    # 反检测设置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 使用临时用户数据目录
    temp_dir = tempfile.mkdtemp(prefix='chrome_selenium_')
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    print(f"使用临时用户数据目录: {temp_dir}")
    
    # 添加远程调试端口
    chrome_options.add_argument('--remote-debugging-port=9223')
    
    # 设置用户代理
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'--user-agent={user_agent}')
    
    # 创建WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 执行反检测脚本
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def analyze_page(driver, keyword):
    """分析页面结构"""
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=note"
    
    print(f"访问: {search_url}")
    driver.get(search_url)
    time.sleep(5)
    
    # 获取页面源码
    page_source = driver.page_source
    
    # 保存页面源码
    with open(f"xhs_page_{keyword}.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    print(f"页面源码已保存: xhs_page_{keyword}.html")
    
    # 分析结构
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # 查找所有div元素
    divs = soup.find_all('div')
    print(f"找到 {len(divs)} 个div元素")
    
    # 查找包含特定关键词的class
    keywords = ['note', 'card', 'item', 'search', 'result', 'content', 'feed', 'list']
    
    for keyword in keywords:
        elements = soup.find_all(class_=lambda x: x and keyword in x)
        if elements:
            print(f"包含 '{keyword}' 的class: {len(elements)} 个元素")
            for elem in elements[:3]:  # 只显示前3个
                classes = elem.get('class', [])
                print(f"  - {classes}")
                text = elem.get_text().strip()[:100]
                if text:
                    print(f"    文本: {text}...")

def main():
    driver = setup_driver()
    
    try:
        analyze_page(driver, "网球")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 