#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查哪些场馆应该被分配到三元桥区域
"""
import sqlite3

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 三元桥区域中心坐标
    sanyuanqiao_center = (116.456, 39.967)
    radius_km = 5.0  # 5公里半径
    
    # 查找在三元桥区域范围内的场馆
    cursor.execute("""
        SELECT name, address, longitude, latitude, area 
        FROM tennis_courts 
        WHERE longitude IS NOT NULL 
        AND latitude IS NOT NULL
    """)
    
    courts = cursor.fetchall()
    print(f"检查 {len(courts)} 个场馆的地理位置...")
    
    sanyuanqiao_candidates = []
    
    for name, address, lng, lat, area in courts:
        if lng and lat:
            # 计算距离（简化计算）
            distance = ((lng - sanyuanqiao_center[0])**2 + (lat - sanyuanqiao_center[1])**2)**0.5 * 111  # 约111km/度
            
            if distance <= radius_km:
                sanyuanqiao_candidates.append({
                    'name': name,
                    'address': address,
                    'longitude': lng,
                    'latitude': lat,
                    'current_area': area,
                    'distance': distance
                })
    
    print(f"\n在三元桥区域5公里范围内的场馆（{len(sanyuanqiao_candidates)}个）:")
    for court in sanyuanqiao_candidates:
        print(f"  {court['name']}")
        print(f"    地址: {court['address']}")
        print(f"    坐标: {court['longitude']}, {court['latitude']}")
        print(f"    当前区域: {court['current_area']}")
        print(f"    距离三元桥: {court['distance']:.2f}km")
        print()
    
    # 检查名称或地址中包含"三元桥"的场馆
    cursor.execute("""
        SELECT name, address, area 
        FROM tennis_courts 
        WHERE name LIKE '%三元桥%' 
        OR address LIKE '%三元桥%'
        OR name LIKE '%太阳宫%'
        OR address LIKE '%太阳宫%'
    """)
    
    name_matches = cursor.fetchall()
    print(f"\n名称或地址包含'三元桥'或'太阳宫'的场馆（{len(name_matches)}个）:")
    for name, address, area in name_matches:
        print(f"  {name}")
        print(f"    地址: {address}")
        print(f"    当前区域: {area}")
        print()
    
    conn.close()

if __name__ == "__main__":
    main() 