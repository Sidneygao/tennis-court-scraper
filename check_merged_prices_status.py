#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查合并价格状态：分析Bing爬取的价格数据是否已正确合并到数据库中
"""
import json
import sqlite3
from collections import defaultdict

def main():
    print("🔍 检查合并价格状态...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 检查数据库中的价格字段
    print("\n📊 数据库价格字段统计:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL AND cd.merged_prices != '' THEN 1 ELSE 0 END) as has_merged_prices,
            SUM(CASE WHEN cd.bing_prices IS NOT NULL AND cd.bing_prices != '' THEN 1 ELSE 0 END) as has_bing_prices,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL AND cd.predict_prices != '' THEN 1 ELSE 0 END) as has_predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    stats = cursor.fetchone()
    print(f"  总场馆数: {stats[0]}")
    print(f"  有合并价格: {stats[1]}")
    print(f"  有Bing价格: {stats[2]}")
    print(f"  有预测价格: {stats[3]}")
    
    # 2. 检查Bing价格数据
    print("\n🔍 检查Bing价格数据:")
    cursor.execute("""
        SELECT tc.id, tc.name, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != ''
        LIMIT 10
    """)
    
    bing_samples = cursor.fetchall()
    print(f"找到 {len(bing_samples)} 个有Bing价格的场馆样本")
    
    for court_id, name, bing_data in bing_samples:
        print(f"\n🏟️ 场馆: {name} (ID: {court_id})")
        try:
            bing_prices = json.loads(bing_data)
            if isinstance(bing_prices, list):
                print(f"  Bing价格: {len(bing_prices)} 个")
                for item in bing_prices:
                    if isinstance(item, dict):
                        price_type = item.get('type', '')
                        price_str = item.get('price', '')
                        confidence = item.get('confidence', 0)
                        print(f"    - {price_type}: {price_str} (置信度: {confidence})")
        except:
            print(f"  Bing价格: 解析失败")
    
    # 3. 检查合并价格数据
    print("\n🔍 检查合并价格数据:")
    cursor.execute("""
        SELECT tc.id, tc.name, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL AND cd.merged_prices != ''
        LIMIT 10
    """)
    
    merged_samples = cursor.fetchall()
    print(f"找到 {len(merged_samples)} 个有合并价格的场馆样本")
    
    for court_id, name, merged_data in merged_samples:
        print(f"\n🏟️ 场馆: {name} (ID: {court_id})")
        try:
            merged_prices = json.loads(merged_data)
            if isinstance(merged_prices, list):
                print(f"  合并价格: {len(merged_prices)} 个")
                for item in merged_prices:
                    if isinstance(item, dict):
                        price_type = item.get('type', '')
                        price_str = item.get('price', '')
                        is_predicted = item.get('is_predicted', False)
                        confidence = item.get('confidence', 0)
                        print(f"    - {price_type}: {price_str} (预测: {is_predicted}, 置信度: {confidence})")
        except:
            print(f"  合并价格: 解析失败")
    
    # 4. 检查价格数据完整性
    print("\n📈 价格数据完整性分析:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN cd.bing_prices IS NOT NULL AND cd.bing_prices != '' THEN 1 ELSE 0 END) as has_bing,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL AND cd.merged_prices != '' THEN 1 ELSE 0 END) as has_merged,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL AND cd.predict_prices != '' THEN 1 ELSE 0 END) as has_predict,
            SUM(CASE WHEN (cd.bing_prices IS NOT NULL AND cd.bing_prices != '') OR 
                        (cd.merged_prices IS NOT NULL AND cd.merged_prices != '') OR
                        (cd.predict_prices IS NOT NULL AND cd.predict_prices != '') THEN 1 ELSE 0 END) as has_any_price
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    completeness = cursor.fetchone()
    print(f"  总场馆数: {completeness[0]}")
    print(f"  有Bing价格: {completeness[1]} ({completeness[1]/completeness[0]*100:.1f}%)")
    print(f"  有合并价格: {completeness[2]} ({completeness[2]/completeness[0]*100:.1f}%)")
    print(f"  有预测价格: {completeness[3]} ({completeness[3]/completeness[0]*100:.1f}%)")
    print(f"  有任何价格: {completeness[4]} ({completeness[4]/completeness[0]*100:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    main() 