#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新建立正态分布模型并重新分配置信度
"""

import sys
import os
import json
import logging
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_confidence_model import PriceConfidenceModel

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def rebuild_confidence_models():
    """重新建立正态分布模型"""
    logger.info("🔄 开始重新建立正态分布模型...")
    
    # 初始化置信度模型
    confidence_model = PriceConfidenceModel()
    
    # 建立正态分布模型
    confidence_model.build_normal_distribution_models()
    
    # 获取模型信息
    model_info = confidence_model.get_model_info()
    
    logger.info("📊 正态分布模型信息:")
    for model_name, model_data in model_info.items():
        if model_data:
            logger.info(f"  {model_name}: 均值={model_data['mean']:.1f}, 标准差={model_data['std']:.1f}, 样本数={model_data['count']}")
        else:
            logger.info(f"  {model_name}: 样本不足，无法建立模型")
    
    return confidence_model

def recalculate_all_confidence_scores(confidence_model):
    """重新计算所有价格的置信度"""
    logger.info("🔄 开始重新计算所有价格的置信度...")
    
    db = SessionLocal()
    
    try:
        # 获取所有有价格数据的场馆
        courts = db.query(TennisCourt).all()
        
        total_updated = 0
        total_prices = 0
        
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                continue
            
            updated = False
            
            # 重新计算BING价格置信度
            if detail.bing_prices:
                try:
                    bing_data = json.loads(detail.bing_prices)
                    if isinstance(bing_data, list):
                        for price_item in bing_data:
                            if isinstance(price_item, dict):
                                price_str = price_item.get('price', '')
                                price_type = price_item.get('type', '标准价格')
                                
                                # 提取价格数值
                                price_value = confidence_model.extract_price_value(price_str)
                                if price_value is not None:
                                    # 重新计算置信度
                                    new_confidence = confidence_model.calculate_confidence(
                                        price_value, court.court_type, court.name, price_type
                                    )
                                    
                                    # 更新置信度
                                    price_item['confidence'] = new_confidence
                                    total_prices += 1
                                    updated = True
                    
                    if updated:
                        detail.bing_prices = json.dumps(bing_data, ensure_ascii=False)
                        total_updated += 1
                        
                except Exception as e:
                    logger.warning(f"处理场馆 {court.name} 的BING价格失败: {e}")
            
            # 重新计算融合价格置信度
            if detail.merged_prices:
                try:
                    merged_data = json.loads(detail.merged_prices)
                    if isinstance(merged_data, list):
                        for price_item in merged_data:
                            if isinstance(price_item, dict):
                                price_str = price_item.get('price', '')
                                price_type = price_item.get('type', '标准价格')
                                
                                # 提取价格数值
                                price_value = confidence_model.extract_price_value(price_str)
                                if price_value is not None:
                                    # 重新计算置信度
                                    new_confidence = confidence_model.calculate_confidence(
                                        price_value, court.court_type, court.name, price_type
                                    )
                                    
                                    # 更新置信度
                                    price_item['confidence'] = new_confidence
                                    total_prices += 1
                                    updated = True
                    
                    if updated:
                        detail.merged_prices = json.dumps(merged_data, ensure_ascii=False)
                        total_updated += 1
                        
                except Exception as e:
                    logger.warning(f"处理场馆 {court.name} 的融合价格失败: {e}")
            
            # 更新详情记录
            if updated:
                detail.updated_at = datetime.now()
        
        # 提交所有更改
        db.commit()
        
        logger.info(f"✅ 置信度重新计算完成:")
        logger.info(f"  更新场馆数: {total_updated}")
        logger.info(f"  更新价格数: {total_prices}")
        
        return total_updated, total_prices
        
    except Exception as e:
        logger.error(f"重新计算置信度失败: {e}")
        db.rollback()
        return 0, 0
    finally:
        db.close()

def analyze_confidence_distribution():
    """分析置信度分布"""
    logger.info("📊 分析置信度分布...")
    
    db = SessionLocal()
    
    try:
        confidence_ranges = {
            '0.0-0.1': 0,
            '0.1-0.3': 0,
            '0.3-0.5': 0,
            '0.5-0.7': 0,
            '0.7-0.9': 0,
            '0.9-1.0': 0
        }
        
        total_prices = 0
        
        courts = db.query(TennisCourt).all()
        
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if not detail:
                continue
            
            # 分析BING价格置信度
            if detail.bing_prices:
                try:
                    bing_data = json.loads(detail.bing_prices)
                    if isinstance(bing_data, list):
                        for price_item in bing_data:
                            if isinstance(price_item, dict):
                                confidence = price_item.get('confidence', 0)
                                total_prices += 1
                                
                                if confidence <= 0.1:
                                    confidence_ranges['0.0-0.1'] += 1
                                elif confidence <= 0.3:
                                    confidence_ranges['0.1-0.3'] += 1
                                elif confidence <= 0.5:
                                    confidence_ranges['0.3-0.5'] += 1
                                elif confidence <= 0.7:
                                    confidence_ranges['0.5-0.7'] += 1
                                elif confidence <= 0.9:
                                    confidence_ranges['0.7-0.9'] += 1
                                else:
                                    confidence_ranges['0.9-1.0'] += 1
                except:
                    pass
            
            # 分析融合价格置信度
            if detail.merged_prices:
                try:
                    merged_data = json.loads(detail.merged_prices)
                    if isinstance(merged_data, list):
                        for price_item in merged_data:
                            if isinstance(price_item, dict):
                                confidence = price_item.get('confidence', 0)
                                total_prices += 1
                                
                                if confidence <= 0.1:
                                    confidence_ranges['0.0-0.1'] += 1
                                elif confidence <= 0.3:
                                    confidence_ranges['0.1-0.3'] += 1
                                elif confidence <= 0.5:
                                    confidence_ranges['0.3-0.5'] += 1
                                elif confidence <= 0.7:
                                    confidence_ranges['0.5-0.7'] += 1
                                elif confidence <= 0.9:
                                    confidence_ranges['0.7-0.9'] += 1
                                else:
                                    confidence_ranges['0.9-1.0'] += 1
                except:
                    pass
        
        logger.info(f"📈 置信度分布统计:")
        logger.info(f"  总价格数: {total_prices}")
        for range_name, count in confidence_ranges.items():
            percentage = count / total_prices * 100 if total_prices > 0 else 0
            logger.info(f"  {range_name}: {count} 个 ({percentage:.1f}%)")
        
        return confidence_ranges, total_prices
        
    except Exception as e:
        logger.error(f"分析置信度分布失败: {e}")
        return {}, 0
    finally:
        db.close()

def main():
    """主函数"""
    logger.info("🚀 开始重新建立置信度模型和重新分配置信度...")
    
    # 1. 重新建立正态分布模型
    confidence_model = rebuild_confidence_models()
    
    # 2. 重新计算所有价格的置信度
    updated_courts, updated_prices = recalculate_all_confidence_scores(confidence_model)
    
    # 3. 分析置信度分布
    confidence_ranges, total_prices = analyze_confidence_distribution()
    
    # 4. 输出总结
    logger.info("🎉 置信度模型重建和重新分配完成!")
    logger.info(f"📊 总结:")
    logger.info(f"  更新场馆数: {updated_courts}")
    logger.info(f"  更新价格数: {updated_prices}")
    logger.info(f"  总价格数: {total_prices}")
    
    # 保存结果到文件
    result = {
        'timestamp': datetime.now().isoformat(),
        'updated_courts': updated_courts,
        'updated_prices': updated_prices,
        'total_prices': total_prices,
        'confidence_distribution': confidence_ranges
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"confidence_rebuild_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 结果已保存到: {filename}")

if __name__ == "__main__":
    main() 