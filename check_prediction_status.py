#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查预测价格的计算状态
"""
import sqlite3
import json

def main():
    print("🔍 检查预测价格计算状态...")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查预测价格状态
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE predict_prices IS NOT NULL AND predict_prices != ''")
    with_predict = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE predict_prices IS NULL OR predict_prices = ''")
    without_predict = cursor.fetchone()[0]
    
    # 检查总场馆数
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_courts = cursor.fetchone()[0]
    
    # 检查有坐标的场馆数
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
    with_coordinates = cursor.fetchone()[0]
    
    # 检查无坐标的场馆数
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE latitude IS NULL OR longitude IS NULL")
    without_coordinates = cursor.fetchone()[0]
    
    print(f"\n📊 预测价格状态统计:")
    print(f"   有预测价格场馆: {with_predict} 个")
    print(f"   无预测价格场馆: {without_predict} 个")
    print(f"   总计场馆: {total_courts} 个")
    
    print(f"\n📍 坐标状态统计:")
    print(f"   有坐标场馆: {with_coordinates} 个")
    print(f"   无坐标场馆: {without_coordinates} 个")
    
    # 分析无预测价格的原因
    if without_predict > 0:
        print(f"\n🔍 分析无预测价格的原因:")
        
        # 检查无坐标但无预测价格的场馆
        cursor.execute("""
            SELECT tc.id, tc.name, tc.latitude, tc.longitude
            FROM tennis_courts tc
            LEFT JOIN court_details cd ON tc.id = cd.court_id
            WHERE (cd.predict_prices IS NULL OR cd.predict_prices = '')
            AND (tc.latitude IS NULL OR tc.longitude IS NULL)
        """)
        no_coord_no_predict = cursor.fetchall()
        
        print(f"   无坐标且无预测价格: {len(no_coord_no_predict)} 个")
        if no_coord_no_predict:
            print(f"   示例场馆:")
            for i, (court_id, name, lat, lon) in enumerate(no_coord_no_predict[:5]):
                print(f"     {i+1}. {name} (ID: {court_id}) - 坐标: {lat}, {lon}")
        
        # 检查有坐标但无预测价格的场馆
        cursor.execute("""
            SELECT tc.id, tc.name, tc.latitude, tc.longitude
            FROM tennis_courts tc
            LEFT JOIN court_details cd ON tc.id = cd.court_id
            WHERE (cd.predict_prices IS NULL OR cd.predict_prices = '')
            AND tc.latitude IS NOT NULL AND tc.longitude IS NOT NULL
        """)
        has_coord_no_predict = cursor.fetchall()
        
        print(f"   有坐标但无预测价格: {len(has_coord_no_predict)} 个")
        if has_coord_no_predict:
            print(f"   示例场馆:")
            for i, (court_id, name, lat, lon) in enumerate(has_coord_no_predict[:5]):
                print(f"     {i+1}. {name} (ID: {court_id}) - 坐标: {lat}, {lon}")
    
    conn.close()
    
    print(f"\n✅ 检查完成！")
    if without_predict > 0:
        print(f"   需要解决的问题:")
        print(f"   1. 无坐标场馆: 需要补充坐标数据")
        print(f"   2. 有坐标但无预测: 需要重新运行2KM步进法")
    else:
        print(f"   🎉 所有场馆都有预测价格！")

if __name__ == "__main__":
    main() 