#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tempfile
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XiaohongshuStructureAnalyzer:
    """分析小红书页面结构的工具"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            chrome_options = Options()
            
            # 不使用无头模式，方便调试
            # chrome_options.add_argument('--headless')
            
            # 反检测设置
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用临时用户数据目录
            temp_dir = tempfile.mkdtemp(prefix='chrome_selenium_')
            chrome_options.add_argument(f'--user-data-dir={temp_dir}')
            print(f"✅ 使用临时用户数据目录: {temp_dir}")
            
            # 添加远程调试端口
            chrome_options.add_argument('--remote-debugging-port=9223')  # 使用不同端口
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # 设置用户代理
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # 其他设置
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # 创建WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行反检测脚本
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome浏览器驱动设置成功")
            
        except Exception as e:
            print(f"❌ 设置Chrome浏览器驱动失败: {e}")
            raise
    
    def analyze_search_page(self, keyword: str):
        """分析搜索页面的结构"""
        try:
            # 构建搜索URL
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=note"
            
            print(f"正在访问小红书搜索页面: {keyword}")
            print(f"URL: {search_url}")
            
            self.driver.get(search_url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 获取页面源码
            page_source = self.driver.page_source
            
            # 保存页面源码到文件
            with open(f"xiaohongshu_page_{keyword.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print(f"✅ 页面源码已保存到: xiaohongshu_page_{keyword.replace(' ', '_')}.html")
            
            # 分析页面结构
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 查找所有可能的容器元素
            containers = []
            
            # 查找常见的容器类名
            container_selectors = [
                'div[class*="note"]',
                'div[class*="card"]',
                'div[class*="item"]',
                'div[class*="search"]',
                'div[class*="result"]',
                'div[class*="content"]',
                'div[class*="feed"]',
                'div[class*="list"]',
                'div[class*="grid"]',
                'div[class*="container"]'
            ]
            
            for selector in container_selectors:
                elements = soup.select(selector)
                if elements:
                    containers.extend(elements)
                    print(f"找到 {len(elements)} 个元素使用选择器: {selector}")
            
            # 去重
            unique_containers = []
            seen_classes = set()
            for container in containers:
                class_name = container.get('class', [])
                if class_name:
                    class_str = ' '.join(class_name)
                    if class_str not in seen_classes:
                        seen_classes.add(class_str)
                        unique_containers.append(container)
            
            print(f"✅ 找到 {len(unique_containers)} 个唯一的容器元素")
            
            # 分析每个容器的结构
            analysis_results = []
            for i, container in enumerate(unique_containers[:10]):  # 只分析前10个
                analysis = self.analyze_container(container, i)
                if analysis:
                    analysis_results.append(analysis)
            
            # 保存分析结果
            with open(f"xiaohongshu_analysis_{keyword.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 分析结果已保存到: xiaohongshu_analysis_{keyword.replace(' ', '_')}.json")
            
            # 查找所有文本内容
            text_elements = soup.find_all(text=True)
            text_content = [text.strip() for text in text_elements if text.strip() and len(text.strip()) > 5]
            
            print(f"✅ 找到 {len(text_content)} 个文本内容片段")
            print("前10个文本内容:")
            for i, text in enumerate(text_content[:10]):
                print(f"  {i+1}. {text[:100]}...")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"分析搜索页面失败: {keyword}, 错误: {e}")
            return None
    
    def analyze_container(self, container, index):
        """分析单个容器的结构"""
        try:
            analysis = {
                "index": index,
                "tag": container.name,
                "classes": container.get('class', []),
                "id": container.get('id', ''),
                "attributes": dict(container.attrs),
                "text_content": container.get_text().strip()[:200] + "..." if len(container.get_text().strip()) > 200 else container.get_text().strip(),
                "children": []
            }
            
            # 分析子元素
            for child in container.find_all(recursive=False)[:5]:  # 只分析前5个子元素
                child_analysis = {
                    "tag": child.name,
                    "classes": child.get('class', []),
                    "text": child.get_text().strip()[:100] + "..." if len(child.get_text().strip()) > 100 else child.get_text().strip()
                }
                analysis["children"].append(child_analysis)
            
            return analysis
            
        except Exception as e:
            print(f"分析容器失败: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    analyzer = XiaohongshuStructureAnalyzer()
    
    try:
        # 测试关键词
        test_keywords = ["网球", "网球场", "网球馆"]
        
        for keyword in test_keywords:
            print(f"\n{'='*50}")
            print(f"分析关键词: {keyword}")
            print(f"{'='*50}")
            
            results = analyzer.analyze_search_page(keyword)
            
            if results:
                print(f"✅ 成功分析关键词: {keyword}")
            else:
                print(f"❌ 分析关键词失败: {keyword}")
            
            # 等待一下再测试下一个关键词
            time.sleep(3)
    
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    main() 