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
    db_path = 'data/courts.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 测试一个已知有真实价格的场馆
    court_id = 102
    
    try:
        # 查询court_details表中的prices字段
        cursor.execute("SELECT prices, merged_prices, bing_prices FROM court_details WHERE court_id=?", (court_id,))
        row = cursor.fetchone()
        if not row:
            print(f"未找到court_id={court_id}的数据")
            return
        prices, merged_prices, bing_prices = row
        print(f"court_id={court_id}")
        print("\n[prices字段]")
        try:
            prices_json = json.loads(prices) if prices else []
            print(json.dumps(prices_json, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析失败: {e}")
        print("\n[merged_prices字段]")
        try:
            merged_json = json.loads(merged_prices) if merged_prices else []
            print(json.dumps(merged_json, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析失败: {e}")
        print("\n[bing_prices字段]")
        try:
            bing_json = json.loads(bing_prices) if bing_prices else []
            print(json.dumps(bing_json, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"解析失败: {e}")
        
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