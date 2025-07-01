#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从real_courts_price_stats.json备份文件恢复真实价格数据
"""
import json
import sqlite3
import sys
import os
from datetime import datetime

def main():
    print("🔄 开始从备份文件恢复真实价格数据...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 读取备份文件
    print("\n📖 第一步：读取备份文件...")
    backup_file = 'real_courts_price_stats.json'
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件 {backup_file} 不存在")
        return
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        print(f"✅ 成功读取备份文件，包含 {len(backup_data.get('courts', []))} 个场馆数据")
    except Exception as e:
        print(f"❌ 读取备份文件失败: {e}")
        return
    
    # 2. 连接数据库
    print("\n🗄️ 第二步：连接数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 3. 恢复真实价格数据
    print("\n💾 第三步：恢复真实价格数据...")
    restored_count = 0
    skipped_count = 0
    
    for court_data in backup_data.get('courts', []):
        court_id = court_data.get('court_id')
        court_name = court_data.get('name')
        merged_prices = court_data.get('merged_prices', [])
        
        if not court_id or not merged_prices:
            print(f"⚠️  跳过无效数据: {court_name}")
            skipped_count += 1
            continue
        
        # 检查场馆是否存在
        cursor.execute("SELECT id FROM tennis_courts WHERE id = ?", (court_id,))
        if not cursor.fetchone():
            print(f"⚠️  场馆不存在: {court_name} (ID: {court_id})")
            skipped_count += 1
            continue
        
        # 转换价格数据格式
        real_prices = []
        for price_info in merged_prices:
            price_str = price_info.get('price', '')
            # 提取数字价格
            import re
            price_match = re.search(r'(\d+)', price_str)
            if price_match:
                price = int(price_match.group(1))
                real_prices.append({
                    'type': price_info.get('type', '标准价格'),
                    'price': price,
                    'time_range': price_info.get('time_range', ''),
                    'source': 'backup_restore',
                    'restored_at': datetime.now().isoformat()
                })
        
        if not real_prices:
            print(f"⚠️  无有效价格数据: {court_name}")
            skipped_count += 1
            continue
        
        # 更新数据库
        try:
            # 检查是否已有court_details记录
            cursor.execute("SELECT court_id FROM court_details WHERE court_id = ?", (court_id,))
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute("""
                    UPDATE court_details 
                    SET prices = ? 
                    WHERE court_id = ?
                """, (json.dumps(real_prices), court_id))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO court_details (court_id, prices) 
                    VALUES (?, ?)
                """, (court_id, json.dumps(real_prices)))
            
            print(f"✅ 恢复成功: {court_name} (ID: {court_id}) - {len(real_prices)} 个价格")
            restored_count += 1
            
        except Exception as e:
            print(f"❌ 恢复失败: {court_name} (ID: {court_id}) - {e}")
            skipped_count += 1
    
    # 4. 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n📊 恢复结果总结:")
    print(f"   成功恢复: {restored_count} 个场馆")
    print(f"   跳过: {skipped_count} 个场馆")
    print(f"   总计处理: {len(backup_data.get('courts', []))} 个场馆")
    
    print(f"\n✅ 真实价格数据恢复完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 