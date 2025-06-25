#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing搜索价格爬虫
用于爬取所有场馆的真实价格信息
"""

import time
import json
import re
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)

MIN_VALID_PRICE = 20
MAX_VALID_PRICE = 1000

def filter_valid_prices(prices, min_price=MIN_VALID_PRICE, max_price=MAX_VALID_PRICE):
    """过滤掉不合理的价格"""
    return [p for p in prices if isinstance(p, (int, float)) and min_price <= p <= max_price]

class BingPriceScraper:
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
            self.driver.implicitly_wait(10)
        except Exception as e:
            logger.error(f"Chrome浏览器初始化失败: {e}")
            raise
    
    def search_bing(self, query: str, max_results: int = 15) -> List[Dict]:
        """使用Bing搜索获取结果"""
        try:
            # 构建搜索URL
            search_url = f"https://www.bing.com/search?q={query}"
            self.driver.get(search_url)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "b_results"))
            )
            
            # 获取搜索结果
            results = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "#b_results .b_algo")
            
            for element in result_elements[:max_results]:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, "h2 a")
                    title = title_element.text.strip()
                    url = title_element.get_attribute("href")
                    
                    # 获取摘要
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".b_caption p")
                        snippet = snippet_element.text.strip()
                    except NoSuchElementException:
                        snippet = ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                except Exception as e:
                    logger.warning(f"解析搜索结果失败: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Bing搜索失败: {e}")
            return []
    
    def extract_price_info(self, text: str) -> Dict:
        """从文本中提取价格信息"""
        price_info = {
            "peak_price": None,
            "off_peak_price": None,
            "weekend_price": None,
            "price_notes": [],
            "phone": None,
            "address": None
        }
        
        # 提取价格信息
        price_patterns = [
            r'(\d+)[-~](\d+)\s*元/小时',  # 120-200元/小时
            r'(\d+)\s*元/小时',  # 200元/小时
            r'(\d+)[-~](\d+)\s*元',  # 120-200元
            r'(\d+)\s*元',  # 200元
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        min_price, max_price = int(match[0]), int(match[1])
                        if not price_info["peak_price"] or max_price > price_info["peak_price"]:
                            price_info["peak_price"] = max_price
                        if not price_info["off_peak_price"] or min_price < price_info["off_peak_price"]:
                            price_info["off_peak_price"] = min_price
                    else:
                        price = int(match)
                        if not price_info["peak_price"] or price > price_info["peak_price"]:
                            price_info["peak_price"] = price
                        if not price_info["off_peak_price"] or price < price_info["off_peak_price"]:
                            price_info["off_peak_price"] = price
        
        # 提取电话号码
        phone_pattern = r'(\d{3}-\d{8}|\d{4}-\d{7}|\d{11})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            price_info["phone"] = phone_match.group(1)
        
        # 提取地址信息
        address_patterns = [
            r'地址[：:]\s*([^\n\r]+)',
            r'位于[^\n\r]*?([^\n\r]{10,})',
            r'地址[^\n\r]*?([^\n\r]{10,})'
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, text)
            if address_match:
                address = address_match.group(1).strip()
                if len(address) > 10:  # 确保地址足够长
                    price_info["address"] = address
                    break
        
        # 提取价格备注
        if "周末" in text or "周六" in text or "周日" in text:
            price_info["price_notes"].append("周末价格可能不同")
        if "节假日" in text:
            price_info["price_notes"].append("节假日价格可能不同")
        if "黄金时段" in text:
            price_info["price_notes"].append("黄金时段价格较高")
        
        return price_info
    
    def scrape_court_prices(self, court_name: str, court_address: str = "") -> Dict:
        """爬取单个场馆的价格信息"""
        try:
            # 构建搜索关键词
            search_queries = [
                f"{court_name} 价格 收费",
                f"{court_name} 网球场 价格",
                f"{court_name} 收费标准",
                f"{court_name} 电话 地址"
            ]
            
            all_price_info = []
            all_text = ""
            
            for query in search_queries:
                logger.info(f"搜索: {query}")
                results = self.search_bing(query, max_results=10)
                
                for result in results:
                    all_text += f"{result['title']} {result['snippet']} "
                    price_info = self.extract_price_info(f"{result['title']} {result['snippet']}")
                    if price_info["peak_price"] or price_info["phone"] or price_info["address"]:
                        all_price_info.append(price_info)
                
                time.sleep(2)  # 避免请求过快
            
            # 合并所有价格信息
            merged_info = {
                "peak_price": None,
                "off_peak_price": None,
                "weekend_price": None,
                "price_notes": [],
                "phone": None,
                "address": None,
                "source": "bing_search"
            }
            
            # 选择最高和最低价格
            peak_prices = [info["peak_price"] for info in all_price_info if info["peak_price"]]
            off_peak_prices = [info["off_peak_price"] for info in all_price_info if info["off_peak_price"]]
            # 新增：过滤极端值
            peak_prices = filter_valid_prices(peak_prices)
            off_peak_prices = filter_valid_prices(off_peak_prices)
            if peak_prices:
                merged_info["peak_price"] = max(peak_prices)
            if off_peak_prices:
                merged_info["off_peak_price"] = min(off_peak_prices)
            
            # 合并电话号码和地址
            for info in all_price_info:
                if info["phone"] and not merged_info["phone"]:
                    merged_info["phone"] = info["phone"]
                if info["address"] and not merged_info["address"]:
                    merged_info["address"] = info["address"]
                merged_info["price_notes"].extend(info["price_notes"])
            
            # 去重备注
            merged_info["price_notes"] = list(set(merged_info["price_notes"]))
            
            # 如果没有找到价格，尝试从所有文本中提取
            if not merged_info["peak_price"]:
                final_price_info = self.extract_price_info(all_text)
                if final_price_info["peak_price"]:
                    merged_info["peak_price"] = final_price_info["peak_price"]
                if final_price_info["off_peak_price"]:
                    merged_info["off_peak_price"] = final_price_info["off_peak_price"]
                if final_price_info["phone"] and not merged_info["phone"]:
                    merged_info["phone"] = final_price_info["phone"]
                if final_price_info["address"] and not merged_info["address"]:
                    merged_info["address"] = final_price_info["address"]
            
            return merged_info
            
        except Exception as e:
            logger.error(f"爬取场馆 {court_name} 价格失败: {e}")
            return {
                "peak_price": None,
                "off_peak_price": None,
                "weekend_price": None,
                "price_notes": [],
                "phone": None,
                "address": None,
                "source": "bing_search",
                "error": str(e)
            }
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 