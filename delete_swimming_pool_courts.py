#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除包含"游泳池"关键词的非网球场馆
"""
import sqlite3
import json

def main():
    print("🔍 查找并删除包含'游泳池'关键词的非网球场馆...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 查找包含"游泳池"的场馆
    print("\n📋 查找包含'游泳池'的场馆:")
    cursor.execute("""
        SELECT id, name, address, area_name
        FROM tennis_courts 
        WHERE name LIKE '%游泳池%'
        ORDER BY id
    """)
    
    swimming_pool_courts = cursor.fetchall()
    print(f"找到 {len(swimming_pool_courts)} 个包含'游泳池'的场馆:")
    
    for court_id, name, address, area in swimming_pool_courts:
        print(f"  ID: {court_id}, 名称: {name}, 区域: {area}")
    
    if not swimming_pool_courts:
        print("✅ 没有找到包含'游泳池'的场馆，无需删除")
        conn.close()
        return
    
    # 2. 确认删除
    print(f"\n⚠️  即将删除 {len(swimming_pool_courts)} 个非网球场馆:")
    for court_id, name, address, area in swimming_pool_courts:
        print(f"  - {name} (ID: {court_id})")
    
    # 3. 删除场馆详情数据
    court_ids = [court[0] for court in swimming_pool_courts]
    placeholders = ','.join(['?' for _ in court_ids])
    
    cursor.execute(f"""
        DELETE FROM court_details 
        WHERE court_id IN ({placeholders})
    """, court_ids)
    
    deleted_details = cursor.rowcount
    print(f"✅ 删除了 {deleted_details} 条场馆详情记录")
    
    # 4. 删除主场馆数据
    cursor.execute(f"""
        DELETE FROM tennis_courts 
        WHERE id IN ({placeholders})
    """, court_ids)
    
    deleted_courts = cursor.rowcount
    print(f"✅ 删除了 {deleted_courts} 个场馆记录")
    
    # 5. 提交事务
    conn.commit()
    
    # 6. 验证删除结果
    print("\n🔍 验证删除结果:")
    cursor.execute("""
        SELECT COUNT(*) as total_courts
        FROM tennis_courts
    """)
    total_courts = cursor.fetchone()[0]
    print(f"  剩余场馆总数: {total_courts}")
    
    cursor.execute("""
        SELECT COUNT(*) as total_details
        FROM court_details
    """)
    total_details = cursor.fetchone()[0]
    print(f"  剩余详情记录数: {total_details}")
    
    # 7. 检查是否还有遗漏的游泳池场馆
    cursor.execute("""
        SELECT id, name
        FROM tennis_courts 
        WHERE name LIKE '%游泳池%'
    """)
    
    remaining = cursor.fetchall()
    if remaining:
        print(f"\n⚠️  仍有 {len(remaining)} 个包含'游泳池'的场馆未删除:")
        for court_id, name in remaining:
            print(f"  - {name} (ID: {court_id})")
    else:
        print("\n✅ 所有包含'游泳池'的场馆已成功删除")
    
    conn.close()
    print("\n🎉 删除操作完成！")

if __name__ == "__main__":
    main() 