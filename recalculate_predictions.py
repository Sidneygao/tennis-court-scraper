#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新计算所有预测价格，排除游泳池场馆
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.database import SessionLocal

def main():
    print("🔄 开始重新计算所有预测价格...")
    
    # 创建预测器
    predictor = PricePredictor()
    
    # 批量预测
    result = predictor.batch_predict_prices(max_workers=1, limit=None)
    
    print(f"\n📊 预测结果统计:")
    print(f"  总场馆数: {result['total_courts']}")
    print(f"  成功预测: {result['success_count']}")
    print(f"  预测失败: {result['failed_count']}")
    print(f"  耗时: {result['duration_seconds']:.2f}秒")
    
    print("\n✅ 预测价格重新计算完成！")
    print("💡 已排除包含'游泳池'的非网球场馆")

if __name__ == "__main__":
    main() 