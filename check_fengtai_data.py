#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查丰台区场馆数据分布
"""
import sqlite3
import json

def main():
    print("🔍 检查丰台区场馆数据分布...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查丰台区场馆总数
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE address LIKE '%丰台%'")
    total_count = cursor.fetchone()[0]
    print(f"丰台区场馆总数: {total_count}")
    
    # 获取丰台区场馆详细信息
    cursor.execute("""
        SELECT id, name, address, latitude, longitude 
        FROM tennis_courts 
        WHERE address LIKE '%丰台%'
        ORDER BY name
    """)
    
    fengtai_courts = cursor.fetchall()
    print(f"\n📊 丰台区场馆列表:")
    
    for court in fengtai_courts:
        court_id, name, address, lat, lng = court
        print(f"  {court_id}: {name}")
        print(f"    地址: {address}")
        print(f"    坐标: ({lat}, {lng})")
        print()
    
    # 首经贸大学坐标（作为分界线）
    # 首经贸大学位于丰台区花乡街道，坐标约为 116.321, 39.886
    shoujingmao_lng = 116.321
    
    # 按经度分东西
    east_count = 0
    west_count = 0
    
    print("📍 按首经贸大学分界线分析:")
    print(f"首经贸大学经度: {shoujingmao_lng}")
    print()
    
    for court in fengtai_courts:
        court_id, name, address, lat, lng = court
        if lng and lng > shoujingmao_lng:
            print(f"  东部: {name} (经度: {lng})")
            east_count += 1
        elif lng and lng <= shoujingmao_lng:
            print(f"  西部: {name} (经度: {lng})")
            west_count += 1
        else:
            print(f"  未知: {name} (经度: {lng})")
    
    print(f"\n📈 分布统计:")
    print(f"  丰台区东部: {east_count} 个场馆")
    print(f"  丰台区西部: {west_count} 个场馆")
    
    # 检查亦庄数据
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE address LIKE '%亦庄%'")
    yizhuang_count = cursor.fetchone()[0]
    print(f"  亦庄: {yizhuang_count} 个场馆")
    
    if yizhuang_count > 0:
        cursor.execute("""
            SELECT id, name, address, latitude, longitude 
            FROM tennis_courts 
            WHERE address LIKE '%亦庄%'
            ORDER BY name
        """)
        
        yizhuang_courts = cursor.fetchall()
        print(f"\n🏢 亦庄场馆列表:")
        for court in yizhuang_courts:
            court_id, name, address, lat, lng = court
            print(f"  {court_id}: {name}")
            print(f"    地址: {address}")
            print(f"    坐标: ({lat}, {lng})")
            print()
    
    conn.close()

if __name__ == "__main__":
    main() 