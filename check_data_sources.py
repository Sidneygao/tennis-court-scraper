#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据源：GeoJSON和数据库的场馆数量差异
"""
import json
import sqlite3

def main():
    # 检查GeoJSON文件
    print("📖 检查GeoJSON文件...")
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    geojson_courts = []
    for feature in geojson['features']:
        prop = feature['properties']
        geojson_courts.append({
            'court_id': prop['court_id'],
            'name': prop['name']
        })
    
    print(f"GeoJSON文件中的场馆数量: {len(geojson_courts)}")
    print(f"GeoJSON中的court_id范围: {min(c['court_id'] for c in geojson_courts)} - {max(c['court_id'] for c in geojson_courts)}")
    
    # 检查数据库
    print("\n🗄️ 检查数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 总场馆数
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_courts = cursor.fetchone()[0]
    print(f"数据库总场馆数: {total_courts}")
    
    # 有真实价格的场馆数
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE merged_prices IS NOT NULL")
    with_real_price = cursor.fetchone()[0]
    print(f"有真实价格的场馆数: {with_real_price}")
    
    # 无真实价格的场馆数
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE merged_prices IS NULL")
    without_real_price = cursor.fetchone()[0]
    print(f"无真实价格的场馆数: {without_real_price}")
    
    # 检查court_details表的总数
    cursor.execute("SELECT COUNT(*) FROM court_details")
    total_details = cursor.fetchone()[0]
    print(f"court_details表总数: {total_details}")
    
    # 检查GeoJSON中的场馆是否在数据库中
    geojson_ids = set(c['court_id'] for c in geojson_courts)
    cursor.execute("SELECT court_id FROM court_details WHERE merged_prices IS NULL")
    db_no_price_ids = set(row[0] for row in cursor.fetchall())
    
    intersection = geojson_ids & db_no_price_ids
    print(f"\n📊 数据交叉分析:")
    print(f"GeoJSON中的场馆ID数量: {len(geojson_ids)}")
    print(f"数据库中无真实价格的场馆ID数量: {len(db_no_price_ids)}")
    print(f"两者交集数量: {len(intersection)}")
    
    if len(intersection) > 0:
        print(f"✅ 有{len(intersection)}家场馆可以预测")
    else:
        print("❌ 没有可预测的场馆")
    
    conn.close()

if __name__ == '__main__':
    main() 