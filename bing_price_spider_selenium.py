#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BING多关键字价格爬取脚本 - Selenium版本
使用真实的BING搜索来爬取场馆价格信息
"""

import os
import sys
import json
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

# Selenium相关导入
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bing_price_spider_selenium.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BingPriceSpiderSelenium:
    """BING价格爬取器 - Selenium版本"""
    
    def __init__(self, headless: bool = True):
        self.db = next(get_db())
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 禁用图片加载以提高速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome驱动初始化成功")
        except Exception as e:
            logger.error(f"Chrome驱动初始化失败: {e}")
            raise
    
    def close_driver(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome驱动已关闭")
    
    def get_courts_without_any_prices(self) -> list:
        """
        获取主表和详情表都没有价格缓存的场馆，自动补建详情表
        """
        courts = self.db.query(TennisCourt).all()
        result = []
        for court in courts:
            # 主表价格字段
            has_main_price = bool(court.peak_price or court.off_peak_price or court.member_price)
            # 详情表价格字段
            detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                # 自动补建详情表
                detail = CourtDetail(court_id=court.id)
                self.db.add(detail)
                self.db.commit()
                self.db.refresh(detail)
                logger.info(f"为场馆 {court.name} 补建详情表: detail_id={detail.id}")
            
            has_detail_price = False
            if detail:
                for field in [detail.dianping_prices, detail.meituan_prices, detail.merged_prices, detail.bing_prices]:
                    try:
                        if field:
                            price_data = json.loads(field)
                            if price_data and len(price_data) > 0:
                                has_detail_price = True
                    except:
                        continue
            if not has_main_price and not has_detail_price:
                result.append({
                    'court_id': court.id,
                    'court_name': court.name,
                    'court_address': court.address,
                    'detail_id': detail.id if detail else None
                })
        logger.info(f"找到 {len(result)} 个主表和详情表都没有价格缓存的场馆")
        return result
    
    def generate_search_keywords(self, court_name: str) -> List[str]:
        """生成搜索关键词"""
        # 清理场馆名称，移除括号内容
        clean_name = re.sub(r'\([^)]*\)', '', court_name).strip()
        
        keywords = [
            f"{clean_name} 网球价格",
            f"{clean_name} 网球预订",
            f"{clean_name} 网球费用",
            f"{clean_name} 网球收费",
            f"{clean_name} 价格",
            f"{clean_name} 预订",
            f"{clean_name} 收费标准"
        ]
        return keywords
    
    def search_bing(self, keyword: str) -> List[Dict]:
        """在BING中搜索关键词并提取价格信息"""
        try:
            # 构建BING搜索URL
            search_url = f"https://www.bing.com/search?q={quote_plus(keyword)}"
            self.driver.get(search_url)
            
            # 等待页面加载
            time.sleep(2)
            
            # 查找搜索结果
            search_results = []
            
            # 查找所有搜索结果
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            
            for element in result_elements[:5]:  # 只处理前5个结果
                try:
                    # 获取标题
                    title_element = element.find_element(By.CSS_SELECTOR, "h2 a")
                    title = title_element.get_attribute("textContent").strip()
                    
                    # 获取摘要
                    snippet_element = element.find_element(By.CSS_SELECTOR, ".b_caption p")
                    snippet = snippet_element.get_attribute("textContent").strip()
                    
                    # 获取链接
                    link = title_element.get_attribute("href")
                    
                    search_results.append({
                        "title": title,
                        "snippet": snippet,
                        "link": link
                    })
                    
                except NoSuchElementException:
                    continue
            
            return search_results
            
        except Exception as e:
            logger.error(f"BING搜索失败: {e}")
            return []
    
    def extract_prices_from_text(self, text: str) -> List[Dict]:
        """从文本中提取价格信息"""
        prices = []
        
        # 价格模式匹配
        price_patterns = [
            r'(\d+)[\s\-]*元/小时',
            r'(\d+)[\s\-]*元/时',
            r'(\d+)[\s\-]*元',
            r'¥(\d+)',
            r'￥(\d+)',
            r'(\d+)[\s\-]*块/小时',
            r'(\d+)[\s\-]*块/时'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price_value = int(match)
                    if 20 <= price_value <= 500:  # 合理的价格范围
                        prices.append({
                            "price": f"¥{price_value}/小时",
                            "value": price_value,
                            "pattern": pattern
                        })
                except ValueError:
                    continue
        
        # 去重
        unique_prices = []
        seen_values = set()
        for price in prices:
            if price["value"] not in seen_values:
                unique_prices.append(price)
                seen_values.add(price["value"])
        
        return unique_prices
    
    def crawl_bing_prices(self, court_data: Dict) -> Dict:
        """爬取单个场馆的BING价格"""
        try:
            court_name = court_data['court_name']
            logger.info(f"开始爬取场馆价格: {court_name}")
            
            # 生成搜索关键词
            keywords = self.generate_search_keywords(court_name)
            
            all_prices = []
            
            for keyword in keywords[:3]:  # 只处理前3个关键词
                logger.info(f"搜索关键词: {keyword}")
                
                # 搜索BING
                search_results = self.search_bing(keyword)
                
                # 从搜索结果中提取价格
                for result in search_results:
                    # 从标题和摘要中提取价格
                    title_prices = self.extract_prices_from_text(result["title"])
                    snippet_prices = self.extract_prices_from_text(result["snippet"])
                    
                    for price in title_prices + snippet_prices:
                        price_info = {
                            "type": self.classify_price_type(price["price"], result["title"]),
                            "price": price["price"],
                            "source": "BING",
                            "keyword": keyword,
                            "confidence": 0.7,
                            "title": result["title"],
                            "link": result["link"]
                        }
                        all_prices.append(price_info)
                
                # 避免请求过快
                time.sleep(1)
            
            # 去重和排序
            unique_prices = self.deduplicate_prices(all_prices)
            
            # 更新缓存
            success = self.update_price_cache(court_data['detail_id'], unique_prices)
            
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": success,
                "prices": unique_prices,
                "keywords_used": keywords[:3]
            }
            
        except Exception as e:
            logger.error(f"爬取场馆 {court_name} 价格失败: {e}")
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": False,
                "error": str(e)
            }
    
    def classify_price_type(self, price: str, title: str) -> str:
        """分类价格类型"""
        title_lower = title.lower()
        price_lower = price.lower()
        
        if any(k in title_lower for k in ['黄金', '高峰', 'peak', '黄金时间']):
            return "黄金时间价格"
        elif any(k in title_lower for k in ['非黄金', '非高峰', 'off', '非黄金时间']):
            return "非黄金时间价格"
        elif any(k in title_lower for k in ['会员', 'vip']):
            return "会员价格"
        elif any(k in title_lower for k in ['学生', 'student']):
            return "学生价格"
        else:
            return "标准价格"
    
    def deduplicate_prices(self, prices: List[Dict]) -> List[Dict]:
        """去重价格信息"""
        unique_prices = []
        seen_prices = set()
        
        for price in prices:
            price_key = f"{price['type']}_{price['price']}"
            if price_key not in seen_prices:
                unique_prices.append(price)
                seen_prices.add(price_key)
        
        # 按价格值排序
        unique_prices.sort(key=lambda x: x.get('price', ''))
        
        return unique_prices
    
    def update_price_cache(self, detail_id: int, prices: List[Dict]) -> bool:
        """更新价格缓存"""
        try:
            detail = self.db.query(CourtDetail).filter(CourtDetail.id == detail_id).first()
            if detail:
                # 只更新BING价格缓存，不动其他字段
                detail.bing_prices = json.dumps(prices, ensure_ascii=False)
                detail.updated_at = datetime.now()
                
                self.db.commit()
                logger.info(f"成功更新价格缓存: detail_id={detail_id}, 价格数量: {len(prices)}")
                return True
            else:
                logger.warning(f"未找到详情记录: detail_id={detail_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新价格缓存失败: {e}")
            self.db.rollback()
            return False
    
    def batch_crawl_prices(self, max_workers: int = 1, limit: int = 50) -> dict:
        """批量爬取价格"""
        start_time = datetime.now()
        logger.info(f"开始批量BING价格爬取，限制: {limit}，并发数: {max_workers}")
        
        # 设置驱动
        self.setup_driver()
        
        try:
            courts = self.get_courts_without_any_prices()
            if not courts:
                logger.info("没有需要爬取价格的场馆")
                return {"success": True, "message": "没有需要爬取的场馆"}
            
            courts = courts[:limit]
            results = []
            
            # 由于Selenium的限制，使用单线程
            for court in courts:
                result = self.crawl_bing_prices(court)
                results.append(result)
                logger.info(f"完成: {result['court_name']} - {'成功' if result['success'] else '失败'}")
                
                # 避免请求过快
                time.sleep(2)
            
            success_count = sum(1 for r in results if r['success'])
            failed_count = len(results) - success_count
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            summary = {
                "success": True,
                "total_courts": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "duration_seconds": duration,
                "results": results
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bing_price_results_selenium_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"结果已保存到: {filename}")
            return summary
            
        finally:
            self.close_driver()

def main():
    """主函数"""
    spider = BingPriceSpiderSelenium(headless=True)
    
    # 批量爬取价格 - 限制数量避免过度请求
    result = spider.batch_crawl_prices(max_workers=1, limit=20)
    
    print(f"\n=== BING价格爬取完成 ===")
    print(f"总场馆数: {result['total_courts']}")
    print(f"成功数: {result['success_count']}")
    print(f"失败数: {result['failed_count']}")
    print(f"耗时: {result['duration_seconds']:.2f}秒")

if __name__ == "__main__":
    main() 