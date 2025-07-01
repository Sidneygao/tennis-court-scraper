#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中真实价格数据的分布情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_real_price_distribution():
    """检查真实价格数据分布"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        all_courts = db.query(TennisCourt).all()
        print(f"总场馆数: {len(all_courts)}")
        
        # 统计有真实价格数据的场馆
        courts_with_prices = []
        courts_without_prices = []
        
        for court in all_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            
            has_real_prices = False
            price_sources = []
            
            if detail:
                # 检查BING价格
                if detail.bing_prices:
                    try:
                        price_data = json.loads(detail.bing_prices)
                        if price_data and isinstance(price_data, list) and len(price_data) > 0:
                            has_real_prices = True
                            price_sources.append('bing')
                    except:
                        pass
                
                # 检查融合价格
                if detail.merged_prices:
                    try:
                        price_data = json.loads(detail.merged_prices)
                        if price_data and isinstance(price_data, list) and len(price_data) > 0:
                            has_real_prices = True
                            price_sources.append('merged')
                    except:
                        pass
                
                # 检查点评价格
                if detail.dianping_prices:
                    try:
                        price_data = json.loads(detail.dianping_prices)
                        if price_data and isinstance(price_data, list) and len(price_data) > 0:
                            has_real_prices = True
                            price_sources.append('dianping')
                    except:
                        pass
                
                # 检查美团价格
                if detail.meituan_prices:
                    try:
                        price_data = json.loads(detail.meituan_prices)
                        if price_data and isinstance(price_data, list) and len(price_data) > 0:
                            has_real_prices = True
                            price_sources.append('meituan')
                    except:
                        pass
            
            if has_real_prices:
                courts_with_prices.append({
                    'id': court.id,
                    'name': court.name,
                    'area': court.area,
                    'latitude': court.latitude,
                    'longitude': court.longitude,
                    'price_sources': price_sources
                })
            else:
                courts_without_prices.append({
                    'id': court.id,
                    'name': court.name,
                    'area': court.area
                })
        
        print(f"\n有真实价格数据的场馆: {len(courts_with_prices)}")
        print(f"无真实价格数据的场馆: {len(courts_without_prices)}")
        print(f"真实价格数据覆盖率: {len(courts_with_prices)/len(all_courts)*100:.1f}%")
        
        # 按区域统计
        area_stats = {}
        for court in courts_with_prices:
            area = court['area']
            if area not in area_stats:
                area_stats[area] = {'with_prices': 0, 'total': 0}
            area_stats[area]['with_prices'] += 1
        
        for court in all_courts:
            area = court.area
            if area not in area_stats:
                area_stats[area] = {'with_prices': 0, 'total': 0}
            area_stats[area]['total'] += 1
        
        print(f"\n各区域真实价格数据分布:")
        for area, stats in area_stats.items():
            coverage = stats['with_prices'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {area}: {stats['with_prices']}/{stats['total']} ({coverage:.1f}%)")
        
        # 显示有价格数据的场馆详情
        print(f"\n有真实价格数据的场馆详情:")
        for court in courts_with_prices[:10]:  # 只显示前10个
            print(f"  {court['id']}: {court['name']} ({court['area']}) - 价格来源: {', '.join(court['price_sources'])}")
        
        if len(courts_with_prices) > 10:
            print(f"  ... 还有 {len(courts_with_prices) - 10} 个场馆")
        
        # 检查坐标分布
        courts_with_coords = [c for c in all_courts if c.latitude and c.longitude]
        print(f"\n坐标数据统计:")
        print(f"  有坐标的场馆: {len(courts_with_coords)}")
        print(f"  无坐标的场馆: {len(all_courts) - len(courts_with_coords)}")
        
        # 检查有坐标且有价格的场馆
        courts_with_coords_and_prices = [c for c in courts_with_prices if c['latitude'] and c['longitude']]
        print(f"  有坐标且有价格的场馆: {len(courts_with_coords_and_prices)}")
        
        return {
            'total_courts': len(all_courts),
            'courts_with_prices': len(courts_with_prices),
            'courts_without_prices': len(courts_without_prices),
            'coverage_rate': len(courts_with_prices)/len(all_courts)*100,
            'area_stats': area_stats,
            'courts_with_coords': len(courts_with_coords),
            'courts_with_coords_and_prices': len(courts_with_coords_and_prices)
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    check_real_price_distribution() 