#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查浩生体育网球俱乐部的当前类型
"""
import sqlite3

def main():
    try:
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, address, court_type 
            FROM tennis_courts 
            WHERE name LIKE '%浩生体育%'
        """)
        
        result = cursor.fetchone()
        if result:
            name, address, court_type = result
            print(f"名称: {name}")
            print(f"地址: {address}")
            print(f"当前类型: {court_type}")
            
            # 检查地址中的关键字
            address_lower = address.lower()
            if '网球场' in address_lower:
                print(f"✅ 地址包含'网球场'，应该判断为室外")
                if court_type == '室外':
                    print(f"✅ 当前类型正确")
                else:
                    print(f"❌ 当前类型错误，应该是室外")
            else:
                print(f"❌ 地址不包含'网球场'")
        else:
            print("未找到浩生体育网球俱乐部")
        
        conn.close()
        print("检查完成")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main() 