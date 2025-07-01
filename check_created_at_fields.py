#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查created_at字段为None的记录
"""
import sqlite3

def main():
    print("🔍 检查created_at字段为None的记录...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查created_at为None的记录
    cursor.execute("""
        SELECT id, name, created_at
        FROM tennis_courts
        WHERE created_at IS NULL
    """)
    
    null_records = cursor.fetchall()
    print(f"\n📊 找到 {len(null_records)} 个created_at为None的记录:")
    
    for record in null_records:
        print(f"  ID: {record[0]}, 名称: {record[1]}, created_at: {record[2]}")
    
    # 检查丰台区和亦庄的场馆
    cursor.execute("""
        SELECT id, name, address, created_at
        FROM tennis_courts
        WHERE address LIKE '%丰台%' OR address LIKE '%亦庄%'
        ORDER BY id
    """)
    
    fengtai_yizhuang = cursor.fetchall()
    print(f"\n📊 丰台区和亦庄场馆 ({len(fengtai_yizhuang)} 个):")
    
    for record in fengtai_yizhuang:
        status = "❌ NULL" if record[3] is None else "✅ 正常"
        print(f"  ID: {record[0]}, 名称: {record[1]}, 地址: {record[2]}, created_at: {status}")
    
    conn.close()

if __name__ == "__main__":
    main() 