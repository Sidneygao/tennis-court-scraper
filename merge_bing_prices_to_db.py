#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将BING爬取的价格数据合并到数据库的bing_prices字段中
"""
import json
import sqlite3
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_bing_prices_to_db():
    """将BING价格数据合并到数据库"""
    logger.info("🔄 开始合并BING价格数据到数据库...")
    
    # 读取最新的BING爬取结果
    bing_file = "bing_price_results_enhanced_20250629_175521.json"
    
    try:
        with open(bing_file, 'r', encoding='utf-8') as f:
            bing_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ 找不到BING结果文件: {bing_file}")
        return
    except json.JSONDecodeError:
        logger.error(f"❌ BING结果文件格式错误: {bing_file}")
        return
    
    logger.info(f"📊 BING数据统计:")
    logger.info(f"   总场馆数: {bing_data.get('total_courts', 0)}")
    logger.info(f"   成功数: {bing_data.get('success_count', 0)}")
    logger.info(f"   总价格数: {bing_data.get('total_prices_found', 0)}")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 统计变量
    total_updated = 0
    total_prices = 0
    
    # 处理每个场馆的价格数据
    for result in bing_data.get('results', []):
        court_id = result.get('court_id')
        court_name = result.get('court_name')
        prices = result.get('prices', [])
        
        if not prices:
            continue
        
        # 去重价格数据
        unique_prices = []
        seen_prices = set()
        
        for price_item in prices:
            price_str = price_item.get('price', '')
            if price_str and price_str not in seen_prices:
                seen_prices.add(price_str)
                unique_prices.append(price_item)
        
        if not unique_prices:
            continue
        
        # 更新数据库
        try:
            # 检查是否已有bing_prices数据
            cursor.execute("""
                SELECT bing_prices FROM court_details 
                WHERE court_id = ?
            """, (court_id,))
            
            existing_data = cursor.fetchone()
            
            if existing_data and existing_data[0]:
                # 合并现有数据
                try:
                    existing_prices = json.loads(existing_data[0])
                    if isinstance(existing_prices, list):
                        # 合并并去重
                        all_prices = existing_prices + unique_prices
                        seen = set()
                        merged_prices = []
                        for p in all_prices:
                            price_key = p.get('price', '')
                            if price_key and price_key not in seen:
                                seen.add(price_key)
                                merged_prices.append(p)
                        final_prices = merged_prices
                    else:
                        final_prices = unique_prices
                except:
                    final_prices = unique_prices
            else:
                final_prices = unique_prices
            
            # 更新bing_prices字段
            cursor.execute("""
                UPDATE court_details 
                SET bing_prices = ?, updated_at = ?
                WHERE court_id = ?
            """, (json.dumps(final_prices, ensure_ascii=False), datetime.now(), court_id))
            
            total_updated += 1
            total_prices += len(final_prices)
            
            logger.info(f"✅ 更新场馆 {court_name} (ID: {court_id}): {len(final_prices)} 个价格")
            
        except Exception as e:
            logger.error(f"❌ 更新场馆 {court_name} (ID: {court_id}) 失败: {e}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    logger.info("🎉 BING价格数据合并完成!")
    logger.info(f"📊 最终统计:")
    logger.info(f"   更新场馆数: {total_updated}")
    logger.info(f"   总价格数: {total_prices}")

if __name__ == "__main__":
    merge_bing_prices_to_db() 