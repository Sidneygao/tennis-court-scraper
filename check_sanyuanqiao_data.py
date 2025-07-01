#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查三元桥区域数据
"""
import sqlite3

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查三元桥区域场馆数量
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area = 'sanyuanqiao'")
    count = cursor.fetchone()[0]
    print(f"三元桥区域场馆数量: {count}")
    
    # 检查所有区域分布
    cursor.execute("SELECT area, COUNT(*) FROM tennis_courts GROUP BY area ORDER BY COUNT(*) DESC")
    areas = cursor.fetchall()
    print("\n各区域场馆分布:")
    for area, count in areas:
        print(f"  {area}: {count}")
    
    # 检查三元桥区域的具体场馆
    if count > 0:
        cursor.execute("SELECT name, area FROM tennis_courts WHERE area = 'sanyuanqiao' LIMIT 10")
        courts = cursor.fetchall()
        print(f"\n三元桥区域场馆列表:")
        for name, area in courts:
            print(f"  {name}: {area}")
    else:
        print("\n三元桥区域没有场馆数据")
    
    conn.close()

if __name__ == "__main__":
    main() 