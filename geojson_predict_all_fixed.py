#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新执行GeoJSON+2KM步进法预测价格 - 使用正确的经纬度数据
"""
import sqlite3
import json
import math
from datetime import datetime
from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt, CourtDetail

def calculate_distance(lat1, lng1, lat2, lng2):
    """计算两点间距离（公里）"""
    R = 6371  # 地球半径（公里）
    
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_nearby_courts_with_real_prices(cursor, target_lat, target_lng, max_distance=16.0):
    """获取指定距离内有真实价格的场馆"""
    cursor.execute("""
        SELECT tc.id, tc.name, tc.latitude, tc.longitude, tc.court_type, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL 
        AND cd.merged_prices != '[]'
        AND cd.merged_prices != 'null'
    """)
    
    courts_with_prices = cursor.fetchall()
    nearby_courts = []
    
    for court_id, name, lat, lng, court_type, merged_prices in courts_with_prices:
        distance = calculate_distance(target_lat, target_lng, lat, lng)
        
        if distance <= max_distance:
            try:
                prices = json.loads(merged_prices) if merged_prices else []
                if prices:
                    nearby_courts.append({
                        'id': court_id,
                        'name': name,
                        'latitude': lat,
                        'longitude': lng,
                        'court_type': court_type,
                        'distance': distance,
                        'prices': prices
                    })
            except:
                continue
    
    return sorted(nearby_courts, key=lambda x: x['distance'])

def main():
    print("🔍 重新执行GeoJSON+2KM步进法预测价格...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 初始化数据库连接和预测器
    db = next(get_db())
    predictor = PricePredictor()
    
    # 2. 统计有真实价格的场馆
    courts_with_real_prices = db.query(TennisCourt).join(
        CourtDetail, CourtDetail.court_id == TennisCourt.id
    ).filter(
        CourtDetail.merged_prices.isnot(None),
        CourtDetail.merged_prices != '[]',
        CourtDetail.merged_prices != 'null'
    ).count()
    
    print(f"📊 有真实价格的场馆数: {courts_with_real_prices}")
    
    # 3. 获取所有需要预测的场馆
    all_courts = db.query(TennisCourt).all()
    print(f"📊 总场馆数: {len(all_courts)}")
    
    # 4. 执行预测
    results = []
    success_count = 0
    no_reference_count = 0
    
    for court in all_courts:
        print(f"\n🔍 开始分析场馆: {court.name}")
        
        try:
            # 使用现有的预测方法
            prediction = predictor.predict_price_for_court(court)
            
            if prediction:
                # 更新数据库
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if not detail:
                    detail = CourtDetail(court_id=court.id)
                    db.add(detail)
                    db.commit()
                    db.refresh(detail)
                
                detail.predict_prices = json.dumps(prediction, ensure_ascii=False)
                db.commit()
                
                print(f"  ✅ 预测成功: {prediction}")
                success_count += 1
                
                results.append({
                    'court_id': court.id,
                    'name': court.name,
                    'prediction': prediction,
                    'search_radius': prediction.get('search_radius', 'unknown'),
                    'data_count': prediction.get('data_count', 0)
                })
            else:
                print(f"  ❌ 预测失败")
                no_reference_count += 1
                
        except Exception as e:
            print(f"  ❌ 预测异常: {str(e)}")
            no_reference_count += 1
    
    # 5. 统计结果
    print(f"\n📊 预测结果统计:")
    print(f"  总场馆数: {len(all_courts)}")
    print(f"  预测成功: {success_count} 个")
    print(f"  无参考数据: {no_reference_count} 个")
    print(f"  成功率: {success_count/len(all_courts)*100:.1f}%")
    
    # 6. 保存详细结果
    result_file = f"geojson_predict_results_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_courts': len(all_courts),
                'success_count': success_count,
                'no_reference_count': no_reference_count,
                'success_rate': success_count/len(all_courts)*100
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📁 详细结果已保存到: {result_file}")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db.close()

if __name__ == "__main__":
    main() 