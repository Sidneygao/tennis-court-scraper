#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析国贸场馆预测时被过滤掉的样本数据和具体原因
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
from app.scrapers.price_confidence_model import PriceConfidenceModel
import json
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（公里）"""
    R = 6371  # 地球半径（公里）
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def debug_guomao_filtered_samples():
    """详细分析国贸场馆预测时被过滤掉的样本"""
    db = SessionLocal()
    
    try:
        print("🔍 详细分析国贸场馆预测样本过滤情况\n")
        
        # 获取国贸地区的场馆
        guomao_courts = db.query(TennisCourt).filter(TennisCourt.area == 'guomao').all()
        print(f"📊 国贸地区共有 {len(guomao_courts)} 个场馆")
        
        # 创建预测器和置信度模型
        predictor = PricePredictor()
        confidence_model = PriceConfidenceModel()
        confidence_model.build_normal_distribution_models()
        
        # 获取所有有真实价格的场馆作为候选样本
        all_courts_with_prices = []
        for court in db.query(TennisCourt).all():
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.merged_prices:
                try:
                    merged = json.loads(detail.merged_prices)
                    if isinstance(merged, list):
                        real_prices = [p for p in merged if not p.get('is_predicted', True)]
                        if real_prices:
                            all_courts_with_prices.append({
                                'court': court,
                                'detail': detail,
                                'real_prices': real_prices
                            })
                except:
                    continue
        
        print(f"📊 全数据库共有 {len(all_courts_with_prices)} 个场馆有真实价格")
        
        # 分析每个国贸场馆的样本过滤情况
        for i, guomao_court in enumerate(guomao_courts):
            print(f"\n{'='*60}")
            print(f"🏟️ 国贸场馆 {i+1}/{len(guomao_courts)}: {guomao_court.name}")
            print(f"   ID: {guomao_court.id}")
            print(f"   类型: {guomao_court.court_type}")
            print(f"   坐标: {guomao_court.latitude}, {guomao_court.longitude}")
            
            # 判断场馆类型
            court_type = predictor.judge_court_type(guomao_court.name)
            print(f"   判断类型: {court_type}")
            
            # 查找附近场馆
            nearby_candidates = []
            for candidate in all_courts_with_prices:
                if candidate['court'].id == guomao_court.id:
                    continue  # 跳过自己
                
                # 计算距离
                distance = haversine_distance(
                    guomao_court.latitude, guomao_court.longitude,
                    candidate['court'].latitude, candidate['court'].longitude
                )
                
                # 判断候选场馆类型
                candidate_type = predictor.judge_court_type(candidate['court'].name)
                
                nearby_candidates.append({
                    'court': candidate['court'],
                    'detail': candidate['detail'],
                    'real_prices': candidate['real_prices'],
                    'distance': distance,
                    'candidate_type': candidate_type
                })
            
            print(f"\n📋 距离16KM内的候选场馆: {len([c for c in nearby_candidates if c['distance'] <= 16])} 个")
            
            # 按距离排序
            nearby_candidates.sort(key=lambda x: x['distance'])
            
            # 分析过滤情况
            filtered_reasons = {
                'distance': 0,
                'type_mismatch': 0,
                'price_range': 0,
                'confidence': 0,
                'no_valid_prices': 0,
                'passed': 0
            }
            
            valid_samples = []
            
            for candidate in nearby_candidates[:50]:  # 只分析前50个最近的
                court_name = candidate['court'].name
                distance = candidate['distance']
                candidate_type = candidate['candidate_type']
                
                print(f"\n  🔍 分析候选: {court_name}")
                print(f"     距离: {distance:.2f}KM")
                print(f"     类型: {candidate_type}")
                
                # 距离过滤
                if distance > 16:
                    print(f"     ❌ 被过滤: 距离过远 (>16KM)")
                    filtered_reasons['distance'] += 1
                    continue
                
                # 类型匹配过滤
                if candidate_type != court_type:
                    print(f"     ❌ 被过滤: 类型不匹配 ({candidate_type} != {court_type})")
                    filtered_reasons['type_mismatch'] += 1
                    continue
                
                # 价格和置信度过滤
                valid_prices = []
                for price_item in candidate['real_prices']:
                    price_str = price_item.get('price', '')
                    price_type = price_item.get('type', '标准价格')
                    
                    # 提取价格数值
                    price_value = predictor._extract_price_value(price_str)
                    if price_value is None:
                        continue
                    
                    # 价格范围过滤
                    if court_type == '室内':
                        if price_value < 60 or price_value > 600:
                            print(f"     ❌ 价格 {price_str} 被过滤: 超出室内范围 (60-600)")
                            filtered_reasons['price_range'] += 1
                            continue
                    else:  # 室外
                        if price_value < 50 or price_value > 300:
                            print(f"     ❌ 价格 {price_str} 被过滤: 超出室外范围 (50-300)")
                            filtered_reasons['price_range'] += 1
                            continue
                    
                    # 计算置信度
                    confidence = confidence_model.calculate_confidence(
                        price_value, candidate_type, court_name, price_type
                    )
                    
                    print(f"     ✅ 价格 {price_str} ({price_type}) -> 置信度: {confidence:.3f}")
                    
                    valid_prices.append({
                        'price_str': price_str,
                        'price_value': price_value,
                        'price_type': price_type,
                        'confidence': confidence
                    })
                
                if not valid_prices:
                    print(f"     ❌ 被过滤: 无有效价格")
                    filtered_reasons['no_valid_prices'] += 1
                    continue
                
                # 置信度过滤（假设阈值为0.3）
                high_confidence_prices = [p for p in valid_prices if p['confidence'] >= 0.3]
                if not high_confidence_prices:
                    print(f"     ❌ 被过滤: 置信度过低 (最高: {max(p['confidence'] for p in valid_prices):.3f})")
                    filtered_reasons['confidence'] += 1
                    continue
                
                print(f"     ✅ 通过所有过滤条件，有效样本: {len(high_confidence_prices)} 个")
                filtered_reasons['passed'] += 1
                
                valid_samples.append({
                    'court_name': court_name,
                    'distance': distance,
                    'prices': high_confidence_prices
                })
            
            # 统计结果
            print(f"\n📊 过滤统计:")
            for reason, count in filtered_reasons.items():
                if count > 0:
                    print(f"   {reason}: {count} 个")
            
            print(f"\n✅ 最终有效样本: {len(valid_samples)} 个")
            
            if len(valid_samples) >= 2:
                print(f"🎯 样本充足，可以进行预测")
            else:
                print(f"❌ 样本不足，无法预测 (需要至少2个样本)")
            
            # 显示有效样本详情
            if valid_samples:
                print(f"\n📋 有效样本详情:")
                for i, sample in enumerate(valid_samples[:5]):  # 只显示前5个
                    print(f"   {i+1}. {sample['court_name']} (距离: {sample['distance']:.2f}KM)")
                    for price in sample['prices']:
                        print(f"      • {price['price_str']} ({price['price_type']}) 置信度: {price['confidence']:.3f}")
                if len(valid_samples) > 5:
                    print(f"   ... 还有 {len(valid_samples) - 5} 个样本")
        
        print(f"\n{'='*60}")
        print("🔍 分析完成")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_guomao_filtered_samples() 