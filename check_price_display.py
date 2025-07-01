#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查API接口返回的价格数据结构
"""
import requests
import json

def check_price_display():
    """检查价格显示问题"""
    print("🔍 检查API接口价格数据结构...")
    
    base_url = "http://127.0.0.1:8000"
    
    # 测试几个场馆的详情接口
    test_court_ids = [1, 5, 10, 15, 20]
    
    for court_id in test_court_ids:
        try:
            print(f"\n📊 检查场馆ID {court_id}:")
            response = requests.get(f"{base_url}/api/details/{court_id}")
            if response.status_code == 200:
                detail = response.json()
                
                print(f"  场馆名称: {detail.get('court_id', 'N/A')}")
                print(f"  融合价格 (merged_prices): {detail.get('merged_prices', [])}")
                print(f"  预测价格 (predict_prices): {detail.get('predict_prices', [])}")
                print(f"  点评价格 (dianping_prices): {detail.get('dianping_prices', [])}")
                print(f"  美团价格 (meituan_prices): {detail.get('meituan_prices', [])}")
                
                # 检查价格数据结构
                merged_prices = detail.get('merged_prices', [])
                predict_prices = detail.get('predict_prices', [])
                
                if merged_prices:
                    print(f"  融合价格数量: {len(merged_prices)}")
                    for i, price in enumerate(merged_prices[:2]):  # 只显示前2个
                        print(f"    价格{i+1}: {price}")
                
                if predict_prices:
                    print(f"  预测价格类型: {type(predict_prices)}")
                    if isinstance(predict_prices, dict):
                        print(f"    预测价格内容: {predict_prices}")
                    elif isinstance(predict_prices, list):
                        print(f"    预测价格数量: {len(predict_prices)}")
                        for i, price in enumerate(predict_prices[:2]):  # 只显示前2个
                            print(f"    价格{i+1}: {price}")
                
            else:
                print(f"  请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"  请求异常: {e}")
    
    # 检查前端价格解析逻辑
    print("\n🔍 检查前端价格解析逻辑:")
    print("  前端会按以下顺序显示价格:")
    print("  1. merged_prices (融合价格)")
    print("  2. dianping_prices (点评价格)")
    print("  3. meituan_prices (美团价格)")
    print("  4. predict_prices (预测价格) - 只有在没有真实价格时才显示")
    
    # 检查数据库中的价格数据
    print("\n🔍 检查数据库中的价格数据:")
    try:
        import sqlite3
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        
        # 检查几个场馆的价格数据
        for court_id in test_court_ids:
            cursor.execute("""
                SELECT cd.merged_prices, cd.predict_prices, cd.dianping_prices, cd.meituan_prices
                FROM court_details cd 
                WHERE cd.court_id = ?
            """, (court_id,))
            result = cursor.fetchone()
            
            if result:
                merged_prices, predict_prices, dianping_prices, meituan_prices = result
                print(f"\n  场馆ID {court_id}:")
                print(f"    数据库merged_prices: {merged_prices}")
                print(f"    数据库predict_prices: {predict_prices}")
                print(f"    数据库dianping_prices: {dianping_prices}")
                print(f"    数据库meituan_prices: {meituan_prices}")
                
                # 解析JSON
                try:
                    if merged_prices:
                        merged_data = json.loads(merged_prices)
                        print(f"    解析后merged_prices: {merged_data}")
                    if predict_prices:
                        predict_data = json.loads(predict_prices)
                        print(f"    解析后predict_prices: {predict_data}")
                except Exception as e:
                    print(f"    JSON解析失败: {e}")
            else:
                print(f"\n  场馆ID {court_id}: 无详情数据")
        
        conn.close()
        
    except Exception as e:
        print(f"  数据库检查失败: {e}")

if __name__ == "__main__":
    check_price_display() 