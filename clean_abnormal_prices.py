#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理动之光·大望路网球馆的异常低价格，按照置信度算法规则进行区间过滤
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
import re

def extract_price_value(price_str):
    """从价格字符串中提取数值"""
    if not price_str:
        return None
    try:
        matches = re.findall(r'(\d+)', price_str)
        if matches:
            return int(matches[0])
    except:
        pass
    return None

def clean_abnormal_prices():
    """清理动之光·大望路网球馆的异常低价格"""
    print("🧹 清理动之光·大望路网球馆的异常低价格...")
    
    db = next(get_db())
    
    # 查找动之光·大望路网球馆
    court = db.query(TennisCourt).filter(TennisCourt.name.like('%动之光%大望路%')).first()
    
    if not court:
        print("❌ 未找到动之光·大望路网球馆")
        return
    
    print(f"🏟️ 场馆: {court.name} (ID: {court.id}, 类型: {court.court_type})")
    
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
    if not detail:
        print("❌ 未找到详情数据")
        return
    
    # 检查并清理merged_prices
    if detail.merged_prices:
        try:
            merged_data = json.loads(detail.merged_prices)
            if isinstance(merged_data, list):
                print(f"\n📊 当前merged_prices: {len(merged_data)}个价格")
                
                # 过滤异常价格
                filtered_prices = []
                for price_item in merged_data:
                    if not isinstance(price_item, dict):
                        continue
                    
                    price_str = price_item.get('price', '')
                    price_value = extract_price_value(price_str)
                    
                    if price_value is None:
                        print(f"  ⚠️ 无法解析价格: {price_str}")
                        continue
                    
                    # 根据场馆类型进行区间过滤
                    if court.court_type == '室内':
                        if 60 <= price_value <= 600:
                            filtered_prices.append(price_item)
                            print(f"  ✅ 保留价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤价格: {price_str} ({price_value}元) - 超出室内范围(60-600)")
                    elif court.court_type == '室外':
                        if 50 <= price_value <= 300:
                            filtered_prices.append(price_item)
                            print(f"  ✅ 保留价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤价格: {price_str} ({price_value}元) - 超出室外范围(50-300)")
                    else:
                        # 未知类型，使用室内标准
                        if 60 <= price_value <= 600:
                            filtered_prices.append(price_item)
                            print(f"  ✅ 保留价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤价格: {price_str} ({price_value}元) - 超出默认范围(60-600)")
                
                # 更新merged_prices
                if len(filtered_prices) != len(merged_data):
                    detail.merged_prices = json.dumps(filtered_prices, ensure_ascii=False)
                    db.commit()
                    print(f"\n✅ 清理完成: {len(merged_data)} -> {len(filtered_prices)} 个价格")
                else:
                    print(f"\n✅ 无需清理: 所有价格都在合理范围内")
                    
        except Exception as e:
            print(f"❌ 处理merged_prices失败: {e}")
    
    # 检查并清理bing_prices
    if detail.bing_prices:
        try:
            bing_data = json.loads(detail.bing_prices)
            if isinstance(bing_data, list):
                print(f"\n📊 当前bing_prices: {len(bing_data)}个价格")
                
                # 过滤异常价格
                filtered_bing_prices = []
                for price_item in bing_data:
                    if not isinstance(price_item, dict):
                        continue
                    
                    price_str = price_item.get('price', '')
                    price_value = extract_price_value(price_str)
                    
                    if price_value is None:
                        print(f"  ⚠️ 无法解析价格: {price_str}")
                        continue
                    
                    # 根据场馆类型进行区间过滤
                    if court.court_type == '室内':
                        if 60 <= price_value <= 600:
                            filtered_bing_prices.append(price_item)
                            print(f"  ✅ 保留BING价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤BING价格: {price_str} ({price_value}元) - 超出室内范围(60-600)")
                    elif court.court_type == '室外':
                        if 50 <= price_value <= 300:
                            filtered_bing_prices.append(price_item)
                            print(f"  ✅ 保留BING价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤BING价格: {price_str} ({price_value}元) - 超出室外范围(50-300)")
                    else:
                        # 未知类型，使用室内标准
                        if 60 <= price_value <= 600:
                            filtered_bing_prices.append(price_item)
                            print(f"  ✅ 保留BING价格: {price_str} ({price_value}元)")
                        else:
                            print(f"  ❌ 过滤BING价格: {price_str} ({price_value}元) - 超出默认范围(60-600)")
                
                # 更新bing_prices
                if len(filtered_bing_prices) != len(bing_data):
                    detail.bing_prices = json.dumps(filtered_bing_prices, ensure_ascii=False)
                    db.commit()
                    print(f"\n✅ BING价格清理完成: {len(bing_data)} -> {len(filtered_bing_prices)} 个价格")
                else:
                    print(f"\n✅ BING价格无需清理: 所有价格都在合理范围内")
                    
        except Exception as e:
            print(f"❌ 处理bing_prices失败: {e}")
    
    print(f"\n🎯 清理完成！")
    print(f"   - 场馆类型: {court.court_type}")
    print(f"   - 价格区间: {'60-600元' if court.court_type == '室内' else '50-300元' if court.court_type == '室外' else '60-600元(默认)'}")

if __name__ == '__main__':
    clean_abnormal_prices() 