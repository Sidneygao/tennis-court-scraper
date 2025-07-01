#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查姜庄湖网球俱乐部的当前类型
"""
import sqlite3

def main():
    try:
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, address, court_type 
            FROM tennis_courts 
            WHERE name LIKE '%姜庄湖%'
        """)
        
        result = cursor.fetchone()
        if result:
            court_id, name, address, court_type = result
            print(f"场馆ID: {court_id}")
            print(f"名称: {name}")
            print(f"地址: {address}")
            print(f"当前类型: {court_type}")
            
            # 使用新的三层判断法
            name_lower = name.lower()
            address_lower = address.lower()
            full_text = name_lower + " " + address_lower
            
            print(f"\n三层判断法分析:")
            
            # 第一层：硬TAG判断
            if "室内" in name_lower or "气膜" in name_lower:
                print("✅ 第一层：硬TAG判断为室内")
                return
            if "室外" in name_lower:
                print("✅ 第一层：硬TAG判断为室外")
                return
            
            # 第二层：直接关键字判断
            indoor_keywords = ["网球馆", "网球中心", "网球俱乐部", "网球汇", "网球学练馆", "网球训练馆"]
            outdoor_keywords = ["网球场", "网球公园", "网球基地"]
            
            for keyword in indoor_keywords:
                if keyword in name_lower:
                    print(f"✅ 第二层：直接关键字'{keyword}'判断为室内")
                    return
            
            for keyword in outdoor_keywords:
                if keyword in name_lower or keyword in address_lower:
                    print(f"✅ 第二层：直接关键字'{keyword}'判断为室外")
                    return
            
            # 第三层：间接关键字判断
            indoor_indirect = ['层', '楼', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5', '电梯']
            outdoor_indirect = ['网球场', '室外', '露天', '户外']
            
            for keyword in indoor_indirect:
                if keyword in full_text:
                    print(f"✅ 第三层：间接关键字'{keyword}'判断为室内")
                    return
            
            for keyword in outdoor_indirect:
                if keyword in full_text:
                    print(f"✅ 第三层：间接关键字'{keyword}'判断为室外")
                    return
            
            print("❌ 三层判断法都无法确定，应该判定为'未知'")
            print(f"当前类型'{court_type}'是错误的")
            
        else:
            print("❌ 未找到姜庄湖网球俱乐部")
            
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 