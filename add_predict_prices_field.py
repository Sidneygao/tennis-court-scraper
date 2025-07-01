#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本：为court_details表添加predict_prices字段
"""

import sqlite3
import os
from datetime import datetime

def add_predict_prices_field():
    """添加predict_prices字段到court_details表"""
    try:
        # 连接数据库
        db_path = "data/courts.db"
        if not os.path.exists(db_path):
            print(f"数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'predict_prices' in columns:
            print("predict_prices字段已存在，跳过添加")
            return True
        
        # 添加predict_prices字段
        print("正在添加predict_prices字段...")
        cursor.execute("""
            ALTER TABLE court_details 
            ADD COLUMN predict_prices TEXT
        """)
        
        conn.commit()
        print("predict_prices字段添加成功")
        
        # 验证字段添加
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'predict_prices' in columns:
            print("字段验证成功")
            return True
        else:
            print("字段验证失败")
            return False
            
    except Exception as e:
        print(f"添加字段失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print(f"开始数据库迁移: {datetime.now()}")
    success = add_predict_prices_field()
    if success:
        print("数据库迁移完成")
    else:
        print("数据库迁移失败") 