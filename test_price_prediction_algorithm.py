#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格预测算法的数据源识别问题
根据新建立的规则：如果发现成功价格预测逻辑基础数据不足，不要急于放弃进入粗糙的通用模型，必须先检查算法
"""
import json
import sqlite3
from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt, CourtDetail

def test_algorithm_data_source_recognition():
    """测试算法数据源识别"""
    print("🔍 测试价格预测算法的数据源识别...")
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 获取数据库连接
    db = next(get_db())
    
    # 检查前10个场馆的数据源识别情况
    courts = db.query(TennisCourt).limit(10).all()
    
    for court in courts:
        print(f"\n🏟️ 场馆: {court.name} (ID: {court.id})")
        
        # 获取详情数据
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        if not detail:
            print("  ❌ 没有详情数据")
            continue
        
        # 检查各个价格字段
        print("  📊 价格字段检查:")
        
        # 检查BING价格
        if detail.bing_prices:
            try:
                bing_data = json.loads(detail.bing_prices)
                if isinstance(bing_data, list) and len(bing_data) > 0:
                    print(f"    ✅ BING价格: {len(bing_data)} 个")
                    # 测试算法是否能识别
                    real_prices = predictor._extract_real_prices(detail)
                    if real_prices:
                        print(f"    ✅ 算法识别成功: {real_prices}")
                    else:
                        print(f"    ❌ 算法识别失败")
                else:
                    print(f"    ❌ BING价格: 空数组")
            except Exception as e:
                print(f"    ❌ BING价格: 解析失败 - {e}")
        else:
            print(f"    ❌ BING价格: 无数据")
        
        # 检查合并价格
        if detail.merged_prices:
            try:
                merged_data = json.loads(detail.merged_prices)
                if isinstance(merged_data, list) and len(merged_data) > 0:
                    print(f"    ✅ 合并价格: {len(merged_data)} 个")
                else:
                    print(f"    ❌ 合并价格: 空数组")
            except Exception as e:
                print(f"    ❌ 合并价格: 解析失败 - {e}")
        else:
            print(f"    ❌ 合并价格: 无数据")
        
        # 检查预测价格
        if detail.predict_prices:
            try:
                predict_data = json.loads(detail.predict_prices)
                if predict_data:
                    print(f"    ✅ 预测价格: 已存在")
                else:
                    print(f"    ❌ 预测价格: 空数据")
            except Exception as e:
                print(f"    ❌ 预测价格: 解析失败 - {e}")
        else:
            print(f"    ❌ 预测价格: 无数据")

def test_nearby_courts_search():
    """测试附近场馆搜索"""
    print("\n🔍 测试附近场馆搜索...")
    
    predictor = PricePredictor()
    db = next(get_db())
    
    # 选择一个有BING价格的场馆进行测试
    test_court = db.query(TennisCourt).filter(TennisCourt.id == 1).first()
    
    if not test_court:
        print("❌ 找不到测试场馆")
        return
    
    print(f"🏟️ 测试场馆: {test_court.name}")
    print(f"📍 坐标: {test_court.latitude}, {test_court.longitude}")
    
    # 测试不同半径的搜索
    for radius in [2, 4, 8, 16]:
        nearby_courts = predictor.find_nearby_courts_with_prices(test_court, radius)
        print(f"  🔍 {radius}KM内: 找到 {len(nearby_courts)} 个有价格的场馆")
        
        if nearby_courts:
            for i, nearby in enumerate(nearby_courts[:3]):  # 只显示前3个
                court = nearby['court']
                distance = nearby['distance']
                prices = nearby['prices']
                print(f"    {i+1}. {court.name} ({distance:.1f}KM) - {prices}")

def test_price_extraction():
    """测试价格提取逻辑"""
    print("\n🔍 测试价格提取逻辑...")
    
    predictor = PricePredictor()
    db = next(get_db())
    
    # 测试几个有BING价格的场馆
    test_courts = db.query(TennisCourt).limit(5).all()
    
    for court in test_courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        if not detail or not detail.bing_prices:
            continue
        
        print(f"\n🏟️ 场馆: {court.name}")
        
        try:
            bing_data = json.loads(detail.bing_prices)
            if isinstance(bing_data, list) and len(bing_data) > 0:
                print(f"  📊 BING价格数据: {len(bing_data)} 个")
                
                # 测试价格解析
                parsed_prices = predictor._parse_price_data(bing_data)
                if parsed_prices:
                    print(f"  ✅ 解析结果: {parsed_prices}")
                else:
                    print(f"  ❌ 解析失败")
                
                # 测试完整提取
                real_prices = predictor._extract_real_prices(detail)
                if real_prices:
                    print(f"  ✅ 提取结果: {real_prices}")
                else:
                    print(f"  ❌ 提取失败")
                
                # 显示前几个价格数据
                print(f"  📋 前3个价格数据:")
                for i, price_item in enumerate(bing_data[:3]):
                    if isinstance(price_item, dict):
                        price_type = price_item.get('type', '')
                        price_str = price_item.get('price', '')
                        confidence = price_item.get('confidence', 0)
                        print(f"    {i+1}. 类型: {price_type}, 价格: {price_str}, 置信度: {confidence}")
        
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

def main():
    """主函数"""
    print("🚀 开始测试价格预测算法...")
    
    # 测试1: 数据源识别
    test_algorithm_data_source_recognition()
    
    # 测试2: 附近场馆搜索
    test_nearby_courts_search()
    
    # 测试3: 价格提取逻辑
    test_price_extraction()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main() 