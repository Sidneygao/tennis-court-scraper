#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查三元桥/酒仙桥区域问题
"""
import sqlite3

def main():
    print("🔍 检查三元桥/酒仙桥区域问题...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查所有区域
    cursor.execute("SELECT DISTINCT area FROM tennis_courts ORDER BY area")
    areas = cursor.fetchall()
    
    print("\n📊 数据库中的区域:")
    for area in areas:
        print(f"  {area[0]}")
    
    # 检查是否有酒仙桥相关区域
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area LIKE '%jiuxianqiao%'")
    jiuxianqiao_count = cursor.fetchone()[0]
    print(f"\n🍷 酒仙桥区域场馆数: {jiuxianqiao_count}")
    
    # 检查是否有三元桥相关区域
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area LIKE '%sanyuanqiao%'")
    sanyuanqiao_count = cursor.fetchone()[0]
    print(f"🌉 三元桥区域场馆数: {sanyuanqiao_count}")
    
    # 检查配置中的区域
    print(f"\n⚙️ 配置中的区域:")
    config_areas = [
        "guomao", "sanlitun", "wangjing", "aoyuncun", "chaoyangpark", 
        "dawanglu", "shuangjing", "gaobeidian", "dongba", "changying", 
        "sanyuanqiao", "fengtai_east", "fengtai_west", "yizhuang"
    ]
    
    for area in config_areas:
        cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area = ?", (area,))
        count = cursor.fetchone()[0]
        print(f"  {area}: {count} 个场馆")
    
    # 查找三元桥/太阳宫相关场馆
    print(f"\n🔍 查找三元桥/太阳宫相关场馆:")
    cursor.execute("""
        SELECT id, name, address, area 
        FROM tennis_courts 
        WHERE name LIKE '%三元桥%' OR address LIKE '%三元桥%' 
           OR name LIKE '%太阳宫%' OR address LIKE '%太阳宫%'
        LIMIT 10
    """)
    results = cursor.fetchall()
    
    if results:
        for r in results:
            print(f"  {r[0]}: {r[1]} - {r[2]} (当前区域: {r[3]})")
    else:
        print("  未找到三元桥/太阳宫相关场馆")
    
    # 查找可能属于三元桥区域的场馆（按地理位置）
    print(f"\n🔍 查找可能属于三元桥区域的场馆（按经纬度）:")
    cursor.execute("""
        SELECT id, name, address, area, latitude, longitude
        FROM tennis_courts 
        WHERE latitude BETWEEN 39.95 AND 39.98 
          AND longitude BETWEEN 116.44 AND 116.47
        LIMIT 10
    """)
    results = cursor.fetchall()
    
    if results:
        for r in results:
            print(f"  {r[0]}: {r[1]} - {r[2]} (区域: {r[3]}, 坐标: {r[4]}, {r[5]})")
    else:
        print("  未找到三元桥区域附近的场馆")
    
    conn.close()

if __name__ == "__main__":
    main() 