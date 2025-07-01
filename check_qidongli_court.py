#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查齐动力网球(丽泽店)的当前类型
"""
import sqlite3

def main():
    try:
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, address, court_type 
            FROM tennis_courts 
            WHERE name LIKE '%齐动力%' AND name LIKE '%丽泽%'
        """)
        
        result = cursor.fetchone()
        if result:
            name, address, court_type = result
            print(f"名称: {name}")
            print(f"地址: {address}")
            print(f"当前类型: {court_type}")
            
            # 检查地址中的关键字
            address_lower = address.lower()
            
            # 第三层间接关键字检查
            indoor_keywords = ['层', '楼', '电梯', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5']
            outdoor_keywords = ['网球场', '室外', '露天', '户外']
            
            print(f"\n地址关键字分析:")
            print(f"地址内容: {address}")
            
            # 检查室内关键字
            indoor_found = []
            for keyword in indoor_keywords:
                if keyword in address_lower:
                    indoor_found.append(keyword)
            
            # 检查室外关键字
            outdoor_found = []
            for keyword in outdoor_keywords:
                if keyword in address_lower:
                    outdoor_found.append(keyword)
            
            if indoor_found:
                print(f"✅ 发现室内关键字: {indoor_found}")
            if outdoor_found:
                print(f"✅ 发现室外关键字: {outdoor_found}")
            
            # 判断应该的类型
            if indoor_found and not outdoor_found:
                should_be = "室内"
                print(f"🔍 根据地址关键字，应该判定为: {should_be}")
                if court_type == should_be:
                    print(f"✅ 当前类型正确")
                else:
                    print(f"❌ 当前类型错误，应该是 {should_be}")
            elif outdoor_found and not indoor_found:
                should_be = "室外"
                print(f"🔍 根据地址关键字，应该判定为: {should_be}")
                if court_type == should_be:
                    print(f"✅ 当前类型正确")
                else:
                    print(f"❌ 当前类型错误，应该是 {should_be}")
            else:
                print(f"⚠️ 地址关键字冲突或不足，需要进一步判断")
                
        else:
            print("❌ 未找到齐动力网球(丽泽店)")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    main() 