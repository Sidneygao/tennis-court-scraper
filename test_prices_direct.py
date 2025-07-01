#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试数据库中的prices字段数据
"""
import sqlite3
import json

def main():
    print("🔍 直接测试数据库中的prices字段数据...")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 测试一个已知有真实价格的场馆
    court_id = 1  # SOLOTennis网球俱乐部
    
    try:
        # 查询court_details表中的prices字段
        cursor.execute("""
            SELECT cd.prices, tc.name
            FROM court_details cd
            JOIN tennis_courts tc ON cd.court_id = tc.id
            WHERE cd.court_id = ?
        """, (court_id,))
        
        result = cursor.fetchone()
        
        if result:
            prices_data, court_name = result
            print(f"\n📊 数据库查询结果:")
            print(f"   场馆名称: {court_name}")
            print(f"   prices字段原始值: {prices_data}")
            
            if prices_data:
                try:
                    prices_json = json.loads(prices_data)
                    print(f"   prices字段解析结果: {len(prices_json)} 个价格")
                    print(f"   价格示例: {prices_json[:2]}")
                except Exception as e:
                    print(f"   ❌ JSON解析失败: {e}")
            else:
                print(f"   ⚠️  prices字段为空")
        else:
            print(f"❌ 未找到场馆ID {court_id} 的数据")
        
        # 检查所有有prices数据的场馆
        cursor.execute("""
            SELECT cd.court_id, tc.name, cd.prices
            FROM court_details cd
            JOIN tennis_courts tc ON cd.court_id = tc.id
            WHERE cd.prices IS NOT NULL AND cd.prices != ''
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        print(f"\n📊 有prices数据的场馆 (前5个):")
        for court_id, name, prices in results:
            try:
                prices_json = json.loads(prices)
                print(f"   {court_id}. {name} - {len(prices_json)} 个价格")
            except:
                print(f"   {court_id}. {name} - JSON解析失败")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 