#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查丰台区场馆的实际经度数据
"""
import sqlite3

def main():
    print("🔍 检查丰台区场馆经度数据...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查询所有丰台区场馆的详细信息
    cursor.execute("""
        SELECT id, name, address, latitude, longitude 
        FROM tennis_courts 
        WHERE name LIKE '%丰台%' OR address LIKE '%丰台%'
        ORDER BY name
    """)
    
    fengtai_courts = cursor.fetchall()
    print(f"丰台区场馆总数: {len(fengtai_courts)}")
    
    print("\n📊 丰台区场馆详细信息:")
    for court in fengtai_courts:
        court_id, name, address, lat, lng = court
        print(f"\n场馆ID: {court_id}")
        print(f"名称: {name}")
        print(f"地址: {address}")
        print(f"纬度: {lat}")
        print(f"经度: {lng}")
        
        # 判断应该属于哪个区域
        if lng and lng > 116.321:
            area = "丰台区东部"
        else:
            area = "丰台区西部"
        print(f"应该属于: {area}")
        
        # 检查数据是否合理
        if not lng or lng == 0:
            print("  ⚠️  经度数据缺失或为0")
        elif lng < 100 or lng > 150:
            print("  ⚠️  经度数据可能错误（超出合理范围）")
        else:
            print("  ✅ 经度数据正常")
    
    # 查询亦庄场馆
    print(f"\n📊 亦庄场馆详细信息:")
    cursor.execute("""
        SELECT id, name, address, latitude, longitude 
        FROM tennis_courts 
        WHERE name LIKE '%亦庄%' OR address LIKE '%亦庄%'
        ORDER BY name
    """)
    
    yizhuang_courts = cursor.fetchall()
    print(f"亦庄场馆总数: {len(yizhuang_courts)}")
    
    for court in yizhuang_courts:
        court_id, name, address, lat, lng = court
        print(f"\n场馆ID: {court_id}")
        print(f"名称: {name}")
        print(f"地址: {address}")
        print(f"纬度: {lat}")
        print(f"经度: {lng}")
        
        if not lng or lng == 0:
            print("  ⚠️  经度数据缺失或为0")
        elif lng < 100 or lng > 150:
            print("  ⚠️  经度数据可能错误（超出合理范围）")
        else:
            print("  ✅ 经度数据正常")
    
    conn.close()

if __name__ == "__main__":
    main() 