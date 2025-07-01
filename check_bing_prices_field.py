#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查BING价格数据是否已存储到数据库
"""
import sqlite3
import json

def check_bing_prices():
    """检查BING价格数据"""
    print("🔍 检查BING价格数据存储情况...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查有多少场馆有BING价格数据
    cursor.execute("""
        SELECT COUNT(*) FROM court_details 
        WHERE bing_prices IS NOT NULL 
        AND bing_prices != '' 
        AND bing_prices != '[]'
    """)
    bing_count = cursor.fetchone()[0]
    print(f"有BING价格数据的场馆数: {bing_count}")
    
    # 检查有多少场馆有merged_prices数据
    cursor.execute("""
        SELECT COUNT(*) FROM court_details 
        WHERE merged_prices IS NOT NULL 
        AND merged_prices != '' 
        AND merged_prices != '[]'
    """)
    merged_count = cursor.fetchone()[0]
    print(f"有merged_prices数据的场馆数: {merged_count}")
    
    # 检查几个具体的场馆
    cursor.execute("""
        SELECT tc.name, cd.bing_prices, cd.merged_prices 
        FROM tennis_courts tc 
        LEFT JOIN court_details cd ON tc.id = cd.court_id 
        WHERE cd.bing_prices IS NOT NULL 
        AND cd.bing_prices != '' 
        AND cd.bing_prices != '[]'
        LIMIT 5
    """)
    results = cursor.fetchall()
    
    print(f"\n📊 前5个有BING价格数据的场馆:")
    for name, bing_prices, merged_prices in results:
        print(f"\n🏟️ {name}:")
        print(f"  BING价格数据: {bing_prices[:200]}..." if len(bing_prices) > 200 else f"  BING价格数据: {bing_prices}")
        print(f"  融合价格数据: {merged_prices}")
        
        # 解析BING价格数据
        try:
            bing_data = json.loads(bing_prices)
            if isinstance(bing_data, list):
                print(f"  BING价格数量: {len(bing_data)}")
                for i, price in enumerate(bing_data[:3]):  # 只显示前3个
                    print(f"    价格{i+1}: {price.get('price', 'N/A')} ({price.get('type', 'N/A')})")
        except Exception as e:
            print(f"  BING价格解析失败: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_bing_prices() 