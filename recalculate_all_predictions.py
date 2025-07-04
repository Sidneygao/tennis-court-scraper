#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新计算所有场馆的预测价格
使用邻域中位数法：优先分黄金/非黄金/会员价分别取邻域样本的中位数，样本不足时合并为一个综合中位数
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def recalculate_all_predictions():
    """重新计算所有场馆的预测价格"""
    print("🔄 开始重新计算所有场馆的预测价格...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取所有场馆
    courts = db.query(TennisCourt).all()
    total_courts = len(courts)
    print(f"📊 总场馆数: {total_courts}")
    
    # 统计变量
    success_count = 0
    failed_count = 0
    no_detail_count = 0
    results = []
    
    for i, court in enumerate(courts, 1):
        print(f"\n[{i}/{total_courts}] 处理场馆: {court.name}")
        
        # 查找详情数据
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        if not detail:
            print(f"  ❌ 无详情数据")
            no_detail_count += 1
            continue
        
        try:
            # 重新预测价格
            prediction_result = predictor.predict_price_for_court(court)
            
            if prediction_result:
                # 更新预测价格
                detail.predict_prices = json.dumps(prediction_result, ensure_ascii=False)
                detail.predict_method = "邻域中位数法"
                detail.updated_at = datetime.now()
                
                db.commit()
                
                print(f"  ✅ 预测成功")
                print(f"     预测结果: {detail.predict_prices}")
                
                success_count += 1
                
                # 记录结果
                results.append({
                    'court_id': court.id,
                    'court_name': court.name,
                    'court_type': court.court_type,
                    'area': court.area,
                    'predictions': detail.predict_prices,
                    'method': detail.predict_method,
                    'success': True
                })
            else:
                print(f"  ❌ 预测失败: 无预测结果")
                failed_count += 1
                
                results.append({
                    'court_id': court.id,
                    'court_name': court.name,
                    'court_type': court.court_type,
                    'area': court.area,
                    'error': '无预测结果',
                    'success': False
                })
                
        except Exception as e:
            print(f"  ❌ 处理异常: {str(e)}")
            failed_count += 1
            
            results.append({
                'court_id': court.id,
                'court_name': court.name,
                'court_type': court.court_type,
                'area': court.area,
                'error': str(e),
                'success': False
            })
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f'recalculate_results_{timestamp}.json'
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_courts': total_courts,
                'success_count': success_count,
                'failed_count': failed_count,
                'no_detail_count': no_detail_count,
                'success_rate': f"{success_count/total_courts*100:.1f}%" if total_courts > 0 else "0%"
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 重新计算完成!")
    print(f"📊 统计结果:")
    print(f"   总场馆数: {total_courts}")
    print(f"   成功预测: {success_count}")
    print(f"   预测失败: {failed_count}")
    print(f"   无详情数据: {no_detail_count}")
    print(f"   成功率: {success_count/total_courts*100:.1f}%" if total_courts > 0 else "0%")
    print(f"📁 结果已保存到: {result_file}")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    recalculate_all_predictions() 