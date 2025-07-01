#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用预测器类执行批量预测
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

def direct_batch_predict():
    print("🔄 直接使用预测器类执行批量预测...")
    
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取所有场馆
    courts = db.query(TennisCourt).all()
    print(f"📊 找到 {len(courts)} 个场馆")
    
    success_count = 0
    failed_count = 0
    consecutive_none = 0
    consecutive_global = 0
    threshold = 4  # 连续4次即暂停
    info_islands = []  # 新增：记录信息孤岛
    
    for i, court in enumerate(courts, 1):
        print(f"\n[{i}/{len(courts)}] 处理场馆: {court.name} (ID: {court.id})")
        
        try:
            # 执行预测
            result = predictor.predict_price_for_court(court)
            
            if result:
                # 判断是否为全局均值预测
                is_global = False
                if result.get('source_courts') == '全局同类型均值预测':
                    # 再次确认16KM内无有效样本
                    nearby = predictor.find_nearby_courts_with_prices(court, 16.0)
                    if not nearby:
                        info_islands.append({
                            'id': court.id,
                            'name': court.name,
                            'address': court.address,
                            'latitude': court.latitude,
                            'longitude': court.longitude
                        })
                        print(f"⚠️ 信息孤岛：{court.name} (ID: {court.id}) 16KM内无有效样本")
                    else:
                        consecutive_global += 1
                        consecutive_none = 0
                        print(f"  ⚠️ 仅用全局通用算法预测（全局同类型均值预测）")
                else:
                    consecutive_global = 0
                    consecutive_none = 0
                # 更新数据库
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if not detail:
                    detail = CourtDetail(court_id=court.id)
                    db.add(detail)
                detail.predict_prices = json.dumps(result, ensure_ascii=False)
                db.commit()
                peak_price = result.get('peak_price')
                off_peak_price = result.get('off_peak_price')
                print(f"  ✅ 预测成功: 黄金{peak_price}元, 非黄金{off_peak_price}元")
                success_count += 1
            else:
                consecutive_none += 1
                consecutive_global = 0
                print(f"  ⚠️ 无预测结果（None）")
                failed_count += 1
            # 检查连续失败/全局通用算法
            if consecutive_none >= threshold:
                print(f"\n⏸️ 连续{threshold}次预测为None，自动暂停批量预测！请人工排查数据或算法问题。")
                break
            if consecutive_global >= threshold:
                print(f"\n⏸️ 连续{threshold}次只能用全局通用算法，自动暂停批量预测！请人工排查数据覆盖或邻域样本问题。")
                break
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            failed_count += 1
            consecutive_none += 1
            consecutive_global = 0
            if consecutive_none >= threshold:
                print(f"\n⏸️ 连续{threshold}次预测为None，自动暂停批量预测！请人工排查数据或算法问题。")
                break
    print(f"\n📊 批量预测完成:")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {failed_count} 个")
    print(f"  总计: {i} 个（如提前暂停则未遍历全部）")
    print(f"\n===== 信息孤岛场馆名单（仅全局均值且16KM无样本） =====")
    if info_islands:
        for c in info_islands:
            print(f"- {c['name']} (ID: {c['id']}) 地址: {c['address']} 坐标: ({c['latitude']}, {c['longitude']})")
        print(f"共计 {len(info_islands)} 个信息孤岛场馆！")
    else:
        print("本次无信息孤岛场馆！")

if __name__ == "__main__":
    direct_batch_predict() 