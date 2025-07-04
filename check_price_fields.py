#!/usr/bin/env python3
"""
彻查后台价格字段逻辑
"""

import sqlite3
import json

def check_price_fields():
    """彻查后台价格字段逻辑"""
    db_path = "data/courts.db"
    
    print("💰 彻查后台价格字段逻辑...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有详情记录的价格字段
        cursor.execute("""
            SELECT id, court_id, 
                   prices, dianping_prices, meituan_prices, 
                   merged_prices, predict_prices, bing_prices
            FROM court_details 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print(f"📊 检查前10条记录的价格字段:")
        
        for detail_id, court_id, prices, dianping_prices, meituan_prices, merged_prices, predict_prices, bing_prices in rows:
            print(f"\n--- 详情ID: {detail_id}, 场馆ID: {court_id} ---")
            
            # 解析各个价格字段
            def parse_prices(field_name, price_data):
                if not price_data:
                    print(f"  {field_name}: 空")
                    return []
                try:
                    parsed = json.loads(price_data)
                    print(f"  {field_name}: {parsed}")
                    return parsed
                except:
                    print(f"  {field_name}: JSON解析失败 - {price_data}")
                    return []
            
            parse_prices("prices", prices)
            parse_prices("dianping_prices", dianping_prices)
            parse_prices("meituan_prices", meituan_prices)
            parse_prices("merged_prices", merged_prices)
            parse_prices("predict_prices", predict_prices)
            parse_prices("bing_prices", bing_prices)
        
        # 统计各字段的非空记录数
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN prices IS NOT NULL AND prices != '' THEN 1 ELSE 0 END) as prices_count,
                SUM(CASE WHEN dianping_prices IS NOT NULL AND dianping_prices != '' THEN 1 ELSE 0 END) as dianping_count,
                SUM(CASE WHEN meituan_prices IS NOT NULL AND meituan_prices != '' THEN 1 ELSE 0 END) as meituan_count,
                SUM(CASE WHEN merged_prices IS NOT NULL AND merged_prices != '' THEN 1 ELSE 0 END) as merged_count,
                SUM(CASE WHEN predict_prices IS NOT NULL AND predict_prices != '' THEN 1 ELSE 0 END) as predict_count,
                SUM(CASE WHEN bing_prices IS NOT NULL AND bing_prices != '' THEN 1 ELSE 0 END) as bing_count
            FROM court_details
        """)
        
        stats = cursor.fetchone()
        print(f"\n📈 价格字段统计:")
        print(f"  总记录数: {stats[0]}")
        print(f"  prices: {stats[1]}")
        print(f"  dianping_prices: {stats[2]}")
        print(f"  meituan_prices: {stats[3]}")
        print(f"  merged_prices: {stats[4]}")
        print(f"  predict_prices: {stats[5]}")
        print(f"  bing_prices: {stats[6]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_price_fields() 