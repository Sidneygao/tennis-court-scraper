#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查前端真实价格显示问题
"""
import requests
import json

def check_frontend_prices():
    """检查前端价格显示"""
    base_url = "http://127.0.0.1:8000"
    
    # 检查几个有真实价格的场馆
    test_courts = [1, 26, 27, 28, 29, 30]
    
    print("检查前端价格显示问题:")
    print("=" * 60)
    
    for court_id in test_courts:
        try:
            # 获取场馆详情
            detail_url = f"{base_url}/api/details/{court_id}"
            detail_response = requests.get(detail_url, timeout=5)
            
            if detail_response.status_code == 200:
                detail = detail_response.json()
                
                print(f"\n场馆ID: {court_id}")
                print(f"名称: {detail.get('name', 'N/A')}")
                
                # 检查prices字段
                prices = detail.get('prices', [])
                print(f"prices字段数量: {len(prices)}")
                
                if prices:
                    print("真实价格内容:")
                    for i, price in enumerate(prices[:2]):  # 只显示前2条
                        print(f"  {i+1}. {price}")
                else:
                    print("❌ prices字段为空")
                
                # 检查predict_prices字段
                predict_prices = detail.get('predict_prices', {})
                if predict_prices:
                    print(f"预测价格: {predict_prices}")
                
                print("-" * 40)
                
        except Exception as e:
            print(f"检查场馆 {court_id} 失败: {e}")
    
    print("\n结论:")
    print("如果prices字段有数据但前端不显示'真实'标签，说明:")
    print("1. 前端getRealPrices函数可能有问题")
    print("2. 前端渲染逻辑可能有问题")
    print("3. 浏览器缓存问题")

if __name__ == "__main__":
    check_frontend_prices() 