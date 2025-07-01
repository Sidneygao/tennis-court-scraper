#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查真实价格的状态
"""
import sqlite3
import json

def main():
    print("🔍 检查真实价格状态...")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查真实价格状态
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE prices IS NOT NULL AND prices != ''")
    with_real_prices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE prices IS NULL OR prices = ''")
    without_real_prices = cursor.fetchone()[0]
    
    # 检查BING价格状态
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE bing_prices IS NOT NULL AND bing_prices != ''")
    with_bing_prices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE bing_prices IS NULL OR bing_prices = ''")
    without_bing_prices = cursor.fetchone()[0]
    
    # 检查合并价格状态
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE merged_prices IS NOT NULL AND merged_prices != ''")
    with_merged_prices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE merged_prices IS NULL OR merged_prices = ''")
    without_merged_prices = cursor.fetchone()[0]
    
    print(f"\n📊 价格数据状态统计:")
    print(f"   真实价格 (prices):")
    print(f"     有数据: {with_real_prices} 个")
    print(f"     无数据: {without_real_prices} 个")
    
    print(f"   BING价格 (bing_prices):")
    print(f"     有数据: {with_bing_prices} 个")
    print(f"     无数据: {without_bing_prices} 个")
    
    print(f"   合并价格 (merged_prices):")
    print(f"     有数据: {with_merged_prices} 个")
    print(f"     无数据: {without_merged_prices} 个")
    
    print(f"   预测价格 (predict_prices):")
    print(f"     有数据: 241 个")
    print(f"     无数据: 0 个")
    
    # 检查有真实价格的场馆示例
    if with_real_prices > 0:
        print(f"\n🔍 有真实价格的场馆示例:")
        cursor.execute("""
            SELECT tc.id, tc.name, cd.prices
            FROM tennis_courts tc
            JOIN court_details cd ON tc.id = cd.court_id
            WHERE cd.prices IS NOT NULL AND cd.prices != ''
            LIMIT 5
        """)
        real_price_examples = cursor.fetchall()
        
        for i, (court_id, name, prices) in enumerate(real_price_examples):
            try:
                prices_data = json.loads(prices)
                print(f"   {i+1}. {name} (ID: {court_id})")
                print(f"      价格数据: {prices_data}")
            except:
                print(f"   {i+1}. {name} (ID: {court_id}) - 价格数据格式错误")
    
    # 检查有BING价格的场馆示例
    if with_bing_prices > 0:
        print(f"\n🔍 有BING价格的场馆示例:")
        cursor.execute("""
            SELECT tc.id, tc.name, cd.bing_prices
            FROM tennis_courts tc
            JOIN court_details cd ON tc.id = cd.court_id
            WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != ''
            LIMIT 3
        """)
        bing_price_examples = cursor.fetchall()
        
        for i, (court_id, name, bing_prices) in enumerate(bing_price_examples):
            try:
                bing_data = json.loads(bing_prices)
                print(f"   {i+1}. {name} (ID: {court_id})")
                print(f"      BING数据: {bing_data}")
            except:
                print(f"   {i+1}. {name} (ID: {court_id}) - BING数据格式错误")
    
    conn.close()
    
    print(f"\n✅ 检查完成！")
    if with_real_prices == 0:
        print(f"   ⚠️  警告: 没有找到真实价格数据！")
        print(f"   可能原因:")
        print(f"   1. 真实价格数据被清空")
        print(f"   2. 真实价格字段名变更")
        print(f"   3. 数据迁移过程中丢失")

if __name__ == "__main__":
    main() 