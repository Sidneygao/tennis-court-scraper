#!/usr/bin/env python3
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

db = next(get_db())

# 查找动之光·大望路网球馆
court = db.query(TennisCourt).filter(TennisCourt.name.like('%动之光%大望路%')).first()

if court:
    print(f'ID: {court.id}')
    print(f'Name: {court.name}')
    print(f'Court Type: {court.court_type}')
    
    # 查找对应的详情数据
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
    
    if detail:
        print(f'\n=== 价格字段内容 ===')
        print(f'Prices: {detail.prices}')
        print(f'Merged_prices: {detail.merged_prices}')
        print(f'Bing_prices: {detail.bing_prices}')
        
        # 解析各个价格字段
        if detail.prices:
            print('\n=== Prices字段解析 ===')
            try:
                prices_data = json.loads(detail.prices) if isinstance(detail.prices, str) else detail.prices
                print(json.dumps(prices_data, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f'Prices字段解析失败: {e}')
        
        if detail.merged_prices:
            print('\n=== Merged_prices字段解析 ===')
            try:
                merged_data = json.loads(detail.merged_prices) if isinstance(detail.merged_prices, str) else detail.merged_prices
                print(json.dumps(merged_data, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f'Merged_prices字段解析失败: {e}')
        
        if detail.bing_prices:
            print('\n=== Bing_prices字段解析 ===')
            try:
                bing_data = json.loads(detail.bing_prices) if isinstance(detail.bing_prices, str) else detail.bing_prices
                print(json.dumps(bing_data, ensure_ascii=False, indent=2))
                
                # 检查BING价格是否符合区间过滤规则
                print('\n=== BING价格区间检查 ===')
                if isinstance(bing_data, list):
                    for i, price_info in enumerate(bing_data):
                        price_str = price_info.get('price', '')
                        # 提取价格数字
                        import re
                        price_match = re.search(r'¥?(\d+)', price_str)
                        if price_match:
                            price_value = int(price_match.group(1))
                            print(f'价格{i+1}: {price_str} -> {price_value}元')
                            if price_value < 60:
                                print(f'  ❌ 低于室内价格下限60元')
                            elif price_value > 600:
                                print(f'  ❌ 高于室内价格上限600元')
                            else:
                                print(f'  ✅ 在合理区间内')
                        else:
                            print(f'价格{i+1}: {price_str} -> 无法解析价格')
                
            except Exception as e:
                print(f'Bing_prices字段解析失败: {e}')
    else:
        print('未找到对应的详情数据')
else:
    print('未找到动之光·大望路网球馆') 