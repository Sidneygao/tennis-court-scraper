#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查浩生体育网球俱乐部(望京店)的详细信息
"""
import sqlite3
import json

def main():
    print("🔍 检查浩生体育网球俱乐部(望京店)的详细信息...")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查找这个场馆
    court_name = "浩生体育网球俱乐部(望京店)"
    
    cursor.execute("""
        SELECT id, name, address, court_type, area, latitude, longitude
        FROM tennis_courts
        WHERE name LIKE ?
    """, (f"%{court_name}%",))
    
    result = cursor.fetchone()
    
    if result:
        court_id, name, address, court_type, area, lat, lon = result
        print(f"\n📊 场馆基本信息:")
        print(f"   ID: {court_id}")
        print(f"   名称: {name}")
        print(f"   地址: {address}")
        print(f"   当前类型: {court_type}")
        print(f"   区域: {area}")
        print(f"   坐标: {lat}, {lon}")
        
        # 检查详情数据
        cursor.execute("""
            SELECT prices, predict_prices, bing_prices
            FROM court_details
            WHERE court_id = ?
        """, (court_id,))
        
        detail_result = cursor.fetchone()
        if detail_result:
            prices, predict_prices, bing_prices = detail_result
            print(f"\n💰 价格信息:")
            print(f"   真实价格: {prices}")
            print(f"   预测价格: {predict_prices}")
            print(f"   BING价格: {bing_prices}")
        
        # 分析地址中的关键字
        print(f"\n🔍 地址分析:")
        address_lower = address.lower()
        
        # 第一层关键字
        indoor_keywords = ['室内', '气膜', '馆']
        outdoor_keywords = ['室外', '露天', '场']
        
        # 第二层关键字
        tennis_keywords = ['网球馆', '网球场']
        
        print(f"   地址: {address}")
        print(f"   地址(小写): {address_lower}")
        
        # 检查第一层关键字
        indoor_found = [kw for kw in indoor_keywords if kw in address_lower]
        outdoor_found = [kw for kw in outdoor_keywords if kw in address_lower]
        
        print(f"   第一层室内关键字: {indoor_found}")
        print(f"   第一层室外关键字: {outdoor_found}")
        
        # 检查第二层关键字
        tennis_found = [kw for kw in tennis_keywords if kw in address_lower]
        print(f"   第二层网球关键字: {tennis_found}")
        
        # 判断逻辑
        print(f"\n🎯 类型判断逻辑:")
        if indoor_found:
            print(f"   ✅ 发现室内关键字: {indoor_found}")
            print(f"   应该判断为: 室内")
        elif outdoor_found:
            print(f"   ✅ 发现室外关键字: {outdoor_found}")
            print(f"   应该判断为: 室外")
        elif tennis_found:
            print(f"   ✅ 发现网球关键字: {tennis_found}")
            if '场' in address_lower:
                print(f"   包含'场'字，应该判断为: 室外")
            elif '馆' in address_lower:
                print(f"   包含'馆'字，应该判断为: 室内")
            else:
                print(f"   默认判断为: 室外")
        else:
            print(f"   ⚠️  未发现明确关键字")
        
        print(f"\n📝 结论:")
        if '网球场' in address_lower:
            print(f"   ❌ 当前类型错误: {court_type}")
            print(f"   ✅ 应该修改为: 室外")
        else:
            print(f"   ✅ 当前类型正确: {court_type}")
            
    else:
        print(f"❌ 未找到场馆: {court_name}")
    
    conn.close()

if __name__ == "__main__":
    main() 