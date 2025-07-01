#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单数据库测试
"""
import sqlite3

def test_db():
    try:
        conn = sqlite3.connect('data/tennis_courts.db')
        cursor = conn.cursor()
        
        # 检查总数量
        cursor.execute('SELECT COUNT(*) FROM tennis_courts')
        total = cursor.fetchone()[0]
        print(f"总场馆数: {total}")
        
        # 检查三元桥区域
        cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area = 'sanyuanqiao'")
        sanyuanqiao_count = cursor.fetchone()[0]
        print(f"三元桥区域场馆数: {sanyuanqiao_count}")
        
        # 检查朝阳区9个区域
        chaoyang_areas = ['guomao', 'sanlitun', 'wangjing', 'aoyuncun', 'chaoyangpark', 'dawanglu', 'shuangjing', 'gaobeidian', 'dongba']
        total_chaoyang = 0
        
        for area in chaoyang_areas:
            cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area = ?", (area,))
            count = cursor.fetchone()[0]
            total_chaoyang += count
            print(f"{area}: {count}")
        
        print(f"朝阳区9个区域总计: {total_chaoyang}")
        
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_db() 