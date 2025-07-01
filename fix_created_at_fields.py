#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中created_at字段为None的问题
"""
import sqlite3
from datetime import datetime

def fix_created_at_fields():
    print("🔧 修复数据库中created_at字段为None的问题...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查有多少条记录的created_at为None
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts WHERE created_at IS NULL
    """)
    null_count = cursor.fetchone()[0]
    print(f"📊 发现 {null_count} 条记录的created_at字段为None")
    
    if null_count > 0:
        # 更新所有created_at为None的记录
        current_time = datetime.now().isoformat()
        cursor.execute("""
            UPDATE tennis_courts 
            SET created_at = ? 
            WHERE created_at IS NULL
        """, (current_time,))
        
        updated_count = cursor.rowcount
        conn.commit()
        print(f"✅ 已修复 {updated_count} 条记录的created_at字段")
    else:
        print("✅ 所有记录的created_at字段都已正常")
    
    # 验证修复结果
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts WHERE created_at IS NULL
    """)
    remaining_null = cursor.fetchone()[0]
    print(f"📊 修复后，仍有 {remaining_null} 条记录的created_at字段为None")
    
    conn.close()

if __name__ == "__main__":
    fix_created_at_fields() 