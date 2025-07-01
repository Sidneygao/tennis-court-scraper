#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析182个无价格数据场馆的具体情况
"""
import json
import sqlite3
from datetime import datetime

def main():
    print("🔍 分析无价格数据场馆的具体情况...")
    print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取所有场馆信息
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.area, tc.latitude, tc.longitude,
               cd.prices, cd.bing_prices, cd.predict_prices, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        ORDER BY tc.id
    """)
    
    results = cursor.fetchall()
    
    # 分析无价格数据的场馆
    no_price_courts = []
    has_price_courts = []
    
    for court_id, name, court_type, area, lat, lon, prices, bing_prices, predict_prices, merged_prices in results:
        has_any_price = False
        
        # 检查各种价格数据
        if prices and prices != '[]' and prices != 'null':
            has_any_price = True
        if bing_prices and bing_prices != '[]' and bing_prices != 'null':
            has_any_price = True
        if predict_prices and predict_prices != '[]' and predict_prices != 'null':
            has_any_price = True
        if merged_prices and merged_prices != '[]' and merged_prices != 'null':
            has_any_price = True
        
        court_info = {
            'court_id': court_id,
            'name': name,
            'court_type': court_type,
            'area': area,
            'latitude': lat,
            'longitude': lon,
            'has_coordinates': lat is not None and lon is not None,
            'prices': prices,
            'bing_prices': bing_prices,
            'predict_prices': predict_prices,
            'merged_prices': merged_prices
        }
        
        if has_any_price:
            has_price_courts.append(court_info)
        else:
            no_price_courts.append(court_info)
    
    print(f"\n📊 统计结果:")
    print(f"   有价格数据场馆: {len(has_price_courts)} 个")
    print(f"   无价格数据场馆: {len(no_price_courts)} 个")
    print(f"   总计: {len(results)} 个")
    
    # 分析无价格场馆的详细情况
    print(f"\n🔍 无价格数据场馆详细分析:")
    
    # 1. 坐标情况
    no_coordinates = [c for c in no_price_courts if not c['has_coordinates']]
    has_coordinates = [c for c in no_price_courts if c['has_coordinates']]
    
    print(f"   无坐标场馆: {len(no_coordinates)} 个")
    print(f"   有坐标场馆: {len(has_coordinates)} 个")
    
    # 2. 场馆类型分布
    type_counts = {}
    for court in no_price_courts:
        court_type = court['court_type'] or '未知'
        type_counts[court_type] = type_counts.get(court_type, 0) + 1
    
    print(f"\n   场馆类型分布:")
    for court_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     {court_type}: {count} 个")
    
    # 3. 区域分布
    area_counts = {}
    for court in no_price_courts:
        area = court['area'] or '未知'
        area_counts[area] = area_counts.get(area, 0) + 1
    
    print(f"\n   区域分布:")
    for area, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     {area}: {count} 个")
    
    # 4. 显示一些具体例子
    print(f"\n📋 无价格数据场馆示例 (前10个):")
    for i, court in enumerate(no_price_courts[:10]):
        print(f"   {i+1}. {court['name']} (ID: {court['court_id']})")
        print(f"      类型: {court['court_type']}")
        print(f"      区域: {court['area']}")
        print(f"      坐标: {court['latitude']}, {court['longitude']}")
        print(f"      有坐标: {court['has_coordinates']}")
        print()
    
    # 5. 检查是否有坐标但无价格的情况
    if has_coordinates:
        print(f"\n⚠️ 有坐标但无价格数据的场馆 (前5个):")
        for i, court in enumerate(has_coordinates[:5]):
            print(f"   {i+1}. {court['name']} (ID: {court['court_id']})")
            print(f"      坐标: {court['latitude']}, {court['longitude']}")
            print(f"      类型: {court['court_type']}")
            print()
    
    conn.close()
    
    print(f"\n✅ 分析完成！")
    print(f"   主要问题可能是:")
    print(f"   1. 部分场馆缺少坐标数据")
    print(f"   2. 部分场馆类型特殊，找不到同类型参考")
    print(f"   3. 需要重新运行2KM步进法预测")

if __name__ == "__main__":
    main() 