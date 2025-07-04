#!/usr/bin/env python3
"""
检查数据库中还有哪些场馆有真实的设施描述信息
"""

import sqlite3
import json

def check_real_facilities():
    """检查数据库中还有哪些场馆有真实的设施描述信息"""
    db_path = "data/courts.db"
    
    print("🔍 检查数据库中还有哪些场馆有真实的设施描述信息...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有详情记录
        cursor.execute("""
            SELECT cd.id, cd.court_id, tc.name, cd.merged_description, cd.merged_facilities 
            FROM court_details cd
            JOIN tennis_courts tc ON cd.court_id = tc.id
            WHERE (cd.merged_description IS NOT NULL AND cd.merged_description != '') 
               OR (cd.merged_facilities IS NOT NULL AND cd.merged_facilities != '')
        """)
        rows = cursor.fetchall()
        
        print(f"📊 找到 {len(rows)} 条有描述或设施信息的记录:")
        
        real_count = 0
        
        for detail_id, court_id, name, description, facilities in rows:
            print(f"\n--- 场馆ID: {court_id}, 名称: {name} ---")
            
            has_real_info = False
            
            if description and description.strip():
                print(f"  描述: {description[:100]}...")
                has_real_info = True
            
            if facilities and facilities.strip():
                print(f"  设施: {facilities[:100]}...")
                has_real_info = True
            
            if has_real_info:
                real_count += 1
        
        print(f"\n📈 统计结果:")
        print(f"  有描述或设施信息的场馆: {real_count} 个")
        print(f"  总计详情记录: {len(rows)} 条")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    check_real_facilities() 