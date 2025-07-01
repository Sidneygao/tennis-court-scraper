#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入调查BING价格集中在某些场馆的原因
"""
import json
import sqlite3
from collections import defaultdict, Counter
import re

def main():
    print("🔍 深入调查BING价格集中现象...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 获取BING价格最多的场馆详细信息
    print("\n🏆 分析BING价格最多的场馆:")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.address, cd.bing_prices, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]'
        ORDER BY tc.name
    """)
    
    courts_with_bing = cursor.fetchall()
    
    # 按BING价格数量排序
    court_data = []
    for court_id, court_name, court_type, address, bing_prices, merged_prices in courts_with_bing:
        try:
            bing_data = json.loads(bing_prices) if bing_prices else []
            merged_data = json.loads(merged_prices) if merged_prices else []
            court_data.append((court_id, court_name, court_type, address, bing_data, merged_data))
        except:
            continue
    
    # 按BING价格数量排序
    court_data.sort(key=lambda x: len(x[4]), reverse=True)
    
    print(f"\n📊 前10个BING价格最多的场馆详细分析:")
    for i, (court_id, court_name, court_type, address, bing_data, merged_data) in enumerate(court_data[:10]):
        print(f"\n{i+1}. {court_name}")
        print(f"   场馆类型: {court_type}")
        print(f"   地址: {address}")
        print(f"   BING价格数: {len(bing_data)}")
        print(f"   真实价格数: {len(merged_data)}")
        
        # 分析BING价格内容
        if bing_data:
            price_values = []
            price_types = []
            sources = []
            
            for item in bing_data:
                if isinstance(item, dict):
                    price_str = item.get('price', '')
                    price_type = item.get('type', '')
                    source = item.get('source', '')
                    
                    # 提取价格数值
                    price_match = re.search(r'¥?(\d+(?:\.\d+)?)', price_str)
                    if price_match:
                        price_values.append(float(price_match.group(1)))
                    
                    price_types.append(price_type)
                    sources.append(source)
            
            if price_values:
                print(f"   价格范围: ¥{min(price_values):.0f} - ¥{max(price_values):.0f}")
                print(f"   平均价格: ¥{sum(price_values)/len(price_values):.0f}")
            
            # 统计价格类型
            type_counter = Counter(price_types)
            print(f"   价格类型分布: {dict(type_counter)}")
            
            # 统计来源
            source_counter = Counter(sources)
            print(f"   来源分布: {dict(source_counter)}")
    
    # 2. 分析价格重复情况
    print(f"\n🔄 分析价格重复情况:")
    all_bing_prices = []
    for _, _, _, _, bing_data, _ in court_data:
        for item in bing_data:
            if isinstance(item, dict):
                price_str = item.get('price', '')
                all_bing_prices.append(price_str)
    
    price_counter = Counter(all_bing_prices)
    print(f"   总BING价格数: {len(all_bing_prices)}")
    print(f"   唯一价格数: {len(price_counter)}")
    print(f"   重复率: {(1 - len(price_counter)/len(all_bing_prices))*100:.1f}%")
    
    # 找出最常见的价格
    print(f"\n📈 最常见的价格 (前10个):")
    for price, count in price_counter.most_common(10):
        print(f"   {price}: {count} 次")
    
    # 3. 分析场馆名称相似性
    print(f"\n🏷️ 分析场馆名称相似性:")
    court_names = [court[1] for court in court_data]
    
    # 检查是否有相似名称
    similar_groups = defaultdict(list)
    for name in court_names:
        # 提取关键词
        keywords = re.findall(r'[网球|体育|中心|俱乐部|馆|场]', name)
        key = ''.join(keywords)
        if key:
            similar_groups[key].append(name)
    
    print(f"   按关键词分组的场馆:")
    for key, names in similar_groups.items():
        if len(names) > 1:
            print(f"   {key}: {names}")
    
    # 4. 分析地理位置集中度
    print(f"\n📍 分析地理位置集中度:")
    address_keywords = defaultdict(list)
    for _, court_name, _, address, _, _ in court_data:
        if address:
            # 提取地址关键词
            keywords = re.findall(r'[区|路|街|号|园|村|城]', address)
            key = ''.join(keywords[:2]) if keywords else '其他'
            address_keywords[key].append(court_name)
    
    print(f"   按地址关键词分组的场馆:")
    for key, names in address_keywords.items():
        if len(names) > 1:
            print(f"   {key}: {len(names)} 个场馆 - {names[:3]}{'...' if len(names) > 3 else ''}")
    
    # 5. 分析爬取时间模式
    print(f"\n⏰ 分析爬取时间模式:")
    timestamps = []
    for _, _, _, _, bing_data, _ in court_data:
        for item in bing_data:
            if isinstance(item, dict):
                timestamp = item.get('timestamp', '')
                if timestamp:
                    timestamps.append(timestamp)
    
    if timestamps:
        print(f"   有时间戳的价格: {len(timestamps)} 个")
        # 分析时间分布
        time_counter = Counter(timestamps)
        print(f"   时间分布 (前5个):")
        for time, count in time_counter.most_common(5):
            print(f"   {time}: {count} 次")
    
    # 6. 分析爬取策略影响
    print(f"\n🤖 分析爬取策略影响:")
    
    # 检查是否有批量爬取的痕迹
    batch_patterns = defaultdict(int)
    for _, _, _, _, bing_data, _ in court_data:
        if len(bing_data) > 10:  # 大量价格的场馆
            # 分析价格模式
            price_patterns = []
            for item in bing_data:
                if isinstance(item, dict):
                    price_str = item.get('price', '')
                    # 提取价格模式
                    pattern = re.sub(r'\d+', 'N', price_str)
                    price_patterns.append(pattern)
            
            pattern_key = '|'.join(sorted(set(price_patterns)))
            batch_patterns[pattern_key] += 1
    
    print(f"   大量价格场馆的价格模式:")
    for pattern, count in batch_patterns.items():
        if count > 1:
            print(f"   模式 {count} 个场馆: {pattern[:100]}{'...' if len(pattern) > 100 else ''}")
    
    # 7. 总结分析
    print(f"\n📋 集中现象总结:")
    
    # 计算集中度指标
    total_prices = sum(len(court[4]) for court in court_data)
    top_5_prices = sum(len(court[4]) for court in court_data[:5])
    top_10_prices = sum(len(court[4]) for court in court_data[:10])
    
    print(f"   前5个场馆占总BING价格: {top_5_prices/total_prices*100:.1f}%")
    print(f"   前10个场馆占总BING价格: {top_10_prices/total_prices*100:.1f}%")
    
    # 分析可能原因
    print(f"\n🔍 可能的原因分析:")
    
    # 检查是否有重复场馆
    name_counter = Counter([court[1] for court in court_data])
    duplicates = {name: count for name, count in name_counter.items() if count > 1}
    if duplicates:
        print(f"   1. 重复场馆: {duplicates}")
    
    # 检查价格质量
    low_quality_count = 0
    for _, _, _, _, bing_data, _ in court_data:
        for item in bing_data:
            if isinstance(item, dict):
                price_str = item.get('price', '')
                # 检查异常价格
                if any(keyword in price_str for keyword in ['¥10', '¥20', '¥1000', '¥1400']):
                    low_quality_count += 1
    
    print(f"   2. 低质量价格: {low_quality_count} 个")
    
    # 检查爬取策略
    large_courts = [court for court in court_data if len(court[4]) > 20]
    print(f"   3. 大量价格场馆: {len(large_courts)} 个")
    
    conn.close()
    print(f"\n✅ 调查完成!")

if __name__ == "__main__":
    main() 