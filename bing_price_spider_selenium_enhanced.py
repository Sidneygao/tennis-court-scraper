#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BING多关键字价格爬取脚本 - 增强版
优化策略以获取更多数据，集成置信度模型
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
from app.scrapers.price_confidence_model import confidence_model

# Selenium相关导入
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BingPriceSpiderEnhanced:
    """增强版BING价格爬虫"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.db = next(get_db())
        
        # 初始化置信度模型
        logger.info("🔄 初始化价格置信度模型...")
        confidence_model.build_normal_distribution_models()
        model_info = confidence_model.get_model_info()
        logger.info(f"✅ 置信度模型初始化完成:")
        for model_name, model_data in model_info.items():
            if model_data:
                logger.info(f"  {model_name}: 均值={model_data['mean']:.1f}, 标准差={model_data['std']:.1f}, 样本数={model_data['count']}")
    
    def setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # 添加更多反检测参数
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def close_driver(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
    
    def get_courts_for_enhanced_crawl(self) -> list:
        """
        获取需要增强爬取的场馆：
        1. 完全没有BING价格数据的场馆
        2. 只有预测价格但无BING价格的场馆
        """
        courts = self.db.query(TennisCourt).all()
        result = []
        
        for court in courts:
            # 检查详情表
            detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                detail = CourtDetail(court_id=court.id)
                self.db.add(detail)
                self.db.commit()
                self.db.refresh(detail)
            
            # 检查BING价格数据
            has_bing_prices = False
            bing_price_count = 0
            
            if detail and detail.bing_prices:
                try:
                    bing_data = json.loads(detail.bing_prices)
                    if isinstance(bing_data, list) and len(bing_data) > 0:
                        has_bing_prices = True
                        bing_price_count = len(bing_data)
                except:
                    pass
            
            # 只爬取没有BING价格数据的场馆
            if not has_bing_prices:
                result.append({
                    'court_id': court.id,
                    'court_name': court.name,
                    'court_address': court.address,
                    'court_type': court.court_type or '',
                    'detail_id': detail.id if detail else None,
                    'price_status': {
                        'has_bing_prices': has_bing_prices,
                        'bing_price_count': bing_price_count
                    }
                })
        
        logger.info(f"找到 {len(result)} 个需要增强爬取的场馆（无BING价格数据）")
        return result
    
    def generate_enhanced_keywords(self, court_name: str, court_address: str) -> List[str]:
        """生成增强版搜索关键词"""
        # 清理场馆名称
        clean_name = re.sub(r'\([^)]*\)', '', court_name).strip()
        
        # 提取地址关键词
        address_keywords = []
        if court_address:
            # 提取区域信息
            area_patterns = [r'([^区]+区)', r'([^路]+路)', r'([^街]+街)']
            for pattern in area_patterns:
                matches = re.findall(pattern, court_address)
                address_keywords.extend(matches)
        
        # 基础关键词
        base_keywords = [
            f"{clean_name} 网球价格",
            f"{clean_name} 网球预订",
            f"{clean_name} 网球费用",
            f"{clean_name} 网球收费",
            f"{clean_name} 价格",
            f"{clean_name} 预订",
            f"{clean_name} 收费标准",
            f"{clean_name} 会员价格",
            f"{clean_name} 学生价格"
        ]
        
        # 地址相关关键词
        address_keywords = []
        if court_address:
            for area in address_keywords[:2]:  # 最多2个地址关键词
                address_keywords.extend([
                    f"{clean_name} {area} 网球价格",
                    f"{area} {clean_name} 价格",
                    f"{clean_name} {area} 预订"
                ])
        
        # 组合关键词
        all_keywords = base_keywords + address_keywords
        
        # 去重并限制数量
        unique_keywords = list(dict.fromkeys(all_keywords))
        return unique_keywords[:8]  # 最多8个关键词
    
    def search_bing_enhanced(self, keyword: str) -> List[Dict]:
        """增强版BING搜索"""
        try:
            search_url = f"https://www.bing.com/search?q={quote_plus(keyword)}&count=20"
            self.driver.get(search_url)
            
            # 等待页面加载
            time.sleep(2)
            
            # 尝试滚动页面获取更多结果
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            search_results = []
            
            # 查找更多类型的结果
            selectors = [
                "li.b_algo",  # 普通搜索结果
                ".b_attribution cite",  # 新闻结果
                ".b_caption p",  # 摘要
                ".b_attribution"  # 来源信息
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:10]:  # 每个类型最多10个
                        try:
                            text = element.get_attribute("textContent").strip()
                            if text and len(text) > 10:
                                search_results.append({
                                    "title": keyword,
                                    "snippet": text,
                                    "link": "",
                                    "type": selector
                                })
                        except:
                            continue
                except:
                    continue
            
            return search_results[:15]  # 最多15个结果
            
        except Exception as e:
            logger.error(f"BING搜索失败: {e}")
            return []
    
    def extract_prices_enhanced(self, text: str, court_name: str = "", court_type: str = "") -> List[Dict]:
        """增强版价格提取，集成置信度计算"""
        prices = []
        
        # 扩展价格模式
        price_patterns = [
            r'(\d+)[\s\-]*元/小时',
            r'(\d+)[\s\-]*元/时',
            r'(\d+)[\s\-]*元',
            r'¥(\d+)',
            r'￥(\d+)',
            r'(\d+)[\s\-]*块/小时',
            r'(\d+)[\s\-]*块/时',
            r'(\d+)[\s\-]*元/场',
            r'(\d+)[\s\-]*元/次',
            r'(\d+)[\s\-]*元/人',
            r'(\d+)[\s\-]*元/天',
            r'(\d+)[\s\-]*元/月',
            r'(\d+)[\s\-]*元/年',
            r'(\d+)[\s\-]*元/会员',
            r'(\d+)[\s\-]*元/学生'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price_value = int(match)
                    # 放宽价格范围
                    if 10 <= price_value <= 2000:
                        # 根据模式推断价格类型
                        price_type = "标准价格"
                        if "会员" in pattern:
                            price_type = "会员价格"
                        elif "学生" in pattern:
                            price_type = "学生价格"
                        elif "场" in pattern or "次" in pattern:
                            price_type = "按场次价格"
                        elif "天" in pattern:
                            price_type = "日租价格"
                        elif "月" in pattern or "年" in pattern:
                            price_type = "长期价格"
                        
                        # 计算置信度
                        confidence = confidence_model.calculate_confidence(
                            price_value, court_type, court_name, price_type
                        )
                        
                        prices.append({
                            "price": f"¥{price_value}/小时",
                            "value": price_value,
                            "pattern": pattern,
                            "type": price_type,
                            "confidence": confidence
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
    
    def crawl_bing_prices_enhanced(self, court_data: Dict) -> Dict:
        """增强版单个场馆价格爬取"""
        try:
            court_name = court_data['court_name']
            court_address = court_data['court_address']
            court_type = court_data.get('court_type', '')
            logger.info(f"开始增强爬取场馆价格: {court_name}")
            
            # 生成增强关键词
            keywords = self.generate_enhanced_keywords(court_name, court_address)
            
            all_prices = []
            found_prices_count = 0
            
            print(f"\n🎾 正在爬取: {court_name}")
            print(f"📍 地址: {court_address}")
            print(f"🔍 使用关键词: {len(keywords)} 个")
            
            for i, keyword in enumerate(keywords, 1):
                print(f"\n  [{i}/{len(keywords)}] 搜索: {keyword}")
                
                # 搜索BING
                search_results = self.search_bing_enhanced(keyword)
                print(f"     📄 找到 {len(search_results)} 个搜索结果")
                
                # 提取价格
                keyword_prices = []
                for result in search_results:
                    snippet_prices = self.extract_prices_enhanced(
                        result["snippet"], court_name, court_type
                    )
                    
                    for price in snippet_prices:
                        price_info = {
                            "type": price.get("type", "标准价格"),
                            "price": price["price"],
                            "source": "BING",
                            "keyword": keyword,
                            "confidence": price.get("confidence", 0.8),
                            "title": result["title"],
                            "link": result.get("link", ""),
                            "extracted_from": result.get("type", "snippet")
                        }
                        all_prices.append(price_info)
                        keyword_prices.append(price_info)
                
                # 动态显示当前关键词找到的价格
                if keyword_prices:
                    print(f"     💰 提取到 {len(keyword_prices)} 个价格:")
                    for price in keyword_prices:
                        confidence_str = f"{price['confidence']:.2f}"
                        print(f"       • {price['price']} ({price['type']}) - 置信度: {confidence_str}")
                    found_prices_count += len(keyword_prices)
                else:
                    print(f"     ❌ 未找到有效价格")
                
                # 避免请求过快
                time.sleep(1.5)
            
            # 去重和排序
            unique_prices = self.deduplicate_prices_enhanced(all_prices)
            
            # 动态显示最终结果
            print(f"\n📊 爬取结果汇总:")
            print(f"   🔍 搜索关键词: {len(keywords)} 个")
            print(f"   📄 总搜索结果: {sum(len(self.search_bing_enhanced(k)) for k in keywords)} 个")
            print(f"   💰 原始价格数: {found_prices_count} 个")
            print(f"   ✅ 去重后价格: {len(unique_prices)} 个")
            
            if unique_prices:
                print(f"   📋 有效价格列表 (按置信度排序):")
                for i, price in enumerate(unique_prices[:5], 1):  # 只显示前5个
                    confidence_str = f"{price['confidence']:.2f}"
                    print(f"     {i}. {price['price']} ({price['type']}) - 置信度: {confidence_str} - 来源: {price['keyword']}")
                if len(unique_prices) > 5:
                    print(f"     ... 还有 {len(unique_prices) - 5} 个价格")
            else:
                print(f"   ❌ 未找到有效价格")
            
            # 更新缓存
            success = self.update_price_cache_enhanced(court_data['detail_id'], unique_prices)
            
            if success:
                print(f"   💾 缓存更新: {'成功' if success else '失败'}")
            else:
                print(f"   ❌ 缓存更新失败")
            
            print(f"   {'✅' if success else '❌'} 场馆 {court_name} 爬取{'完成' if success else '失败'}")
            
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": success,
                "prices": unique_prices,
                "keywords_used": keywords,
                "price_status": court_data['price_status'],
                "stats": {
                    "keywords_count": len(keywords),
                    "raw_prices_count": found_prices_count,
                    "unique_prices_count": len(unique_prices)
                }
            }
            
        except Exception as e:
            logger.error(f"增强爬取场馆 {court_name} 价格失败: {e}")
            print(f"   ❌ 爬取失败: {e}")
            return {
                "court_id": court_data['court_id'],
                "court_name": court_name,
                "success": False,
                "error": str(e)
            }
    
    def deduplicate_prices_enhanced(self, prices: List[Dict]) -> List[Dict]:
        """增强版价格去重，按置信度排序"""
        unique_prices = []
        seen_prices = set()
        
        for price in prices:
            # 更精确的去重键
            price_key = f"{price['type']}_{price['price']}_{price.get('keyword', '')}"
            if price_key not in seen_prices:
                unique_prices.append(price)
                seen_prices.add(price_key)
        
        # 按置信度排序（置信度高的在前）
        unique_prices.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return unique_prices
    
    def update_price_cache_enhanced(self, detail_id: int, prices: List[Dict]) -> bool:
        """增强版价格缓存更新"""
        try:
            detail = self.db.query(CourtDetail).filter(CourtDetail.id == detail_id).first()
            if detail:
                # 合并现有BING价格和新价格
                existing_prices = []
                if detail.bing_prices:
                    try:
                        existing_prices = json.loads(detail.bing_prices)
                    except:
                        pass
                
                # 合并价格，避免重复
                all_prices = existing_prices + prices
                unique_prices = self.deduplicate_prices_enhanced(all_prices)
                
                detail.bing_prices = json.dumps(unique_prices, ensure_ascii=False)
                detail.updated_at = datetime.now()
                
                self.db.commit()
                logger.info(f"成功更新增强价格缓存: detail_id={detail_id}, 价格数量: {len(unique_prices)}")
                return True
            else:
                logger.warning(f"未找到详情记录: detail_id={detail_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新增强价格缓存失败: {e}")
            self.db.rollback()
            return False
    
    def batch_crawl_prices_enhanced(self, limit: int = 100) -> dict:
        """增强版批量爬取"""
        start_time = datetime.now()
        logger.info(f"开始增强版BING价格爬取，限制: {limit}")
        
        print(f"\n🚀 开始增强版BING价格爬取")
        print(f"📊 限制数量: {limit}")
        print(f"⏰ 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 设置驱动
        self.setup_driver()
        
        try:
            courts = self.get_courts_for_enhanced_crawl()
            if not courts:
                logger.info("没有需要增强爬取价格的场馆")
                print("❌ 没有需要爬取的场馆")
                return {"success": True, "message": "没有需要爬取的场馆"}
            
            courts = courts[:limit]
            results = []
            
            # 实时统计
            total_success = 0
            total_failed = 0
            total_prices_found = 0
            
            print(f"🎯 找到 {len(courts)} 个需要爬取的场馆")
            print("=" * 60)
            
            for i, court in enumerate(courts):
                print(f"\n{'='*20} 第 {i+1}/{len(courts)} 个场馆 {'='*20}")
                
                result = self.crawl_bing_prices_enhanced(court)
                results.append(result)
                
                # 更新统计
                if result['success']:
                    total_success += 1
                    prices_count = len(result.get('prices', []))
                    total_prices_found += prices_count
                    print(f"✅ 成功! 找到 {prices_count} 个价格")
                else:
                    total_failed += 1
                    print(f"❌ 失败: {result.get('error', '未知错误')}")
                
                # 显示实时统计
                print(f"\n📈 实时统计:")
                print(f"   ✅ 成功: {total_success}/{i+1}")
                print(f"   ❌ 失败: {total_failed}/{i+1}")
                print(f"   💰 总价格: {total_prices_found} 个")
                print(f"   📊 成功率: {total_success/(i+1)*100:.1f}%")
                
                # 避免请求过快
                time.sleep(2)
                
                # 每10个请求后稍作休息
                if (i + 1) % 10 == 0:
                    print(f"\n⏸️  已完成 {i+1} 个场馆，休息5秒...")
                    time.sleep(5)
            
            success_count = sum(1 for r in results if r['success'])
            failed_count = len(results) - success_count
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 最终统计
            print(f"\n{'='*60}")
            print(f"🎉 增强版BING价格爬取完成!")
            print(f"{'='*60}")
            print(f"📊 最终统计:")
            print(f"   🎯 总场馆数: {len(results)}")
            print(f"   ✅ 成功数: {success_count}")
            print(f"   ❌ 失败数: {failed_count}")
            print(f"   💰 总价格数: {total_prices_found}")
            print(f"   📈 成功率: {success_count/len(results)*100:.1f}%")
            print(f"   ⏱️  总耗时: {duration:.1f}秒")
            print(f"   🚀 平均速度: {len(results)/duration*60:.1f}个/分钟")
            
            # 价格分布统计
            price_types = {}
            for result in results:
                if result['success']:
                    for price in result.get('prices', []):
                        price_type = price.get('type', '未知')
                        price_types[price_type] = price_types.get(price_type, 0) + 1
            
            if price_types:
                print(f"\n💰 价格类型分布:")
                for price_type, count in sorted(price_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {price_type}: {count} 个")
            
            summary = {
                "success": True,
                "total_courts": len(results),
                "success_count": success_count,
                "failed_count": failed_count,
                "total_prices_found": total_prices_found,
                "duration_seconds": duration,
                "success_rate": success_count/len(results)*100 if results else 0,
                "speed_per_minute": len(results)/duration*60 if duration > 0 else 0,
                "price_type_distribution": price_types,
                "results": results
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bing_price_results_enhanced_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"增强版结果已保存到: {filename}")
            print(f"💾 结果已保存到: {filename}")
            
            return summary
            
        finally:
            self.close_driver()

def main():
    """主函数"""
    spider = BingPriceSpiderEnhanced(headless=True)
    
    # 增强版批量爬取价格 - 爬取所有需要爬取的场馆
    result = spider.batch_crawl_prices_enhanced(limit=1000)  # 设置足够大的限制
    
    print(f"\n=== 增强版BING价格爬取完成 ===")
    print(f"总场馆数: {result['total_courts']}")
    print(f"成功数: {result['success_count']}")
    print(f"失败数: {result['failed_count']}")
    print(f"耗时: {result['duration_seconds']:.2f}秒")

if __name__ == "__main__":
    main() 