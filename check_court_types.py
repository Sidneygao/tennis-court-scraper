#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查场馆类型判断是否正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.scrapers.price_predictor import PricePredictor

def main():
    print("🔍 检查场馆类型判断...")
    
    predictor = PricePredictor()
    
    # 测试几个场馆的类型判断
    test_courts = [
        "茂华UHN国际村-网球场",
        "乾坤体育网球学练馆(望京SOHOT1商场店)", 
        "朝阳公园体育中心网球中心-网球场",
        "郡王府网球馆",
        "几木网球训练馆TennisGym"
    ]
    
    for court_name in test_courts:
        print(f"\n🏟️ 测试场馆: {court_name}")
        court_type = predictor.judge_court_type(court_name)
        print(f"   类型: {court_type}")

if __name__ == "__main__":
    main() 