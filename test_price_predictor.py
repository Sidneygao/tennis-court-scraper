#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试价格预测模型
验证场地类型检测和价格预测功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor, CourtType

def test_court_type_detection():
    """测试场地类型检测"""
    print("🧪 测试场地类型检测")
    print("=" * 60)
    
    predictor = PricePredictor()
    
    test_cases = [
        ("嘉里中心网球场", "室内"),
        ("金地网球中心", "气膜"),
        ("朝阳公园网球场", "室外"),
        ("国贸网球俱乐部", "室内"),
        ("望京气膜网球馆", "气膜"),
        ("奥林匹克公园网球场", "室外"),
        ("三里屯网球中心", "室内"),
        ("酒仙桥网球馆", "气膜")
    ]
    
    for venue_name, expected_type in test_cases:
        detected_type = predictor.detect_court_type(venue_name)
        status = "✅" if detected_type.value == expected_type else "❌"
        print(f"{status} {venue_name} -> {detected_type.value} (期望: {expected_type})")

def test_price_prediction():
    """测试价格预测"""
    print("\n🧪 测试价格预测")
    print("=" * 60)
    
    predictor = PricePredictor()
    
    # 模拟周边场馆数据
    mock_venues = [
        {
            'venue_name': '嘉里中心网球场',
            'prices': [
                {'price': '280元/小时'},
                {'price': '320元/小时'},
                {'price': '260元/小时'}
            ]
        },
        {
            'venue_name': '金地网球中心',
            'prices': [
                {'price': '160元/小时'},
                {'price': '180元/小时'},
                {'price': '140元/小时'}
            ]
        }
    ]
    
    test_venues = [
        "嘉里中心网球场",
        "金地网球中心", 
        "朝阳公园网球场",
        "国贸网球俱乐部",
        "望京气膜网球馆"
    ]
    
    for venue_name in test_venues:
        print(f"\n📋 测试场馆: {venue_name}")
        print("-" * 50)
        
        predicted = predictor.predict_price_range(venue_name, "", mock_venues)
        
        print(f"   场地类型: {predicted.court_type.value}")
        print(f"   预测最低: {predicted.predicted_min}元/小时")
        print(f"   预测中点: {predicted.predicted_mid}元/小时")
        print(f"   预测最高: {predicted.predicted_max}元/小时")
        print(f"   置信度: {predicted.confidence:.2f}")
        print(f"   参考价格数: {len(predicted.nearby_prices)}")

def test_price_labeling():
    """测试价格标签格式化"""
    print("\n🧪 测试价格标签格式化")
    print("=" * 60)
    
    predictor = PricePredictor()
    
    # 模拟实际价格
    actual_prices = [
        {
            "type": "黄金时间",
            "price": "200元/小时",
            "time_range": "18:00-22:00"
        },
        {
            "type": "非黄金时间",
            "price": "150元/小时", 
            "time_range": "09:00-18:00"
        },
        {
            "type": "会员价",
            "price": "120元/小时",
            "time_range": "全天"
        }
    ]
    
    # 模拟预测价格
    predicted_prices = type('PredictedPrice', (), {
        'predicted_min': 100,
        'predicted_max': 250,
        'predicted_mid': 175,
        'confidence': 0.8,
        'court_type': type('CourtType', (), {'value': '室内'})()
    })()
    
    formatted_prices = predictor.format_price_labels(actual_prices, predicted_prices)
    
    print("📋 格式化后的价格标签:")
    for price in formatted_prices:
        label = price.get('label', '')
        price_value = price.get('price', '')
        is_actual = price.get('is_actual', False)
        actual_text = "实际" if is_actual else "预测"
        print(f"   {actual_text}: {label} - {price_value}")

def test_location_factor():
    """测试地理位置因子计算"""
    print("\n🧪 测试地理位置因子计算")
    print("=" * 60)
    
    predictor = PricePredictor()
    
    test_venues = [
        ("国贸网球俱乐部", 1.3),
        ("CBD网球中心", 1.3),
        ("三里屯网球馆", 1.3),
        ("望京网球中心", 1.0),
        ("酒仙桥网球馆", 1.0),
        ("双井网球俱乐部", 1.0),
        ("通州网球中心", 0.9),
        ("昌平网球馆", 0.9)
    ]
    
    for venue_name, expected_factor in test_venues:
        factor = predictor.calculate_location_factor(venue_name)
        status = "✅" if abs(factor - expected_factor) < 0.1 else "❌"
        print(f"{status} {venue_name} -> {factor:.1f} (期望: {expected_factor})")

def test_comprehensive_prediction():
    """综合测试价格预测"""
    print("\n🧪 综合测试价格预测")
    print("=" * 60)
    
    predictor = PricePredictor()
    
    # 模拟真实场馆数据
    real_venues = [
        {
            'venue_name': '嘉里中心网球场',
            'prices': [{'price': '280元/小时'}, {'price': '320元/小时'}]
        },
        {
            'venue_name': '金地网球中心', 
            'prices': [{'price': '160元/小时'}, {'price': '180元/小时'}]
        },
        {
            'venue_name': '朝阳公园网球场',
            'prices': [{'price': '120元/小时'}, {'price': '140元/小时'}]
        }
    ]
    
    test_venue = "新网球中心"
    predicted = predictor.predict_price_range(test_venue, "新开业的网球中心", real_venues)
    
    print(f"📋 测试场馆: {test_venue}")
    print("-" * 50)
    print(f"   场地类型: {predicted.court_type.value}")
    print(f"   地理位置因子: {predictor.calculate_location_factor(test_venue):.2f}")
    print(f"   参考价格: {predicted.nearby_prices}")
    print(f"   预测价格范围: {predicted.predicted_min}-{predicted.predicted_max}元/小时")
    print(f"   预测中点: {predicted.predicted_mid}元/小时")
    print(f"   置信度: {predicted.confidence:.2f}")

if __name__ == "__main__":
    test_court_type_detection()
    test_price_prediction()
    test_price_labeling()
    test_location_factor()
    test_comprehensive_prediction()
    
    print(f"\n{'='*60}")
    print("✅ 价格预测模型测试完成!") 