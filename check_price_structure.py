#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查价格数据结构：黄金时段和非黄金时段价格分布
"""
import json
import sqlite3
from collections import defaultdict

def main():
    print("🔍 检查价格数据结构...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 检查真实价格数据结构
    print("\n📊 检查真实价格数据结构:")
    cursor.execute("""
        SELECT tc.name, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL
        LIMIT 10
    """)
    
    real_price_samples = cursor.fetchall()
    print(f"找到 {len(real_price_samples)} 个有真实价格的场馆样本")
    
    peak_count = 0
    offpeak_count = 0
    
    for name, merged in real_price_samples:
        print(f"\n🏟️ 场馆: {name}")
        
        if merged:
            try:
                prices = json.loads(merged)
                if isinstance(prices, list):
                    print(f"  merged: {len(prices)} 个价格项")
                    for item in prices:
                        if isinstance(item, dict):
                            price_type = item.get('type', '').lower()
                            price_str = item.get('price', '')
                            print(f"    - {price_type}: {price_str}")
                            
                            # 统计黄金/非黄金
                            if any(k in price_type for k in ['黄金', '高峰', 'peak', '黄金时间']):
                                peak_count += 1
                            elif any(k in price_type for k in ['非黄金', '非高峰', 'off', '非黄金时间']):
                                offpeak_count += 1
            except:
                print(f"  merged: 解析失败")
    
    print(f"\n📈 真实价格统计:")
    print(f"  黄金时段价格: {peak_count} 个")
    print(f"  非黄金时段价格: {offpeak_count} 个")
    
    # 2. 检查预测价格数据结构
    print("\n🔮 检查预测价格数据结构:")
    cursor.execute("""
        SELECT tc.name, cd.predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.predict_prices IS NOT NULL
        LIMIT 10
    """)
    
    predict_samples = cursor.fetchall()
    print(f"找到 {len(predict_samples)} 个有预测价格的场馆样本")
    
    predict_peak_count = 0
    predict_offpeak_count = 0
    
    for name, predict_data in predict_samples:
        print(f"\n🏟️ 场馆: {name}")
        if predict_data:
            try:
                predict = json.loads(predict_data)
                print(f"  预测结果: {predict}")
                
                if predict.get('peak_price'):
                    predict_peak_count += 1
                if predict.get('off_peak_price'):
                    predict_offpeak_count += 1
            except:
                print(f"  预测数据解析失败")
    
    print(f"\n📈 预测价格统计:")
    print(f"  黄金时段价格: {predict_peak_count} 个")
    print(f"  非黄金时段价格: {predict_offpeak_count} 个")
    
    # 3. 检查所有场馆的价格分布
    print("\n📊 所有场馆价格分布:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL THEN 1 ELSE 0 END) as has_real_prices,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL THEN 1 ELSE 0 END) as has_predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    stats = cursor.fetchone()
    print(f"  总场馆数: {stats[0]}")
    print(f"  有真实价格: {stats[1]}")
    print(f"  有预测价格: {stats[2]}")
    
    conn.close()

if __name__ == "__main__":
    main() 