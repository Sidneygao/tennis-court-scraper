#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对全部12个区域重新计算场馆类型和价格预测
"""
import sqlite3
import json
import sys
import os
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt, CourtDetail

def assign_area_for_court(lat, lng):
    """
    根据经纬度分配12个区域，全部用圆形区域分配，不做特殊区分
    lat: 经度（latitude）
    lng: 纬度（longitude）
    """
    # 区域中心点和半径 - 与app/config.py完全一致
    area_defs = {
        'guomao':      (116.468, 39.914, 5000),
        'sanlitun':    (116.453, 39.933, 5000),
        'wangjing':    (116.4828, 39.9968, 5000),
        'aoyuncun':    (116.396, 40.008, 5000),
        'chaoyangpark':(116.478, 39.946, 5000),
        'dawanglu':    (116.489, 39.914, 5000),
        'shuangjing':  (116.468, 39.894, 5000),
        'gaobeidian':  (116.525, 39.908, 5000),
        'dongba':      (116.5607, 39.9582, 5000),
        'changying':   (116.601, 39.933, 5000),
        'sanyuanqiao': (116.456, 39.967, 5000),  # 修正三元桥配置
        'fengtai_east':(116.321, 39.858, 8000),
        'fengtai_west':(116.247, 39.858, 8000),
        'yizhuang':    (116.493, 39.808, 8000),
    }
    def haversine(lon1, lat1, lon2, lat2):
        # 经纬度转距离，单位米
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)
        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
        return 2*R*atan2(sqrt(a), sqrt(1-a))
    min_dist = float('inf')
    best_area = None
    for area, (center_lng, center_lat, radius) in area_defs.items():
        dist = haversine(lng, lat, center_lng, center_lat)
        if dist < radius and dist < min_dist:
            min_dist = dist
            best_area = area
    return best_area

def main():
    print("🔄 开始对全部12个区域重新计算...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 第一步：重新分配全部场馆区域...")
    recalculate_area_fields()
    print("\n📊 第二步：重新计算所有场馆类型...")
    recalculate_court_types()
    print("\n💰 第三步：重新计算所有场馆价格预测...")
    recalculate_price_predictions()
    print("\n🔍 第四步：检查计算结果...")
    check_results()
    print(f"\n✅ 全部12个区域重新计算完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def recalculate_court_types():
    """重新计算所有场馆类型"""
    print("  🔄 重新计算场馆类型...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取所有场馆
    cursor.execute("SELECT id, name, address FROM tennis_courts")
    courts = cursor.fetchall()
    
    print(f"  找到 {len(courts)} 个场馆需要重新计算类型")
    
    # 初始化PricePredictor用于类型计算
    predictor = PricePredictor()
    
    updated_count = 0
    for court_id, name, address in courts:
        try:
            # 使用三层次算法计算场馆类型
            court_type = predictor.judge_court_type(name, address or "")
            
            # 更新数据库
            cursor.execute("""
                UPDATE tennis_courts 
                SET court_type = ?, updated_at = ?
                WHERE id = ?
            """, (court_type, datetime.now(), court_id))
            
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"    已处理 {updated_count}/{len(courts)} 个场馆")
                
        except Exception as e:
            print(f"    ❌ 处理场馆 {name} (ID: {court_id}) 时出错: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"  ✅ 场馆类型重新计算完成，更新了 {updated_count} 个场馆")

def recalculate_price_predictions():
    """重新计算所有场馆价格预测"""
    print("  🔄 重新计算价格预测...")
    
    # 使用数据库模型进行预测
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取所有场馆
    courts = db.query(TennisCourt).all()
    print(f"  找到 {len(courts)} 个场馆需要重新计算价格")
    
    # 重新计算所有场馆的价格预测
    updated_count = 0
    success_count = 0
    
    for court in courts:
        try:
            # 使用现有的预测方法
            prediction_result = predictor.predict_price_for_court(court)
            
            if prediction_result:
                # 查找或创建详情记录
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if not detail:
                    detail = CourtDetail(court_id=court.id)
                    db.add(detail)
                
                # 更新预测价格
                detail.predict_prices = json.dumps(prediction_result, ensure_ascii=False)
                detail.updated_at = datetime.now()
                
                success_count += 1
            
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"    已处理 {updated_count}/{len(courts)} 个场馆，成功 {success_count} 个")
                
        except Exception as e:
            print(f"    ❌ 处理场馆 {court.name} (ID: {court.id}) 时出错: {e}")
    
    db.commit()
    db.close()
    
    print(f"  ✅ 价格预测重新计算完成，处理了 {updated_count} 个场馆，成功 {success_count} 个")

def check_results():
    """检查计算结果"""
    print("  🔍 检查计算结果...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 检查场馆类型分布
    print("\n📊 场馆类型分布:")
    cursor.execute("""
        SELECT court_type, COUNT(*) as count
        FROM tennis_courts
        WHERE court_type IS NOT NULL
        GROUP BY court_type
        ORDER BY count DESC
    """)
    
    type_stats = cursor.fetchall()
    for court_type, count in type_stats:
        print(f"    {court_type}: {count} 个场馆")
    
    # 2. 检查价格预测分布
    print("\n💰 价格预测分布:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN cd.predict_prices IS NOT NULL THEN 1 ELSE 0 END) as has_predict,
            SUM(CASE WHEN cd.merged_prices IS NOT NULL AND cd.merged_prices != '[]' THEN 1 ELSE 0 END) as has_real
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
    """)
    
    price_stats = cursor.fetchone()
    print(f"    总场馆数: {price_stats[0]}")
    print(f"    有预测价格: {price_stats[1]}")
    print(f"    有真实价格: {price_stats[2]}")
    
    # 3. 检查各区域场馆数量
    print("\n🏢 各区域场馆数量:")
    
    # 定义12个区域
    areas = {
        'guomao': '国贸CBD核心区',
        'sanyuanqiao': '三元桥-太阳宫国际生活区',
        'wangjing': '望京科技商务区',
        'aoyuncun': '奥运村-亚运村文体区',
        'chaoyanggongyuan': '朝阳公园-蓝色港湾生态区',
        'dawanglu': '大望路-华贸商业区',
        'shuangjing': '双井-富力城居住区',
        'gaobeidian': '高碑店-传媒文化区',
        'dongba': '东坝-第四使馆区',
        'changying': '常营-东坝边缘居住区',
        'fengtai_east': '丰台区东部',
        'fengtai_west': '丰台区西部',
        'yizhuang': '亦庄'
    }
    
    for area_code, area_name in areas.items():
        if area_code in ['fengtai_east', 'fengtai_west', 'yizhuang']:
            # 动态计算丰台区和亦庄
            if area_code == 'fengtai_east':
                cursor.execute("""
                    SELECT COUNT(*) FROM tennis_courts 
                    WHERE longitude > 116.321 AND (name LIKE '%丰台%' OR address LIKE '%丰台%')
                """)
            elif area_code == 'fengtai_west':
                cursor.execute("""
                    SELECT COUNT(*) FROM tennis_courts 
                    WHERE longitude <= 116.321 AND (name LIKE '%丰台%' OR address LIKE '%丰台%')
                """)
            elif area_code == 'yizhuang':
                cursor.execute("""
                    SELECT COUNT(*) FROM tennis_courts 
                    WHERE name LIKE '%亦庄%' OR address LIKE '%亦庄%'
                """)
        else:
            # 其他区域使用area字段
            cursor.execute("""
                SELECT COUNT(*) FROM tennis_courts WHERE area = ?
            """, (area_code,))
        
        count = cursor.fetchone()[0]
        print(f"    {area_name}: {count} 个场馆")
    
    conn.close()
    
    print("  ✅ 检查完成")

def recalculate_area_fields():
    print("  🔄 重新分配全部场馆区域...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, latitude, longitude FROM tennis_courts")
    courts = cursor.fetchall()
    updated = 0
    for court_id, lat, lng in courts:
        if lat is None or lng is None:
            continue
        area = assign_area_for_court(lat, lng)
        if area:
            cursor.execute("UPDATE tennis_courts SET area = ?, updated_at = ? WHERE id = ?", (area, datetime.now(), court_id))
            updated += 1
    conn.commit()
    conn.close()
    print(f"  ✅ 区域分配完成，更新了 {updated} 个场馆")

if __name__ == "__main__":
    main() 