#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计merged_prices中is_predicted: False的真实价格总数，并输出部分样本
"""
import sqlite3
import json

def main():
    print("🔍 统计merged_prices中真实价格数量...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tc.name, cd.merged_prices FROM tennis_courts tc LEFT JOIN court_details cd ON tc.id = cd.court_id WHERE cd.merged_prices IS NOT NULL AND cd.merged_prices != '' AND cd.merged_prices != '[]'")
    results = cursor.fetchall()
    real_count = 0
    total_count = 0
    samples = []
    for name, prices in results:
        try:
            price_list = json.loads(prices)
            for item in price_list:
                total_count += 1
                if not item.get('is_predicted', True):
                    real_count += 1
                    if len(samples) < 10:
                        samples.append((name, item))
        except Exception as e:
            continue
    print(f"\n✅ merged_prices中真实价格总数: {real_count}")
    print(f"  merged_prices中所有价格项总数: {total_count}")
    print("\n部分真实价格样本:")
    for name, item in samples:
        print(f"🏟️ {name} | {item}")
    conn.close()

if __name__ == "__main__":
    main() 