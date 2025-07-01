#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析嘉里中心被弃用的具体原因
"""
import sqlite3
import json
from math import radians, cos, sin, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

def main():
    print("\n=== 嘉里中心被弃用原因深度分析 ===\n")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查找嘉里中心相关场馆
    cursor.execute("""
        SELECT tc.id, tc.name, tc.latitude, tc.longitude, tc.area, 
               cd.merged_prices, cd.bing_prices, cd.predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.name LIKE '%嘉里%' OR tc.name LIKE '%Kerry%'
    """)
    results = cursor.fetchall()
    
    for cid, name, lat, lng, area, merged_prices, bing_prices, predict_prices in results:
        print(f"🏟️ {name} (ID: {cid})")
        print(f"  区域: {area}")
        print(f"  坐标: ({lat}, {lng})")
        
        # 分析merged_prices
        if merged_prices:
            try:
                prices = json.loads(merged_prices)
                print(f"  merged_prices: {len(prices)}条")
                for i, item in enumerate(prices[:3]):  # 只显示前3条
                    print(f"    {i+1}. 价格: {item.get('price', 'N/A')}, 置信度: {item.get('confidence', 'N/A')}, 来源: {item.get('source', 'N/A')}")
            except:
                print(f"  merged_prices解析失败: {merged_prices}")
        else:
            print("  merged_prices: 空")
            
        # 分析bing_prices
        if bing_prices:
            try:
                prices = json.loads(bing_prices)
                print(f"  bing_prices: {len(prices)}条")
                for i, item in enumerate(prices[:3]):  # 只显示前3条
                    print(f"    {i+1}. 价格: {item.get('price', 'N/A')}, 置信度: {item.get('confidence', 'N/A')}")
            except:
                print(f"  bing_prices解析失败: {bing_prices}")
        else:
            print("  bing_prices: 空")
            
        # 分析predict_prices
        if predict_prices:
            try:
                prices = json.loads(predict_prices)
                print(f"  predict_prices: {len(prices)}条")
                for i, item in enumerate(prices[:3]):  # 只显示前3条
                    print(f"    {i+1}. 价格: {item.get('price', 'N/A')}, 置信度: {item.get('confidence', 'N/A')}")
            except:
                print(f"  predict_prices解析失败: {predict_prices}")
        else:
            print("  predict_prices: 空")
            
        print()
    
    # 检查国贸区域中心点
    print("=== 国贸区域中心点分析 ===")
    cursor.execute("""
        SELECT AVG(latitude) as avg_lat, AVG(longitude) as avg_lng
        FROM tennis_courts 
        WHERE area = 'guomao'
    """)
    center = cursor.fetchone()
    if center[0] and center[1]:
        print(f"国贸区域平均中心: ({center[0]:.6f}, {center[1]:.6f})")
        
        # 计算嘉里中心到国贸中心的距离
        cursor.execute("""
            SELECT id, name, latitude, longitude
            FROM tennis_courts 
            WHERE name LIKE '%嘉里%' AND area = 'guomao'
        """)
        jiari_courts = cursor.fetchall()
        for cid, name, lat, lng in jiari_courts:
            if lat and lng:
                distance = haversine(lng, lat, center[1], center[0])
                print(f"  {name} 到国贸中心距离: {distance:.0f}米")
    
    conn.close()

if __name__ == "__main__":
    main() 