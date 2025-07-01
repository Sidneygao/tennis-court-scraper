#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析特定场馆的价格情况
"""
import json
import sqlite3
from collections import defaultdict

def main():
    print("🔍 详细分析特定场馆价格情况...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 分析柏林瀚网球馆望京店
    print("\n🏟️ 柏林瀚网球馆望京店 详细分析:")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.address, 
               cd.merged_prices, cd.predict_prices, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.name LIKE '%柏林瀚网球馆望京店%'
    """)
    
    berlin_court = cursor.fetchone()
    if berlin_court:
        court_id, name, court_type, address, merged_prices, predict_prices, bing_prices = berlin_court
        print(f"  场馆ID: {court_id}")
        print(f"  场馆名称: {name}")
        print(f"  场馆类型: {court_type}")
        print(f"  地址: {address}")
        
        # 分析真实价格
        if merged_prices:
            try:
                real_prices = json.loads(merged_prices)
                print(f"  真实价格数量: {len(real_prices)}")
                for i, price in enumerate(real_prices):
                    print(f"    真实价格{i+1}: {price}")
            except:
                print(f"  真实价格解析失败: {merged_prices}")
        else:
            print("  真实价格: 无")
        
        # 分析预测价格
        if predict_prices:
            try:
                predict = json.loads(predict_prices)
                print(f"  预测价格: {predict}")
            except:
                print(f"  预测价格解析失败: {predict_prices}")
        else:
            print("  预测价格: 无")
        
        # 分析BING价格
        if bing_prices:
            try:
                bing = json.loads(bing_prices)
                print(f"  BING价格数量: {len(bing)}")
                for i, price in enumerate(bing):
                    print(f"    BING价格{i+1}: {price}")
            except:
                print(f"  BING价格解析失败: {bing_prices}")
        else:
            print("  BING价格: 无")
    
    # 分析育乐网球(航星园店)
    print("\n🏟️ 育乐网球(航星园店) 详细分析:")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.address, 
               cd.merged_prices, cd.predict_prices, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.name LIKE '%育乐网球%航星园%'
    """)
    
    yule_court = cursor.fetchone()
    if yule_court:
        court_id, name, court_type, address, merged_prices, predict_prices, bing_prices = yule_court
        print(f"  场馆ID: {court_id}")
        print(f"  场馆名称: {name}")
        print(f"  场馆类型: {court_type}")
        print(f"  地址: {address}")
        
        # 分析真实价格
        if merged_prices:
            try:
                real_prices = json.loads(merged_prices)
                print(f"  真实价格数量: {len(real_prices)}")
                for i, price in enumerate(real_prices):
                    print(f"    真实价格{i+1}: {price}")
            except:
                print(f"  真实价格解析失败: {merged_prices}")
        else:
            print("  真实价格: 无")
        
        # 分析预测价格
        if predict_prices:
            try:
                predict = json.loads(predict_prices)
                print(f"  预测价格: {predict}")
            except:
                print(f"  预测价格解析失败: {predict_prices}")
        else:
            print("  预测价格: 无")
        
        # 分析BING价格
        if bing_prices:
            try:
                bing = json.loads(bing_prices)
                print(f"  BING价格数量: {len(bing)}")
                for i, price in enumerate(bing):
                    print(f"    BING价格{i+1}: {price}")
            except:
                print(f"  BING价格解析失败: {bing_prices}")
        else:
            print("  BING价格: 无")
    
    # 检查预测价格计算逻辑
    print("\n🔍 检查预测价格计算逻辑:")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, cd.predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.name IN ('柏林瀚网球馆望京店', '育乐网球(航星园店)')
    """)
    
    courts = cursor.fetchall()
    for court_id, name, court_type, predict_prices in courts:
        print(f"\n  {name} (ID: {court_id}, 类型: {court_type}):")
        if predict_prices:
            try:
                predict = json.loads(predict_prices)
                print(f"    预测结果: {predict}")
                
                # 分析预测价格是否合理
                if 'peak_price' in predict and 'off_peak_price' in predict:
                    peak = predict['peak_price']
                    off_peak = predict['off_peak_price']
                    
                    if court_type == '室内':
                        if peak < 150 or off_peak < 120:
                            print(f"    ⚠️  室内场馆预测价格偏低: 黄金时段¥{peak}, 非黄金时段¥{off_peak}")
                        else:
                            print(f"    ✅ 室内场馆预测价格合理: 黄金时段¥{peak}, 非黄金时段¥{off_peak}")
                    elif court_type == '室外':
                        if peak < 120 or off_peak < 100:
                            print(f"    ⚠️  室外场馆预测价格偏低: 黄金时段¥{peak}, 非黄金时段¥{off_peak}")
                        else:
                            print(f"    ✅ 室外场馆预测价格合理: 黄金时段¥{peak}, 非黄金时段¥{off_peak}")
            except:
                print(f"    预测价格解析失败: {predict_prices}")
        else:
            print("    无预测价格")
    
    conn.close()

if __name__ == "__main__":
    main() 