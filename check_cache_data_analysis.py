#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析缓存数据的完整性：场馆数量、类型计算、价格计算状态
"""
import json
import sqlite3
from collections import defaultdict

def main():
    print("🔍 分析缓存数据完整性...")
    
    # 1. 分析 real_courts_locations.json
    print("\n📊 分析 real_courts_locations.json:")
    try:
        with open('real_courts_locations.json', 'r', encoding='utf-8') as f:
            courts_data = json.load(f)
        
        print(f"缓存中总场馆数: {len(courts_data)}")
        
        # 统计丰台和亦庄场馆
        fengtai_count = 0
        yizhuang_count = 0
        fengtai_courts = []
        yizhuang_courts = []
        
        for court in courts_data:
            name = court.get('name', '')
            address = court.get('address', '')
            longitude = court.get('longitude', 0)
            
            if '丰台' in name or '丰台' in address:
                fengtai_count += 1
                fengtai_courts.append({
                    'name': name,
                    'longitude': longitude,
                    'area': '丰台区东部' if longitude > 116.321 else '丰台区西部'
                })
            elif '亦庄' in name or '亦庄' in address:
                yizhuang_count += 1
                yizhuang_courts.append({
                    'name': name,
                    'longitude': longitude
                })
        
        print(f"丰台区场馆数: {fengtai_count}")
        print(f"亦庄场馆数: {yizhuang_count}")
        
        # 按经度划分丰台区
        fengtai_east = [c for c in fengtai_courts if c['longitude'] > 116.321]
        fengtai_west = [c for c in fengtai_courts if c['longitude'] <= 116.321]
        
        print(f"  丰台区东部: {len(fengtai_east)} 家")
        print(f"  丰台区西部: {len(fengtai_west)} 家")
        
        # 显示样本
        print("\n丰台区东部样本:")
        for court in fengtai_east[:5]:
            print(f"  - {court['name']} (经度: {court['longitude']})")
        
        print("\n丰台区西部样本:")
        for court in fengtai_west[:5]:
            print(f"  - {court['name']} (经度: {court['longitude']})")
        
        print("\n亦庄样本:")
        for court in yizhuang_courts[:5]:
            print(f"  - {court['name']} (经度: {court['longitude']})")
            
    except Exception as e:
        print(f"读取 real_courts_locations.json 失败: {e}")
    
    # 2. 检查数据库中的场馆状态
    print("\n📊 检查数据库状态:")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查数据库中的丰台和亦庄场馆
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE address LIKE '%丰台%' OR name LIKE '%丰台%'
    """)
    db_fengtai = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE address LIKE '%亦庄%' OR name LIKE '%亦庄%'
    """)
    db_yizhuang = cursor.fetchone()[0]
    
    print(f"数据库中丰台区场馆: {db_fengtai}")
    print(f"数据库中亦庄场馆: {db_yizhuang}")
    
    # 3. 检查类型计算状态
    print("\n🔍 检查类型计算状态:")
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE court_type IS NOT NULL AND court_type != ''
    """)
    typed_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_count = cursor.fetchone()[0]
    
    print(f"已计算类型的场馆: {typed_count}/{total_count} ({typed_count/total_count*100:.1f}%)")
    
    # 4. 检查价格计算状态
    print("\n💰 检查价格计算状态:")
    cursor.execute("""
        SELECT COUNT(*) FROM court_details 
        WHERE predict_prices IS NOT NULL AND predict_prices != ''
    """)
    predicted_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM court_details")
    detail_count = cursor.fetchone()[0]
    
    print(f"已预测价格的场馆: {predicted_count}/{detail_count} ({predicted_count/detail_count*100:.1f}%)")
    
    # 5. 检查真实价格状态
    cursor.execute("""
        SELECT COUNT(*) FROM court_details 
        WHERE merged_prices IS NOT NULL AND merged_prices != ''
    """)
    real_price_count = cursor.fetchone()[0]
    
    print(f"有真实价格的场馆: {real_price_count}/{detail_count} ({real_price_count/detail_count*100:.1f}%)")
    
    conn.close()
    
    # 6. 总结和建议
    print("\n📋 总结和建议:")
    print(f"1. 缓存数据可用性: ✅ 缓存中有 {len(courts_data)} 个场馆")
    print(f"2. 丰台区数据: 缓存 {fengtai_count} 个，数据库 {db_fengtai} 个")
    print(f"3. 亦庄数据: 缓存 {yizhuang_count} 个，数据库 {db_yizhuang} 个")
    print(f"4. 类型计算: {typed_count/total_count*100:.1f}% 完成")
    print(f"5. 价格预测: {predicted_count/detail_count*100:.1f}% 完成")
    
    if db_fengtai < fengtai_count or db_yizhuang < yizhuang_count:
        print("\n⚠️  建议: 需要从缓存恢复缺失的场馆数据")
    else:
        print("\n✅ 数据库数据完整，无需恢复")

if __name__ == "__main__":
    main() 