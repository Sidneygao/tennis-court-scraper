#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查merged_prices字段内容，输出is_predicted分布
"""
import sqlite3
import json

def main():
    print("🔍 检查merged_prices字段内容...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tc.name, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL AND cd.merged_prices != '' AND cd.merged_prices != '[]'
        LIMIT 10
    """)
    results = cursor.fetchall()
    print(f"  样本数量: {len(results)}")
    for name, prices in results:
        print(f"\n🏟️ 场馆: {name}")
        try:
            price_list = json.loads(prices)
            for i, item in enumerate(price_list):
                print(f"  {i+1}. {item.get('type','')}: {item.get('price','')} | is_predicted: {item.get('is_predicted')} | 来源: {item.get('source')}")
        except Exception as e:
            print(f"  解析失败: {e}")
    conn.close()

if __name__ == "__main__":
    main() 