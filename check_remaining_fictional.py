#!/usr/bin/env python3
"""
检查数据库中是否还有虚构描述和设施留存
"""

import sqlite3
import re

def check_remaining_fictional():
    """检查数据库中是否还有虚构描述和设施留存"""
    db_path = "data/courts.db"
    
    print("🔍 检查数据库中是否还有虚构描述和设施留存...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 虚构数据的关键词模式
        fictional_patterns = [
            r'是一家专业的网球场地',
            r'设施完善',
            r'环境优美',
            r'免费停车',
            r'淋浴设施',
            r'更衣室',
            r'休息区',
            r'模板',
            r'示例',
            r'虚构',
            r'测试',
            r'demo'
        ]
        
        # 查询所有详情记录
        cursor.execute("SELECT id, court_id, merged_description, merged_facilities FROM court_details")
        rows = cursor.fetchall()
        
        found_count = 0
        
        for detail_id, court_id, description, facilities in rows:
            found_fictional = False
            
            # 检查描述是否包含虚构内容
            if description:
                for pattern in fictional_patterns:
                    if re.search(pattern, description, re.IGNORECASE):
                        print(f"❌ 发现虚构描述 (详情ID: {detail_id}, 场馆ID: {court_id}): {description[:100]}...")
                        found_fictional = True
                        break
            
            # 检查设施是否包含虚构内容
            if facilities:
                for pattern in fictional_patterns:
                    if re.search(pattern, facilities, re.IGNORECASE):
                        print(f"❌ 发现虚构设施 (详情ID: {detail_id}, 场馆ID: {court_id}): {facilities[:100]}...")
                        found_fictional = True
                        break
            
            if found_fictional:
                found_count += 1
        
        conn.close()
        
        if found_count == 0:
            print("✅ 没有发现虚构描述和设施留存")
        else:
            print(f"⚠️ 发现 {found_count} 条记录仍有虚构内容")
        
        return found_count == 0
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    check_remaining_fictional() 