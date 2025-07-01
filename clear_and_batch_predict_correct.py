#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除现有预测价格并重新计算所有场馆的预测价格
基于新的置信度模型和增加的真实价格样本
"""
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict

# 添加项目路径
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.scrapers.price_confidence_model import confidence_model
from app.models import TennisCourt

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("重新计算所有场馆预测价格...")
    
    # 1. 初始化置信度模型和价格预测器
    print("初始化模型...")
    confidence_model.build_normal_distribution_models()
    predictor = PricePredictor()
    
    # 2. 清除现有预测价格
    print("清除现有预测价格...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE court_details SET predict_prices = NULL")
    cleared_count = cursor.rowcount
    conn.commit()
    print(f"已清除 {cleared_count} 个场馆的预测价格")
    
    # 3. 获取所有场馆
    print("获取所有场馆...")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, tc.latitude, tc.longitude, tc.address
        FROM tennis_courts tc
        ORDER BY tc.id
    """)
    
    all_courts_data = cursor.fetchall()
    print(f"总场馆数: {len(all_courts_data)}")
    
    # 4. 重新计算预测价格
    print("开始重新计算预测价格...")
    
    success_count = 0
    error_count = 0
    
    for i, (court_id, court_name, court_type, lat, lng, address) in enumerate(all_courts_data, 1):
        try:
            print(f"[{i}/{len(all_courts_data)}] 计算场馆: {court_name}")
            
            # 创建TennisCourt对象
            court = TennisCourt(
                id=court_id,
                name=court_name,
                court_type=court_type,
                latitude=lat,
                longitude=lng,
                address=address
            )
            
            # 预测价格
            prediction_result = predictor.predict_price_for_court(court)
            
            if prediction_result:
                # 保存预测结果
                cursor.execute("""
                    UPDATE court_details 
                    SET predict_prices = ? 
                    WHERE court_id = ?
                """, (json.dumps(prediction_result, ensure_ascii=False), court_id))
                
                # 显示预测结果
                peak_price = prediction_result.get('peak_price', 'N/A')
                off_peak_price = prediction_result.get('off_peak_price', 'N/A')
                confidence = prediction_result.get('confidence', 'N/A')
                method = prediction_result.get('method', 'N/A')
                
                print(f"  预测成功:")
                print(f"    黄金时段: {peak_price}元")
                print(f"    非黄金时段: {off_peak_price}元")
                print(f"    置信度: {confidence}")
                print(f"    方法: {method}")
                
                success_count += 1
            else:
                print(f"  预测失败: 无结果")
                error_count += 1
                
        except Exception as e:
            print(f"  预测失败: {str(e)}")
            error_count += 1
            continue
    
    # 5. 提交更改
    conn.commit()
    
    # 6. 统计结果
    print(f"重新计算完成!")
    print(f"  总场馆数: {len(all_courts_data)}")
    print(f"  成功数: {success_count}")
    print(f"  失败数: {error_count}")
    print(f"  成功率: {success_count/len(all_courts_data)*100:.1f}%")
    
    # 7. 验证结果
    print(f"验证预测价格分布...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL THEN 1 ELSE 0 END) as has_predict_prices,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL THEN 1 ELSE 0 END) as has_real_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    stats = cursor.fetchone()
    print(f"  总场馆数: {stats[0]}")
    print(f"  有预测价格: {stats[1]}")
    print(f"  有真实价格: {stats[2]}")
    
    conn.close()
    print(f"重新计算预测价格完成!")

if __name__ == "__main__":
    main() 