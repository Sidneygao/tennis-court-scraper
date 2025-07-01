#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格置信度模型
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.price_confidence_model import confidence_model

def main():
    print("🧪 测试价格置信度模型...")
    
    # 1. 构建模型
    print("\n🔄 构建正态分布模型...")
    confidence_model.build_normal_distribution_models()
    
    # 2. 显示模型信息
    print("\n📊 模型信息:")
    model_info = confidence_model.get_model_info()
    for model_name, model_data in model_info.items():
        if model_data:
            print(f"  {model_name}:")
            print(f"    均值: {model_data['mean']:.1f}")
            print(f"    标准差: {model_data['std']:.1f}")
            print(f"    样本数: {model_data['count']}")
            print(f"    范围: {model_data['min']:.1f} - {model_data['max']:.1f}")
        else:
            print(f"  {model_name}: 无数据")
    
    # 3. 测试置信度计算
    print("\n🧮 测试置信度计算:")
    
    test_cases = [
        # (价格, 场馆类型, 场馆名称, 价格类型, 描述)
        (100, "室内", "测试室内网球馆", "标准价格", "室内标准价格"),
        (200, "室外", "测试室外网球场", "标准价格", "室外标准价格"),
        (50, "室内", "测试室内网球馆", "会员价格", "室内会员价格"),
        (30, "室外", "测试室外网球场", "学生价格", "室外学生价格"),
        (500, "室内", "测试室内网球馆", "标准价格", "室内高价"),
        (300, "室外", "测试室外网球场", "标准价格", "室外高价"),
        (25, "室外", "测试室外网球场", "标准价格", "室外低价"),
        (40, "室内", "测试室内网球馆", "标准价格", "室内低价"),
    ]
    
    for price, court_type, court_name, price_type, description in test_cases:
        confidence = confidence_model.calculate_confidence(price, court_type, court_name, price_type)
        print(f"  {description}: ¥{price} -> 置信度: {confidence:.3f}")
    
    # 4. 测试价格提取
    print("\n🔍 测试价格提取:")
    test_text = "网球价格100元/小时，会员价格80元/小时，学生价格50元/小时"
    prices = confidence_model.extract_price_value("100元/小时")
    print(f"  提取价格: {prices}")
    
    print("\n✅ 置信度模型测试完成!")

if __name__ == "__main__":
    main() 