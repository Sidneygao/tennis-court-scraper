#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量触发所有场馆的自动预测价格功能
"""
import requests
import time
import json

def batch_auto_predict():
    print("🔄 批量触发所有场馆的自动预测价格功能...")
    
    base_url = "http://localhost:8000"
    
    # 1. 获取所有场馆列表
    try:
        response = requests.get(f"{base_url}/api/courts/?limit=1000")
        if response.status_code != 200:
            print(f"❌ 获取场馆列表失败: {response.status_code}")
            return
        
        courts = response.json()
        print(f"📊 找到 {len(courts)} 个场馆")
        
    except Exception as e:
        print(f"❌ 获取场馆列表失败: {e}")
        return
    
    # 2. 批量触发自动预测
    success_count = 0
    failed_count = 0
    
    for i, court in enumerate(courts, 1):
        court_id = court['id']
        court_name = court['name']
        
        print(f"\n[{i}/{len(courts)}] 处理场馆: {court_name} (ID: {court_id})")
        
        try:
            # 触发强制更新（自动预测）
            response = requests.get(f"{base_url}/api/details/{court_id}?force_update=true")
            
            if response.status_code == 200:
                detail = response.json()
                predict_prices = detail.get('predict_prices', {})
                
                if predict_prices and isinstance(predict_prices, dict):
                    peak_price = predict_prices.get('peak_price')
                    off_peak_price = predict_prices.get('off_peak_price')
                    print(f"  ✅ 预测成功: 黄金{peak_price}元, 非黄金{off_peak_price}元")
                    success_count += 1
                else:
                    print(f"  ⚠️ 无预测价格")
                    failed_count += 1
            else:
                print(f"  ❌ 更新失败: {response.status_code}")
                failed_count += 1
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            failed_count += 1
        
        # 避免请求过于频繁
        time.sleep(0.1)
    
    print(f"\n📊 批量预测完成:")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {failed_count} 个")
    print(f"  总计: {len(courts)} 个")

if __name__ == "__main__":
    batch_auto_predict() 