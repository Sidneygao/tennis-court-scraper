#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查浩生体育网球俱乐部(望京店)的详细信息
"""
import sqlite3
import json
import os

def main():
    print("🔍 检查茂华UHN国际村-网球场的详细信息...")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查找这个场馆
    court_name = "茂华UHN国际村-网球场"
    
    cursor.execute("""
        SELECT id, name, address, court_type, area, latitude, longitude
        FROM tennis_courts
        WHERE name LIKE ?
    """, (f"%{court_name}%",))
    
    result = cursor.fetchone()
    
    if result:
        court_id, name, address, court_type, area, lat, lon = result
        print(f"\n📊 场馆基本信息:")
        print(f"   ID: {court_id}")
        print(f"   名称: {name}")
        print(f"   地址: {address}")
        print(f"   当前类型: {court_type}")
        print(f"   区域: {area}")
        print(f"   坐标: {lat}, {lon}")
        
        # 检查详情数据
        cursor.execute("""
            SELECT merged_prices, predict_prices
            FROM court_details
            WHERE court_id = ?
        """, (court_id,))
        
        detail_result = cursor.fetchone()
        if detail_result:
            merged_prices, predict_prices = detail_result
            print(f"\n💰 merged_prices: {merged_prices}")
            print(f"💡 predict_prices: {predict_prices}")
        else:
            print('  ❌ 未找到court_details记录')
    else:
        print('未找到该场馆')
    conn.close()

if __name__ == "__main__":
    main()

def main_new():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, latitude, longitude FROM tennis_courts WHERE name LIKE '%茂华UHN国际村-网球场%'")
    rows = cursor.fetchall()
    if not rows:
        print('未找到该场馆')
    for court_id, name, lat, lng in rows:
        print(f'场馆: {name}\n  id: {court_id}\n  纬度: {lat}\n  经度: {lng}')
        # 查map_image
        cursor.execute("SELECT map_image FROM court_details WHERE court_id=?", (court_id,))
        map_row = cursor.fetchone()
        if map_row:
            map_image = map_row[0]
            print(f'  map_image: {map_image}')
            # 检查文件存在性
            if map_image:
                file_path = map_image.lstrip('/')
                if os.path.exists(file_path):
                    print(f'  ✅ 文件存在: {file_path}')
                else:
                    print(f'  ❌ 文件不存在: {file_path}')
        else:
            print('  ❌ 未找到court_details记录')
    conn.close()

if __name__ == '__main__':
    main_new() 