#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端真实价格显示
"""
import requests
import json

def test_real_price_display():
    """测试前端真实价格显示"""
    base_url = "http://127.0.0.1:8000"
    
    print("测试前端真实价格显示:")
    print("=" * 60)
    
    # 测试几个有真实价格的场馆
    test_courts = [1, 26, 27]
    
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
                    print("✅ 有真实价格数据，前端应该显示'真实'标签")
                    print("真实价格内容:")
                    for i, price in enumerate(prices[:2]):
                        print(f"  {i+1}. {price.get('type', 'N/A')}: {price.get('price', 'N/A')}")
                    
                    # 模拟前端getRealPrices函数逻辑
                    valid_prices = [p for p in prices if p.get('price') and p.get('price') != '该数据不能获得']
                    if valid_prices:
                        print(f"✅ 有效真实价格数量: {len(valid_prices)}")
                        print("前端应该显示这些价格，并带有'真实'标签")
                    else:
                        print("❌ 没有有效的真实价格")
                else:
                    print("❌ 无真实价格数据")
                
                print("-" * 40)
                
        except Exception as e:
            print(f"测试场馆 {court_id} 失败: {e}")
    
    print("\n前端显示检查:")
    print("1. 如果API返回prices字段有数据，前端应该显示'真实'标签")
    print("2. 真实价格标签应该是绿色背景 (#28a745)")
    print("3. 预测价格标签应该是黄色背景 (#ffc107)")
    print("4. 请刷新浏览器页面查看效果")

if __name__ == "__main__":
    test_real_price_display() 