#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析价格分布情况：解释BING价格多但真实价格少的原因
"""
import json
import sqlite3
from collections import defaultdict, Counter

def main():
    print("🔍 分析价格分布情况...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 统计各类型价格数据
    print("\n📊 价格数据类型统计:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]' THEN 1 ELSE 0 END) as has_bing_prices,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL AND cd.merged_prices != '' AND cd.merged_prices != '[]' THEN 1 ELSE 0 END) as has_merged_prices,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL AND cd.predict_prices != '' AND cd.predict_prices != '[]' THEN 1 ELSE 0 END) as has_predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    stats = cursor.fetchone()
    print(f"  总场馆数: {stats[0]}")
    print(f"  有BING价格: {stats[1]} 个场馆")
    print(f"  有真实价格: {stats[2]} 个场馆")
    print(f"  有预测价格: {stats[3]} 个场馆")
    
    # 2. 分析BING价格分布
    print("\n🔍 BING价格分布分析:")
    cursor.execute("""
        SELECT tc.name, tc.court_type, cd.bing_prices, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]'
        ORDER BY tc.name
    """)
    
    courts_with_bing = cursor.fetchall()
    
    # 统计每个场馆的BING价格数量
    bing_price_counts = []
    court_types = defaultdict(int)
    total_bing_prices = 0
    
    for court_name, court_type, bing_prices, merged_prices in courts_with_bing:
        try:
            bing_data = json.loads(bing_prices) if bing_prices else []
            merged_data = json.loads(merged_prices) if merged_prices else []
            
            bing_count = len(bing_data)
            merged_count = len(merged_data)
            
            bing_price_counts.append((court_name, court_type, bing_count, merged_count))
            court_types[court_type or '未知'] += 1
            total_bing_prices += bing_count
            
        except Exception as e:
            print(f"  解析失败 {court_name}: {e}")
    
    print(f"\n📈 BING价格总数: {total_bing_prices}")
    print(f"  场馆类型分布:")
    for court_type, count in court_types.items():
        print(f"    {court_type}: {count} 个场馆")
    
    # 3. 分析价格数量分布
    print(f"\n📊 各场馆BING价格数量分布:")
    price_count_distribution = Counter([count for _, _, count, _ in bing_price_counts])
    for count, num_courts in sorted(price_count_distribution.items()):
        print(f"  {count} 个价格: {num_courts} 个场馆")
    
    # 4. 找出价格最多的场馆
    print(f"\n🏆 BING价格最多的场馆 (前10名):")
    sorted_courts = sorted(bing_price_counts, key=lambda x: x[2], reverse=True)
    for i, (court_name, court_type, bing_count, merged_count) in enumerate(sorted_courts[:10]):
        print(f"  {i+1}. {court_name} ({court_type}): {bing_count} 个BING价格, {merged_count} 个真实价格")
    
    # 5. 分析真实价格分布
    print(f"\n📋 真实价格分布分析:")
    courts_with_merged = [c for c in bing_price_counts if c[3] > 0]
    courts_without_merged = [c for c in bing_price_counts if c[3] == 0]
    
    print(f"  有真实价格的场馆: {len(courts_with_merged)} 个")
    print(f"  无真实价格的场馆: {len(courts_without_merged)} 个")
    
    if courts_with_merged:
        print(f"\n✅ 有真实价格的场馆 (前10名):")
        sorted_with_merged = sorted(courts_with_merged, key=lambda x: x[3], reverse=True)
        for i, (court_name, court_type, bing_count, merged_count) in enumerate(sorted_with_merged[:10]):
            print(f"  {i+1}. {court_name} ({court_type}): {merged_count} 个真实价格, {bing_count} 个BING价格")
    
    # 6. 分析价格集中度
    print(f"\n🎯 价格集中度分析:")
    total_courts = len(bing_price_counts)
    top_10_courts_bing = sum([count for _, _, count, _ in sorted_courts[:10]])
    top_20_courts_bing = sum([count for _, _, count, _ in sorted_courts[:20]])
    
    print(f"  前10个场馆的BING价格: {top_10_courts_bing} 个 ({top_10_courts_bing/total_bing_prices*100:.1f}%)")
    print(f"  前20个场馆的BING价格: {top_20_courts_bing} 个 ({top_20_courts_bing/total_bing_prices*100:.1f}%)")
    
    # 7. 分析为什么真实价格少
    print(f"\n🤔 真实价格少的原因分析:")
    
    # 统计有BING但无真实价格的场馆
    no_real_prices = [c for c in bing_price_counts if c[3] == 0]
    print(f"  有BING但无真实价格的场馆: {len(no_real_prices)} 个")
    
    if no_real_prices:
        print(f"  这些场馆的BING价格总数: {sum([c[2] for c in no_real_prices])} 个")
        print(f"  平均每个场馆BING价格数: {sum([c[2] for c in no_real_prices])/len(no_real_prices):.1f} 个")
    
    # 8. 分析场馆类型与真实价格的关系
    print(f"\n🏟️ 场馆类型与真实价格关系:")
    type_stats = defaultdict(lambda: {'total': 0, 'with_merged': 0, 'total_bing': 0, 'total_merged': 0})
    
    for court_name, court_type, bing_count, merged_count in bing_price_counts:
        court_type = court_type or '未知'
        type_stats[court_type]['total'] += 1
        type_stats[court_type]['total_bing'] += bing_count
        type_stats[court_type]['total_merged'] += merged_count
        if merged_count > 0:
            type_stats[court_type]['with_merged'] += 1
    
    for court_type, stats in type_stats.items():
        if stats['total'] > 0:
            merged_ratio = stats['with_merged'] / stats['total'] * 100
            avg_bing = stats['total_bing'] / stats['total']
            avg_merged = stats['total_merged'] / stats['total']
            print(f"  {court_type}: {stats['total']} 个场馆, {stats['with_merged']} 个有真实价格 ({merged_ratio:.1f}%), 平均BING价格 {avg_bing:.1f} 个, 平均真实价格 {avg_merged:.1f} 个")
    
    conn.close()
    
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main() 