#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新计算所有场馆的预测价格
包括受保护的BING价格数据和其他预测数据
"""
import json
import sqlite3
import sys
import os
from datetime import datetime
import re

def main():
    print("🔄 开始重新计算所有场馆的预测价格...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 连接数据库
    print("\n🗄️ 第一步：连接数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 2. 获取所有场馆信息
    print("\n📖 第二步：获取所有场馆信息...")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.area,
               cd.prices, cd.bing_prices, cd.predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        ORDER BY tc.id
    """)
    
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个场馆")
    
    # 3. 重新计算每个场馆的预测价格
    print("\n🔄 第三步：重新计算预测价格...")
    processed_count = 0
    skipped_count = 0
    protected_count = 0
    
    for court_id, court_name, court_type, area, prices, bing_prices, predict_prices in results:
        try:
            # 收集所有可用的价格数据
            all_prices = []
            price_sources = []
            
            # 1. 检查真实价格
            if prices:
                try:
                    real_data = json.loads(prices)
                    if isinstance(real_data, list):
                        for price_info in real_data:
                            if isinstance(price_info, dict) and 'price' in price_info:
                                price = price_info['price']
                                if isinstance(price, (int, float)):
                                    all_prices.append(price)
                                    price_sources.append('real')
                    elif isinstance(real_data, dict) and 'prices' in real_data:
                        for price in real_data['prices']:
                            if isinstance(price, (int, float)):
                                all_prices.append(price)
                                price_sources.append('real')
                except:
                    pass
            
            # 2. 检查BING价格（如果存在且未在predict_prices中）
            if bing_prices and bing_prices != '[]':
                try:
                    bing_data = json.loads(bing_prices)
                    if isinstance(bing_data, list):
                        for price_info in bing_data:
                            price_str = price_info.get('price', '')
                            price_match = re.search(r'¥(\d+)', price_str)
                            if price_match:
                                price_num = int(price_match.group(1))
                                all_prices.append(price_num)
                                price_sources.append('bing')
                    elif isinstance(bing_data, dict) and 'prices' in bing_data:
                        for price_num in bing_data['prices']:
                            if isinstance(price_num, (int, float)):
                                all_prices.append(int(price_num))
                                price_sources.append('bing')
                except:
                    pass
            
            # 3. 检查现有预测价格（保留受保护的数据）
            if predict_prices:
                try:
                    predict_data = json.loads(predict_prices)
                    if isinstance(predict_data, dict):
                        # 如果是受保护的数据，保留原始价格
                        if predict_data.get('protected', False):
                            protected_prices = predict_data.get('prices', [])
                            for price in protected_prices:
                                if isinstance(price, (int, float)):
                                    all_prices.append(price)
                                    price_sources.append('protected')
                            protected_count += 1
                            print(f"🛡️ 场馆 {court_id} ({court_name}) - 保留受保护数据")
                        else:
                            # 非受保护数据，重新计算
                            existing_prices = predict_data.get('prices', [])
                            for price in existing_prices:
                                if isinstance(price, (int, float)):
                                    all_prices.append(price)
                                    price_sources.append('existing')
                except:
                    pass
            
            if not all_prices:
                print(f"⚠️ 场馆 {court_id} ({court_name}) 无价格数据，跳过")
                skipped_count += 1
                continue
            
            # 按价格区间过滤（室内60~600元，室外50~300元）
            filtered_prices = []
            filtered_sources = []
            
            for i, price in enumerate(all_prices):
                if court_type == '室内' or court_type == '气膜':
                    if 60 <= price <= 600:
                        filtered_prices.append(price)
                        filtered_sources.append(price_sources[i])
                elif court_type == '室外':
                    if 50 <= price <= 300:
                        filtered_prices.append(price)
                        filtered_sources.append(price_sources[i])
                else:
                    # 未知类型，使用室内标准
                    if 60 <= price <= 600:
                        filtered_prices.append(price)
                        filtered_sources.append(price_sources[i])
            
            if not filtered_prices:
                print(f"⚠️ 场馆 {court_id} ({court_name}) 价格超出区间，跳过")
                skipped_count += 1
                continue
            
            # 计算平均价格
            avg_price = sum(filtered_prices) / len(filtered_prices)
            
            # 统计各来源的价格数量
            source_counts = {}
            for source in filtered_sources:
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # 确定主要来源
            if 'protected' in source_counts:
                main_source = 'PROTECTED_BING'
            elif 'real' in source_counts:
                main_source = 'REAL'
            elif 'bing' in source_counts:
                main_source = 'BING'
            else:
                main_source = 'EXISTING'
            
            # 创建新的预测价格数据
            new_predict_data = {
                "prices": filtered_prices,
                "avg_price": round(avg_price, 2),
                "count": len(filtered_prices),
                "source": main_source,
                "recalculated_at": datetime.now().isoformat(),
                "court_type": court_type,
                "area": area,
                "source_breakdown": source_counts,
                "protected": 'protected' in source_counts
            }
            
            # 如果有受保护的数据，保留原始信息
            if predict_prices:
                try:
                    old_predict_data = json.loads(predict_prices)
                    if isinstance(old_predict_data, dict) and old_predict_data.get('protected', False):
                        new_predict_data["original_bing_data"] = old_predict_data.get('original_bing_data')
                        new_predict_data["restore_version"] = old_predict_data.get('restore_version')
                        new_predict_data["restored_at"] = old_predict_data.get('restored_at')
                except:
                    pass
            
            # 更新predict_prices字段
            cursor.execute("""
                UPDATE court_details 
                SET predict_prices = ?, updated_at = ?
                WHERE court_id = ?
            """, (
                json.dumps(new_predict_data, ensure_ascii=False),
                datetime.now(),
                court_id
            ))
            
            processed_count += 1
            print(f"✅ 场馆 {court_id} ({court_name}) 重新计算成功，平均价格: {avg_price:.2f}，来源: {main_source}")
            
        except Exception as e:
            print(f"❌ 处理场馆 {court_id} ({court_name}) 时出错: {e}")
            skipped_count += 1
            continue
    
    # 4. 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n✅ 预测价格重新计算完成！")
    print(f"📊 统计结果:")
    print(f"   处理成功: {processed_count} 个场馆")
    print(f"   跳过: {skipped_count} 个场馆")
    print(f"   保留受保护数据: {protected_count} 个场馆")
    print(f"   总计: {len(results)} 个场馆")
    
    # 5. 验证结果
    print("\n🔍 第五步：验证重新计算结果...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE predict_prices IS NOT NULL AND predict_prices != ''")
    total_with_predict = cursor.fetchone()[0]
    conn.close()
    
    print(f"数据库中有预测价格的场馆数: {total_with_predict}")
    
    print(f"\n✅ 所有场馆预测价格重新计算完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 