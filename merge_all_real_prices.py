#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并所有真实价格到merged_prices，包括BING价格数据
"""
import sqlite3
import json

def extract_real_prices(prices_str, source_name):
    """提取真实价格项"""
    if not prices_str:
        return []
    try:
        items = json.loads(prices_str)
        if isinstance(items, list):
            real_prices = []
            for item in items:
                if isinstance(item, dict):
                    # BING价格数据没有is_predicted字段，直接当作真实价格
                    if source_name == 'bing':
                        real_prices.append({
                            'type': item.get('type', '标准价格'),
                            'price': item.get('price', ''),
                            'source': 'BING',
                            'is_predicted': False,
                            'confidence': item.get('confidence', 0.8)
                        })
                    # 其他来源的价格，只提取is_predicted=False的
                    elif not item.get('is_predicted', True):
                        real_prices.append(item)
            return real_prices
        return []
    except Exception as e:
        print(f"解析价格数据失败: {e}")
        return []

def main():
    print("🔄 合并所有真实价格到merged_prices...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, bing_prices, dianping_prices, meituan_prices FROM court_details")
    rows = cursor.fetchall()
    update_count = 0
    
    for row in rows:
        detail_id, bing, dianping, meituan = row
        merged = []
        
        # 合并BING价格数据
        if bing:
            bing_prices = extract_real_prices(bing, 'bing')
            merged.extend(bing_prices)
            print(f"场馆ID {detail_id}: 添加 {len(bing_prices)} 个BING价格")
        
        # 合并点评价格数据
        if dianping:
            dianping_prices = extract_real_prices(dianping, 'dianping')
            merged.extend(dianping_prices)
            print(f"场馆ID {detail_id}: 添加 {len(dianping_prices)} 个点评价格")
        
        # 合并美团价格数据
        if meituan:
            meituan_prices = extract_real_prices(meituan, 'meituan')
            merged.extend(meituan_prices)
            print(f"场馆ID {detail_id}: 添加 {len(meituan_prices)} 个美团价格")
        
        # 去重（按type+price+source）
        seen = set()
        unique = []
        for item in merged:
            key = (item.get('type'), item.get('price'), item.get('source'))
            if key not in seen:
                seen.add(key)
                unique.append(item)
        
        if unique:
            cursor.execute("UPDATE court_details SET merged_prices=? WHERE id=?", 
                         (json.dumps(unique, ensure_ascii=False), detail_id))
            update_count += 1
            print(f"场馆ID {detail_id}: 合并 {len(unique)} 个真实价格")
    
    conn.commit()
    print(f"✅ 合并完成，更新 {update_count} 条记录")
    conn.close()

if __name__ == "__main__":
    main() 