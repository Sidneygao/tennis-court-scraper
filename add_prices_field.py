#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加prices字段到court_details表
"""
import sqlite3
from datetime import datetime

def main():
    print("🔄 开始添加prices字段到court_details表...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'prices' in columns:
            print("✅ prices字段已存在，无需添加")
        else:
            # 添加prices字段
            print("📝 添加prices字段...")
            cursor.execute("ALTER TABLE court_details ADD COLUMN prices TEXT")
            print("✅ prices字段添加成功")
        
        # 验证字段添加
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 court_details表字段: {columns}")
        
        conn.commit()
        print("✅ 数据库更新完成")
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 