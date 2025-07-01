#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对现有BING缓存数据应用置信度模型
严格区分真实数据和预测数据
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

from app.scrapers.price_confidence_model import confidence_model

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🔄 对现有BING缓存数据应用置信度模型...")
    
    # 1. 初始化置信度模型
    print("\n📊 初始化置信度模型...")
    confidence_model.build_normal_distribution_models()
    model_info = confidence_model.get_model_info()
    
    print("✅ 置信度模型初始化完成:")
    for model_name, model_data in model_info.items():
        if model_data:
            print(f"  {model_name}: 均值={model_data['mean']:.1f}, 标准差={model_data['std']:.1f}, 样本数={model_data['count']}")
    
    # 2. 连接数据库
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 3. 获取所有有BING价格数据的场馆
    print("\n🔍 获取现有BING价格数据...")
    cursor.execute("""
        SELECT tc.id, tc.name, tc.court_type, cd.bing_prices, cd.merged_prices, cd.predict_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]'
    """)
    
    courts_with_bing = cursor.fetchall()
    print(f"找到 {len(courts_with_bing)} 个有BING价格数据的场馆")
    
    # 4. 统计数据类型
    total_bing_prices = 0
    total_merged_prices = 0
    total_predict_prices = 0
    
    # 5. 处理每个场馆的数据
    updated_count = 0
    confidence_stats = {
        'high_confidence': 0,    # 置信度 > 0.7
        'medium_confidence': 0,  # 置信度 0.4-0.7
        'low_confidence': 0,     # 置信度 < 0.4
        'total_prices': 0
    }
    
    print("\n📋 处理场馆数据:")
    for court_id, court_name, court_type, bing_prices, merged_prices, predict_prices in courts_with_bing:
        print(f"\n🎾 处理场馆: {court_name}")
        print(f"  场馆类型: {court_type or '未知'}")
        
        # 统计现有数据
        try:
            bing_data = json.loads(bing_prices) if bing_prices else []
            merged_data = json.loads(merged_prices) if merged_prices else []
            predict_data = json.loads(predict_prices) if predict_prices else []
            
            print(f"  BING价格: {len(bing_data)} 个")
            print(f"  真实价格: {len(merged_data)} 个")
            print(f"  预测价格: {len(predict_data)} 个")
            
            total_bing_prices += len(bing_data)
            total_merged_prices += len(merged_data)
            total_predict_prices += len(predict_data)
            
            # 对BING价格应用置信度模型
            updated_bing_prices = []
            for price_item in bing_data:
                if isinstance(price_item, dict):
                    price_str = price_item.get('price', '')
                    price_type = price_item.get('type', '标准价格')
                    
                    # 提取价格数值
                    price_value = confidence_model.extract_price_value(price_str)
                    if price_value is None:
                        continue
                    
                    # 计算置信度
                    confidence = confidence_model.calculate_confidence(
                        price_value, court_type or '', court_name, price_type
                    )
                    
                    # 更新价格项
                    updated_price_item = price_item.copy()
                    updated_price_item['confidence'] = confidence
                    updated_price_item['confidence_calculated_at'] = datetime.now().isoformat()
                    updated_bing_prices.append(updated_price_item)
                    
                    # 统计置信度分布
                    confidence_stats['total_prices'] += 1
                    if confidence > 0.7:
                        confidence_stats['high_confidence'] += 1
                    elif confidence > 0.4:
                        confidence_stats['medium_confidence'] += 1
                    else:
                        confidence_stats['low_confidence'] += 1
                    
                    print(f"    • {price_str} ({price_type}) -> 置信度: {confidence:.3f}")
            
            # 按置信度排序
            updated_bing_prices.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            # 更新数据库
            if updated_bing_prices:
                cursor.execute("""
                    UPDATE court_details 
                    SET bing_prices = ? 
                    WHERE court_id = ?
                """, (json.dumps(updated_bing_prices, ensure_ascii=False), court_id))
                updated_count += 1
                print(f"  ✅ 更新了 {len(updated_bing_prices)} 个价格数据")
            
        except Exception as e:
            logger.error(f"处理场馆 {court_name} 数据失败: {e}")
            print(f"  ❌ 处理失败: {e}")
            continue
    
    # 6. 提交更改
    conn.commit()
    conn.close()
    
    # 7. 输出统计结果
    print(f"\n📊 置信度模型应用完成!")
    print(f"  处理场馆数: {len(courts_with_bing)}")
    print(f"  更新场馆数: {updated_count}")
    print(f"  总价格数: {confidence_stats['total_prices']}")
    print(f"  高置信度 (>0.7): {confidence_stats['high_confidence']} ({confidence_stats['high_confidence']/max(1, confidence_stats['total_prices'])*100:.1f}%)")
    print(f"  中置信度 (0.4-0.7): {confidence_stats['medium_confidence']} ({confidence_stats['medium_confidence']/max(1, confidence_stats['total_prices'])*100:.1f}%)")
    print(f"  低置信度 (<0.4): {confidence_stats['low_confidence']} ({confidence_stats['low_confidence']/max(1, confidence_stats['total_prices'])*100:.1f}%)")
    
    print(f"\n📋 数据类型统计:")
    print(f"  BING价格数据: {total_bing_prices} 个")
    print(f"  真实价格数据: {total_merged_prices} 个")
    print(f"  预测价格数据: {total_predict_prices} 个")
    
    print(f"\n✅ 置信度模型应用完成，数据严格分离!")

if __name__ == "__main__":
    main() 