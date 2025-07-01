#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将数据库中所有BING价格数据转换为预测价格格式，并添加防删除机制
"""
import json
import sqlite3
import sys
import os
from datetime import datetime
import re

def main():
    print("🔄 开始恢复所有BING价格数据为预测价格...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 连接数据库
    print("\n🗄️ 第一步：连接数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 2. 获取所有有BING价格的场馆
    print("\n📖 第二步：获取所有有BING价格的场馆...")
    cursor.execute("""
        SELECT cd.court_id, tc.name, tc.court_type, cd.bing_prices 
        FROM court_details cd
        JOIN tennis_courts tc ON cd.court_id = tc.id
        WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]'
    """)
    
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个有BING价格的场馆")
    
    # 3. 处理每个场馆的BING价格
    print("\n🔄 第三步：处理BING价格数据...")
    processed_count = 0
    skipped_count = 0
    
    for court_id, court_name, court_type, bing_prices_json in results:
        try:
            # 解析BING价格数据
            bing_data = json.loads(bing_prices_json)
            
            # 提取价格数字
            price_numbers = []
            
            if isinstance(bing_data, list):
                # 如果是列表格式，直接处理
                for price_info in bing_data:
                    price_str = price_info.get('price', '')
                    price_match = re.search(r'¥(\d+)', price_str)
                    if price_match:
                        price_num = int(price_match.group(1))
                        price_numbers.append(price_num)
            elif isinstance(bing_data, dict):
                # 如果是字典格式，检查是否有prices字段
                if 'prices' in bing_data and isinstance(bing_data['prices'], list):
                    for price_num in bing_data['prices']:
                        if isinstance(price_num, (int, float)):
                            price_numbers.append(int(price_num))
            
            if not price_numbers:
                print(f"⚠️ 场馆 {court_id} ({court_name}) 无有效价格数字，跳过")
                skipped_count += 1
                continue
            
            # 按价格区间过滤（室内60~600元，室外50~300元）
            filtered_prices = []
            for price in price_numbers:
                if court_type == '室内' or court_type == '气膜':
                    if 60 <= price <= 600:
                        filtered_prices.append(price)
                elif court_type == '室外':
                    if 50 <= price <= 300:
                        filtered_prices.append(price)
                else:
                    # 未知类型，使用室内标准
                    if 60 <= price <= 600:
                        filtered_prices.append(price)
            
            if not filtered_prices:
                print(f"⚠️ 场馆 {court_id} ({court_name}) 价格超出区间，跳过")
                skipped_count += 1
                continue
            
            # 计算平均价格
            avg_price = sum(filtered_prices) / len(filtered_prices)
            
            # 创建预测价格数据（带防删除机制）
            predict_data = {
                "prices": filtered_prices,
                "avg_price": round(avg_price, 2),
                "count": len(filtered_prices),
                "source": "BING",
                "restored_at": datetime.now().isoformat(),
                "protected": True,  # 防删除标记
                "original_bing_data": bing_data,  # 保留原始数据
                "court_type": court_type,
                "restore_version": "1.0"
            }
            
            # 更新predict_prices字段
            cursor.execute("""
                UPDATE court_details 
                SET predict_prices = ?, updated_at = ?
                WHERE court_id = ?
            """, (
                json.dumps(predict_data, ensure_ascii=False),
                datetime.now(),
                court_id
            ))
            
            processed_count += 1
            print(f"✅ 场馆 {court_id} ({court_name}) 转换成功，平均价格: {avg_price:.2f}")
            
        except Exception as e:
            print(f"❌ 处理场馆 {court_id} ({court_name}) 时出错: {e}")
            skipped_count += 1
            continue
    
    # 4. 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n✅ BING价格数据恢复完成！")
    print(f"📊 统计结果:")
    print(f"   处理成功: {processed_count} 个场馆")
    print(f"   跳过: {skipped_count} 个场馆")
    print(f"   总计: {len(results)} 个场馆")
    
    # 5. 验证结果
    print("\n🔍 第五步：验证恢复结果...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE predict_prices IS NOT NULL AND predict_prices != ''")
    total_with_predict = cursor.fetchone()[0]
    conn.close()
    
    print(f"数据库中有预测价格的场馆数: {total_with_predict}")
    
    print(f"\n✅ 所有BING价格数据恢复完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 6. 创建防删除机制说明
    print(f"\n🛡️ 防删除机制已启用:")
    print(f"   - 所有恢复的数据都标记了 protected=True")
    print(f"   - 原始BING数据已保存在 original_bing_data 字段中")
    print(f"   - 恢复版本信息已记录")
    print(f"   - 建议在删除前检查 protected 标记")

if __name__ == "__main__":
    main() 