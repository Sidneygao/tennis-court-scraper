#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从geojson_predict_results.json中提取丰台和亦庄的场馆数据
"""
import json
import sqlite3

def main():
    print("🔍 从缓存中提取丰台和亦庄场馆数据...")
    
    # 读取geojson_predict_results.json
    try:
        with open('geojson_predict_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"缓存中总场馆数: {len(data)}")
        
        # 提取丰台和亦庄场馆
        fengtai_courts = []
        yizhuang_courts = []
        
        for court in data:
            name = court.get('name', '')
            address = court.get('address', '')
            longitude = court.get('longitude', 0)
            latitude = court.get('latitude', 0)
            court_id = court.get('court_id', 0)
            
            if '丰台' in name or '丰台' in address:
                fengtai_courts.append({
                    'court_id': court_id,
                    'name': name,
                    'address': address,
                    'longitude': longitude,
                    'latitude': latitude,
                    'area': '丰台区东部' if longitude > 116.321 else '丰台区西部'
                })
            elif '亦庄' in name or '亦庄' in address:
                yizhuang_courts.append({
                    'court_id': court_id,
                    'name': name,
                    'address': address,
                    'longitude': longitude,
                    'latitude': latitude,
                    'area': '亦庄'
                })
        
        print(f"\n📊 提取结果:")
        print(f"丰台区场馆数: {len(fengtai_courts)}")
        print(f"亦庄场馆数: {len(yizhuang_courts)}")
        
        # 按经度划分丰台区
        fengtai_east = [c for c in fengtai_courts if c['longitude'] > 116.321]
        fengtai_west = [c for c in fengtai_courts if c['longitude'] <= 116.321]
        
        print(f"\n丰台区东部: {len(fengtai_east)} 家")
        for court in fengtai_east:
            print(f"  - {court['name']} (经度: {court['longitude']})")
        
        print(f"\n丰台区西部: {len(fengtai_west)} 家")
        for court in fengtai_west:
            print(f"  - {court['name']} (经度: {court['longitude']})")
        
        print(f"\n亦庄: {len(yizhuang_courts)} 家")
        for court in yizhuang_courts:
            print(f"  - {court['name']} (经度: {court['longitude']})")
        
        # 检查数据库中是否已有这些场馆
        print(f"\n🔍 检查数据库状态:")
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        
        # 检查丰台区场馆
        cursor.execute("""
            SELECT name, address FROM tennis_courts 
            WHERE address LIKE '%丰台%' OR name LIKE '%丰台%'
        """)
        db_fengtai = cursor.fetchall()
        
        cursor.execute("""
            SELECT name, address FROM tennis_courts 
            WHERE address LIKE '%亦庄%' OR name LIKE '%亦庄%'
        """)
        db_yizhuang = cursor.fetchall()
        
        print(f"数据库中丰台区场馆: {len(db_fengtai)}")
        for name, address in db_fengtai:
            print(f"  - {name}")
        
        print(f"数据库中亦庄场馆: {len(db_yizhuang)}")
        for name, address in db_yizhuang:
            print(f"  - {name}")
        
        conn.close()
        
        # 总结
        print(f"\n📋 总结:")
        print(f"1. 缓存中丰台区场馆: {len(fengtai_courts)} 个")
        print(f"2. 缓存中亦庄场馆: {len(yizhuang_courts)} 个")
        print(f"3. 数据库中丰台区场馆: {len(db_fengtai)} 个")
        print(f"4. 数据库中亦庄场馆: {len(db_yizhuang)} 个")
        
        if len(fengtai_courts) > len(db_fengtai) or len(yizhuang_courts) > len(db_yizhuang):
            print(f"\n⚠️  需要从缓存恢复数据")
            return fengtai_courts + yizhuang_courts
        else:
            print(f"\n✅ 数据库数据完整")
            return []
            
    except Exception as e:
        print(f"读取缓存文件失败: {e}")
        return []

if __name__ == "__main__":
    main() 