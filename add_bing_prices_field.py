#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加bing_prices字段到court_details表
"""

import sqlite3
import os

def add_bing_prices_field():
    """添加bing_prices字段到court_details表"""
    db_path = 'data/courts.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'bing_prices' not in columns:
            # 添加bing_prices字段
            cursor.execute("ALTER TABLE court_details ADD COLUMN bing_prices TEXT")
            conn.commit()
            print("✅ 成功添加bing_prices字段到court_details表")
        else:
            print("ℹ️ bing_prices字段已存在")
        
        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前court_details表字段: {columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    add_bing_prices_field() 