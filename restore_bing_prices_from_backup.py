#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从BING价格备份文件中恢复价格数据到数据库
"""
import json
import sqlite3
import sys
import os
from datetime import datetime
import re

def main():
    print("🔄 开始从BING价格备份文件恢复价格数据...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 选择最新的备份文件
    backup_files = [
        'bing_price_results_enhanced_20250629_175521.json',
        'bing_price_results_enhanced_20250629_133403.json', 
        'bing_price_results_enhanced_20250629_133224.json',
        'bing_price_results_20250628_232507.json',
        'bing_price_results_20250628_232247.json'
    ]
    
    selected_file = None
    for file in backup_files:
        if os.path.exists(file):
            selected_file = file
            break
    
    if not selected_file:
        print("❌ 未找到可用的BING价格备份文件")
        return
    
    print(f"📖 使用备份文件: {selected_file}")
    
    # 1. 读取备份文件
    print("\n📖 第一步：读取备份文件...")
    with open(selected_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    # 2. 提取价格数据
    print("\n🔧 第二步：提取价格数据...")
    price_data = {}
    
    if 'results' in backup_data:
        for result in backup_data['results']:
            court_id = result.get('court_id')
            court_name = result.get('court_name')
            prices = result.get('prices', [])
            
            if court_id and prices:
                price_data[court_id] = {
                    'court_name': court_name,
                    'prices': prices
                }
    
    print(f"提取到 {len(price_data)} 个场馆的价格数据")
    
    # 3. 连接数据库
    print("\n🗄️ 第三步：连接数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 4. 恢复价格数据
    print("\n🔄 第四步：恢复价格数据...")
    restored_count = 0
    
    for court_id, data in price_data.items():
        try:
            # 检查场馆是否存在
            cursor.execute("SELECT id FROM tennis_courts WHERE id = ?", (court_id,))
            if not cursor.fetchone():
                print(f"⚠️ 场馆ID {court_id} ({data['court_name']}) 不存在，跳过")
                continue
            
            # 提取价格数字
            price_numbers = []
            for price_info in data['prices']:
                price_str = price_info.get('price', '')
                # 提取数字
                price_match = re.search(r'¥(\d+)', price_str)
                if price_match:
                    price_num = int(price_match.group(1))
                    price_numbers.append(price_num)
            
            if price_numbers:
                # 计算平均价格
                avg_price = sum(price_numbers) / len(price_numbers)
                
                # 检查court_details表中是否已有记录
                cursor.execute("SELECT id FROM court_details WHERE court_id = ?", (court_id,))
                detail_record = cursor.fetchone()
                
                if detail_record:
                    # 更新现有记录
                    cursor.execute("""
                        UPDATE court_details 
                        SET bing_prices = ?, updated_at = ?
                        WHERE court_id = ?
                    """, (
                        json.dumps({
                            'prices': price_numbers,
                            'avg_price': round(avg_price, 2),
                            'count': len(price_numbers),
                            'source': 'BING',
                            'restored_from': selected_file,
                            'restored_at': datetime.now().isoformat()
                        }, ensure_ascii=False),
                        datetime.now(),
                        court_id
                    ))
                else:
                    # 创建新记录
                    cursor.execute("""
                        INSERT INTO court_details (court_id, bing_prices, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        court_id,
                        json.dumps({
                            'prices': price_numbers,
                            'avg_price': round(avg_price, 2),
                            'count': len(price_numbers),
                            'source': 'BING',
                            'restored_from': selected_file,
                            'restored_at': datetime.now().isoformat()
                        }, ensure_ascii=False),
                        datetime.now(),
                        datetime.now()
                    ))
                
                restored_count += 1
                print(f"✅ 恢复场馆 {court_id} ({data['court_name']}) 的价格数据，平均价格: {avg_price:.2f}")
            
        except Exception as e:
            print(f"❌ 处理场馆 {court_id} 时出错: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 成功恢复 {restored_count} 个场馆的BING价格数据")
    
    # 5. 验证结果
    print("\n🔍 第五步：验证恢复结果...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM court_details WHERE bing_prices IS NOT NULL AND bing_prices != ''")
    total_with_prices = cursor.fetchone()[0]
    conn.close()
    
    print(f"数据库中有BING价格的场馆数: {total_with_prices}")
    
    print(f"\n✅ BING价格数据恢复完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 