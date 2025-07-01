#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查重新计算脚本和API响应之间的矛盾原因
"""
import sqlite3
import json
import requests

def main():
    print("🔍 检查重新计算脚本和API响应之间的矛盾...")
    
    # 1. 检查重新计算脚本的统计逻辑
    print("\n📊 检查重新计算脚本的统计逻辑:")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 丰台区东部
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE longitude > 116.321 AND (name LIKE '%丰台%' OR address LIKE '%丰台%')
    """)
    fengtai_east_count = cursor.fetchone()[0]
    
    # 丰台区西部
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE longitude <= 116.321 AND (name LIKE '%丰台%' OR address LIKE '%丰台%')
    """)
    fengtai_west_count = cursor.fetchone()[0]
    
    # 亦庄
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE name LIKE '%亦庄%' OR address LIKE '%亦庄%'
    """)
    yizhuang_count = cursor.fetchone()[0]
    
    print(f"重新计算脚本统计结果:")
    print(f"  丰台区东部: {fengtai_east_count} 个")
    print(f"  丰台区西部: {fengtai_west_count} 个")
    print(f"  亦庄: {yizhuang_count} 个")
    
    # 2. 检查API的统计逻辑
    print("\n🌐 检查API的统计逻辑:")
    try:
        response = requests.get("http://localhost:8000/api/courts/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"API统计结果:")
            print(f"  丰台区东部: {stats['area_stats']['fengtai_east']['count']} 个")
            print(f"  丰台区西部: {stats['area_stats']['fengtai_west']['count']} 个")
            print(f"  亦庄: {stats['area_stats']['yizhuang']['count']} 个")
        else:
            print(f"API请求失败: {response.status_code}")
    except Exception as e:
        print(f"API请求异常: {e}")
    
    # 3. 检查具体的场馆数据
    print("\n🏟️ 检查具体的场馆数据:")
    
    # 丰台区场馆详情
    cursor.execute("""
        SELECT id, name, address, longitude, latitude
        FROM tennis_courts 
        WHERE name LIKE '%丰台%' OR address LIKE '%丰台%'
        ORDER BY longitude
    """)
    fengtai_courts = cursor.fetchall()
    
    print(f"\n丰台区场馆详情 ({len(fengtai_courts)} 个):")
    for court_id, name, address, lng, lat in fengtai_courts:
        area = "丰台区东部" if lng and lng > 116.321 else "丰台区西部"
        print(f"  ID {court_id}: {name}")
        print(f"    地址: {address}")
        print(f"    经度: {lng} -> {area}")
        print()
    
    # 亦庄场馆详情
    cursor.execute("""
        SELECT id, name, address, longitude, latitude
        FROM tennis_courts 
        WHERE name LIKE '%亦庄%' OR address LIKE '%亦庄%'
        ORDER BY name
    """)
    yizhuang_courts = cursor.fetchall()
    
    print(f"\n亦庄场馆详情 ({len(yizhuang_courts)} 个):")
    for court_id, name, address, lng, lat in yizhuang_courts:
        print(f"  ID {court_id}: {name}")
        print(f"    地址: {address}")
        print(f"    经度: {lng}")
        print()
    
    # 4. 检查API筛选逻辑
    print("\n🔍 检查API筛选逻辑:")
    
    # 测试丰台区东部API
    try:
        response = requests.get("http://localhost:8000/api/courts/?area=fengtai_east&limit=100")
        if response.status_code == 200:
            fengtai_east_api = response.json()
            print(f"丰台区东部API返回: {len(fengtai_east_api)} 个场馆")
            for court in fengtai_east_api:
                print(f"  - {court['name']} (经度: {court.get('longitude', 'N/A')})")
        else:
            print(f"丰台区东部API失败: {response.status_code}")
    except Exception as e:
        print(f"丰台区东部API异常: {e}")
    
    # 测试丰台区西部API
    try:
        response = requests.get("http://localhost:8000/api/courts/?area=fengtai_west&limit=100")
        if response.status_code == 200:
            fengtai_west_api = response.json()
            print(f"\n丰台区西部API返回: {len(fengtai_west_api)} 个场馆")
            for court in fengtai_west_api:
                print(f"  - {court['name']} (经度: {court.get('longitude', 'N/A')})")
        else:
            print(f"丰台区西部API失败: {response.status_code}")
    except Exception as e:
        print(f"丰台区西部API异常: {e}")
    
    # 测试亦庄API
    try:
        response = requests.get("http://localhost:8000/api/courts/?area=yizhuang&limit=100")
        if response.status_code == 200:
            yizhuang_api = response.json()
            print(f"\n亦庄API返回: {len(yizhuang_api)} 个场馆")
            for court in yizhuang_api:
                print(f"  - {court['name']} (经度: {court.get('longitude', 'N/A')})")
        else:
            print(f"亦庄API失败: {response.status_code}")
    except Exception as e:
        print(f"亦庄API异常: {e}")
    
    conn.close()
    
    print(f"\n📋 矛盾分析总结:")
    print(f"1. 重新计算脚本统计: 丰台东部{fengtai_east_count}个，丰台西部{fengtai_west_count}个，亦庄{yizhuang_count}个")
    print(f"2. API统计: 需要对比上面的API结果")
    print(f"3. 可能的原因:")
    print(f"   - API筛选逻辑与重新计算脚本不一致")
    print(f"   - 场馆数据在重新计算后被修改")
    print(f"   - API缓存问题")

if __name__ == "__main__":
    main() 