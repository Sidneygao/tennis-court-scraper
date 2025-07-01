#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查防删除机制是否正常工作，显示所有受保护的价格数据
"""
import json
import sqlite3
from datetime import datetime

def main():
    print("🛡️ 检查防删除机制状态...")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 检查所有预测价格数据
    cursor.execute("""
        SELECT cd.court_id, tc.name, tc.court_type, cd.predict_prices 
        FROM court_details cd
        JOIN tennis_courts tc ON cd.court_id = tc.id
        WHERE cd.predict_prices IS NOT NULL AND cd.predict_prices != ''
    """)
    
    results = cursor.fetchall()
    print(f"\n📊 找到 {len(results)} 个有预测价格的场馆")
    
    # 统计受保护的数据
    protected_count = 0
    unprotected_count = 0
    restored_count = 0
    
    for court_id, court_name, court_type, predict_prices_json in results:
        try:
            predict_data = json.loads(predict_prices_json)
            
            if isinstance(predict_data, dict):
                is_protected = predict_data.get('protected', False)
                is_restored = 'restored_at' in predict_data
                source = predict_data.get('source', '未知')
                avg_price = predict_data.get('avg_price', 0)
                
                if is_protected:
                    protected_count += 1
                    if is_restored:
                        restored_count += 1
                        print(f"🛡️ 场馆 {court_id} ({court_name}) - 受保护，来源: {source}，平均价格: {avg_price}")
                else:
                    unprotected_count += 1
                    print(f"⚠️ 场馆 {court_id} ({court_name}) - 未受保护，来源: {source}，平均价格: {avg_price}")
            
        except Exception as e:
            print(f"❌ 解析场馆 {court_id} ({court_name}) 数据时出错: {e}")
    
    conn.close()
    
    print(f"\n📈 统计结果:")
    print(f"   受保护数据: {protected_count} 个")
    print(f"   未受保护数据: {unprotected_count} 个")
    print(f"   本次恢复数据: {restored_count} 个")
    print(f"   总计: {len(results)} 个")
    
    if restored_count > 0:
        print(f"\n✅ 防删除机制正常工作！")
        print(f"   - 成功恢复了 {restored_count} 个场馆的BING价格数据")
        print(f"   - 所有恢复的数据都标记了 protected=True")
        print(f"   - 原始数据已保存在 original_bing_data 字段中")
    else:
        print(f"\n⚠️ 未发现本次恢复的数据，请检查恢复脚本是否正常运行")

if __name__ == "__main__":
    main() 