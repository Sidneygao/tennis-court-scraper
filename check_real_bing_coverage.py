#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查真实的BING价格覆盖率
区分有实际价格数据的场馆和空数组的场馆
"""
import json
import sqlite3

def main():
    print("🔍 检查真实的BING价格覆盖率...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 查询所有场馆的BING价格数据
    cursor.execute("""
        SELECT tc.id, tc.name, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        ORDER BY tc.id
    """)
    
    results = cursor.fetchall()
    
    total_courts = len(results)
    has_bing_prices_field = 0
    has_actual_prices = 0
    empty_arrays = 0
    null_fields = 0
    
    print(f"\n📊 详细统计:")
    
    for court_id, name, bing_prices in results:
        if bing_prices is None:
            null_fields += 1
            print(f"  ❌ {court_id}: {name} - bing_prices字段为NULL")
        else:
            has_bing_prices_field += 1
            try:
                prices_data = json.loads(bing_prices)
                if isinstance(prices_data, list):
                    if len(prices_data) > 0:
                        has_actual_prices += 1
                        print(f"  ✅ {court_id}: {name} - 有{len(prices_data)}个价格")
                    else:
                        empty_arrays += 1
                        print(f"  ⚠️  {court_id}: {name} - 空数组[]")
                else:
                    empty_arrays += 1
                    print(f"  ⚠️  {court_id}: {name} - 非数组格式")
            except json.JSONDecodeError:
                empty_arrays += 1
                print(f"  ⚠️  {court_id}: {name} - JSON解析失败")
    
    print(f"\n📈 覆盖率统计:")
    print(f"  总场馆数: {total_courts}")
    print(f"  有bing_prices字段: {has_bing_prices_field} ({has_bing_prices_field/total_courts*100:.1f}%)")
    print(f"  有实际价格数据: {has_actual_prices} ({has_actual_prices/total_courts*100:.1f}%)")
    print(f"  空数组或无效: {empty_arrays} ({empty_arrays/total_courts*100:.1f}%)")
    print(f"  字段为NULL: {null_fields} ({null_fields/total_courts*100:.1f}%)")
    
    # 检查BING爬取结果文件
    print(f"\n📄 检查BING爬取结果文件...")
    try:
        with open('bing_price_results_enhanced_20250629_175521.json', 'r', encoding='utf-8') as f:
            bing_data = json.load(f)
        
        file_total = bing_data.get('total_courts', 0)
        file_success = bing_data.get('success_count', 0)
        file_prices = bing_data.get('total_prices_found', 0)
        
        print(f"  BING文件统计:")
        print(f"    总场馆数: {file_total}")
        print(f"    成功数: {file_success}")
        print(f"    总价格数: {file_prices}")
        
        # 统计实际有价格的场馆
        actual_priced_courts = 0
        for result in bing_data.get('results', []):
            if result.get('prices') and len(result['prices']) > 0:
                actual_priced_courts += 1
        
        print(f"    实际有价格的场馆: {actual_priced_courts} ({actual_priced_courts/file_total*100:.1f}%)")
        
    except FileNotFoundError:
        print("  ❌ 找不到BING结果文件")
    except json.JSONDecodeError:
        print("  ❌ BING结果文件格式错误")
    
    conn.close()

if __name__ == "__main__":
    main() 