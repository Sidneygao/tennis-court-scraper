#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复浩生体育网球俱乐部(望京店)的场馆类型
"""
import sqlite3
from datetime import datetime

def main():
    print("🔧 修复浩生体育网球俱乐部(望京店)的场馆类型...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查找并修复场馆类型
    court_name = "浩生体育网球俱乐部(望京店)"
    
    try:
        # 查找场馆
        cursor.execute("""
            SELECT id, name, address, court_type
            FROM tennis_courts
            WHERE name LIKE ?
        """, (f"%{court_name}%",))
        
        result = cursor.fetchone()
        
        if result:
            court_id, name, address, old_type = result
            print(f"\n📊 修复前信息:")
            print(f"   ID: {court_id}")
            print(f"   名称: {name}")
            print(f"   地址: {address}")
            print(f"   原类型: {old_type}")
            
            # 修复类型为室外
            new_type = "室外"
            cursor.execute("""
                UPDATE tennis_courts
                SET court_type = ?, updated_at = ?
                WHERE id = ?
            """, (new_type, datetime.now(), court_id))
            
            print(f"\n✅ 修复完成:")
            print(f"   原类型: {old_type} → 新类型: {new_type}")
            
            # 验证修复结果
            cursor.execute("""
                SELECT court_type
                FROM tennis_courts
                WHERE id = ?
            """, (court_id,))
            
            updated_type = cursor.fetchone()[0]
            print(f"   验证结果: {updated_type}")
            
            conn.commit()
            print(f"✅ 数据库更新成功")
            
        else:
            print(f"❌ 未找到场馆: {court_name}")
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 