#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中经纬度数据被搞反的问题
"""
import sqlite3

def main():
    print("🔧 修复经纬度数据...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 先检查当前数据
    print("📊 修复前数据检查:")
    cursor.execute("""
        SELECT id, name, latitude, longitude 
        FROM tennis_courts 
        WHERE name LIKE '%丰台%' OR name LIKE '%亦庄%'
        LIMIT 5
    """)
    
    sample_courts = cursor.fetchall()
    for court in sample_courts:
        court_id, name, lat, lng = court
        print(f"场馆: {name}")
        print(f"  修复前 - 纬度: {lat}, 经度: {lng}")
    
    # 修复经纬度数据：交换latitude和longitude的值
    print("\n🔧 开始修复经纬度数据...")
    
    # 更新所有场馆的经纬度数据
    cursor.execute("""
        UPDATE tennis_courts 
        SET latitude = longitude, longitude = latitude
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    updated_count = cursor.rowcount
    print(f"已修复 {updated_count} 个场馆的经纬度数据")
    
    # 验证修复结果
    print("\n📊 修复后数据验证:")
    cursor.execute("""
        SELECT id, name, latitude, longitude 
        FROM tennis_courts 
        WHERE name LIKE '%丰台%' OR name LIKE '%亦庄%'
        ORDER BY name
    """)
    
    fixed_courts = cursor.fetchall()
    for court in fixed_courts:
        court_id, name, lat, lng = court
        print(f"\n场馆: {name}")
        print(f"  修复后 - 纬度: {lat}, 经度: {lng}")
        
        # 判断丰台区场馆归属
        if '丰台' in name:
            if lng and lng > 116.321:
                area = "丰台区东部"
            else:
                area = "丰台区西部"
            print(f"  应该属于: {area}")
        
        # 检查数据是否合理
        if not lng or lng == 0:
            print("  ⚠️  经度数据缺失或为0")
        elif lng < 116 or lng > 117:
            print("  ⚠️  经度数据可能错误（超出北京范围）")
        else:
            print("  ✅ 经度数据正常")
    
    # 提交更改
    conn.commit()
    print(f"\n✅ 经纬度数据修复完成，已更新 {updated_count} 个场馆")
    
    conn.close()

if __name__ == "__main__":
    main() 