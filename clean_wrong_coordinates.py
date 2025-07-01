#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理错误的经纬度数据：删除经纬度明显错误的记录
"""
import sqlite3
from collections import defaultdict

def main():
    print("🧹 开始清理错误的经纬度数据...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 统计清理前的数据
    print("\n📊 清理前统计:")
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_before = cursor.fetchone()[0]
    print(f"  总场馆数: {total_before}")
    
    # 2. 找出错误的经纬度记录
    print("\n🔍 查找错误的经纬度记录:")
    
    # 北京地区的合理经纬度范围
    # 纬度: 39.4 ~ 41.1 (北京范围)
    # 经度: 115.7 ~ 117.4 (北京范围)
    
    # 查找错误的记录
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE (latitude < 39.4 OR latitude > 41.1 OR longitude < 115.7 OR longitude > 117.4)
        AND (latitude IS NOT NULL AND longitude IS NOT NULL)
        ORDER BY id
    """)
    
    wrong_records = cursor.fetchall()
    print(f"  找到 {len(wrong_records)} 个经纬度错误的记录:")
    
    wrong_ids = []
    for record in wrong_records:
        court_id, name, lat, lng = record
        wrong_ids.append(court_id)
        print(f"    ID {court_id}: {name}")
        print(f"      错误坐标: ({lat}, {lng})")
    
    # 3. 查找重复的场馆名称
    print("\n🔍 查找重复的场馆名称:")
    cursor.execute("""
        SELECT name, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM tennis_courts
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicates = cursor.fetchall()
    print(f"  找到 {len(duplicates)} 个重复的场馆名称:")
    
    duplicate_ids_to_delete = []
    for name, count, ids in duplicates:
        id_list = [int(x) for x in ids.split(',')]
        print(f"    {name}: {count} 个记录 (ID: {id_list})")
        
        # 检查这些记录中哪些经纬度是错误的
        cursor.execute("""
            SELECT id, latitude, longitude
            FROM tennis_courts
            WHERE id IN ({})
        """.format(','.join(map(str, id_list))))
        
        records = cursor.fetchall()
        valid_records = []
        invalid_records = []
        
        for record_id, lat, lng in records:
            if (39.4 <= lat <= 41.1 and 115.7 <= lng <= 117.4):
                valid_records.append(record_id)
            else:
                invalid_records.append(record_id)
        
        print(f"      有效记录: {valid_records}")
        print(f"      无效记录: {invalid_records}")
        
        # 如果有有效记录，删除无效记录
        if valid_records and invalid_records:
            duplicate_ids_to_delete.extend(invalid_records)
            print(f"      ✅ 将删除无效记录: {invalid_records}")
        elif not valid_records and invalid_records:
            # 如果都是无效的，保留第一个
            duplicate_ids_to_delete.extend(invalid_records[1:])
            print(f"      ⚠️  都是无效记录，保留第一个，删除: {invalid_records[1:]}")
    
    # 4. 合并需要删除的ID
    all_ids_to_delete = list(set(wrong_ids + duplicate_ids_to_delete))
    print(f"\n📋 总计需要删除 {len(all_ids_to_delete)} 个记录:")
    print(f"  经纬度错误: {len(wrong_ids)} 个")
    print(f"  重复记录: {len(duplicate_ids_to_delete)} 个")
    
    # 5. 删除错误记录
    if all_ids_to_delete:
        print(f"\n🗑️  开始删除错误记录...")
        
        # 先删除court_details中的相关记录
        cursor.execute("""
            DELETE FROM court_details 
            WHERE court_id IN ({})
        """.format(','.join(map(str, all_ids_to_delete))))
        
        details_deleted = cursor.rowcount
        print(f"  删除 court_details 记录: {details_deleted} 个")
        
        # 再删除tennis_courts中的记录
        cursor.execute("""
            DELETE FROM tennis_courts 
            WHERE id IN ({})
        """.format(','.join(map(str, all_ids_to_delete))))
        
        courts_deleted = cursor.rowcount
        print(f"  删除 tennis_courts 记录: {courts_deleted} 个")
        
        # 提交更改
        conn.commit()
        print(f"✅ 删除完成")
    else:
        print(f"\n✅ 没有需要删除的记录")
    
    # 6. 统计清理后的数据
    print("\n📊 清理后统计:")
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_after = cursor.fetchone()[0]
    print(f"  总场馆数: {total_after}")
    print(f"  删除了 {total_before - total_after} 个记录")
    
    # 7. 检查丰台区场馆
    print("\n🏢 检查丰台区场馆:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE name LIKE '%丰台%' OR address LIKE '%丰台%'
        ORDER BY name
    """)
    
    fengtai_courts = cursor.fetchall()
    print(f"  丰台区场馆数: {len(fengtai_courts)}")
    
    fengtai_east = 0
    fengtai_west = 0
    
    for court_id, name, lat, lng in fengtai_courts:
        if lng > 116.321:
            area = "丰台区东部"
            fengtai_east += 1
        else:
            area = "丰台区西部"
            fengtai_west += 1
        
        print(f"    ID {court_id}: {name}")
        print(f"      坐标: ({lat}, {lng}) -> {area}")
    
    print(f"\n📈 丰台区分布:")
    print(f"  丰台区东部: {fengtai_east} 个场馆")
    print(f"  丰台区西部: {fengtai_west} 个场馆")
    
    # 8. 检查亦庄场馆
    print("\n🏢 检查亦庄场馆:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE name LIKE '%亦庄%' OR address LIKE '%亦庄%'
        ORDER BY name
    """)
    
    yizhuang_courts = cursor.fetchall()
    print(f"  亦庄场馆数: {len(yizhuang_courts)}")
    
    for court_id, name, lat, lng in yizhuang_courts:
        print(f"    ID {court_id}: {name}")
        print(f"      坐标: ({lat}, {lng})")
    
    conn.close()
    print(f"\n✅ 经纬度数据清理完成！")

if __name__ == "__main__":
    main() 