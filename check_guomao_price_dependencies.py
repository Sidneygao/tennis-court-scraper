#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看国贸地区的具体价格依赖列表
显示每个场馆的预测价格及其依赖的真实价格样本
"""
import sqlite3
import json
from math import radians, cos, sin, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):
    """计算两点间距离，单位米"""
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

def extract_price_value(price_str):
    """从价格字符串中提取数值"""
    if not price_str:
        return None
    try:
        import re
        matches = re.findall(r'(\d+)', str(price_str))
        if matches:
            return int(matches[0])
        return None
    except:
        return None

def main():
    print("\n=== 国贸地区价格依赖详细分析 ===\n")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取国贸区域所有场馆
    cursor.execute("""
        SELECT tc.id, tc.name, tc.latitude, tc.longitude, 
               cd.predict_prices, cd.merged_prices, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.area = 'guomao'
        ORDER BY tc.id
    """)
    
    guomao_courts = cursor.fetchall()
    
    print(f"国贸区域总场馆数: {len(guomao_courts)}\n")
    
    for court_id, name, lat, lng, predict_prices, merged_prices, bing_prices in guomao_courts:
        print(f"🏟️ {name} (ID: {court_id})")
        print(f"   坐标: ({lat}, {lng})")
        
        # 显示预测价格
        if predict_prices:
            try:
                pred = json.loads(predict_prices)
                print(f"   预测价格:")
                print(f"     黄金时段: {pred.get('peak_price', '无')} 元")
                print(f"     非黄金时段: {pred.get('off_peak_price', '无')} 元")
                print(f"     样本数量: {pred.get('data_count', '无')}")
                print(f"     搜索半径: {pred.get('search_radius', '无')} KM")
                
                # 显示依赖的场馆列表
                source_courts = pred.get('source_courts', [])
                if source_courts and isinstance(source_courts, list):
                    print(f"   依赖场馆列表:")
                    for i, src in enumerate(source_courts[:10]):  # 只显示前10个
                        print(f"     {i+1}. {src.get('name', '')} (距离: {src.get('distance', '无')}km)")
                    if len(source_courts) > 10:
                        print(f"     ... 还有 {len(source_courts) - 10} 个场馆")
                elif source_courts == '全局同类型均值预测':
                    print(f"   依赖方式: 全局同类型均值预测")
            except Exception as e:
                print(f"   预测价格解析失败: {e}")
        else:
            print("   无预测价格")
        
        # 显示真实价格样本
        print(f"   真实价格样本:")
        real_prices = []
        
        # 从merged_prices中提取真实价格
        if merged_prices:
            try:
                merged = json.loads(merged_prices)
                if isinstance(merged, list):
                    for item in merged:
                        if isinstance(item, dict) and not item.get('is_predicted', True):
                            real_prices.append({
                                'price': item.get('price', ''),
                                'type': item.get('type', ''),
                                'source': item.get('source', ''),
                                'confidence': item.get('confidence', '')
                            })
            except:
                pass
        
        # 从bing_prices中提取原始价格（如果merged_prices为空）
        if not real_prices and bing_prices:
            try:
                bing = json.loads(bing_prices)
                if isinstance(bing, list):
                    for item in bing:
                        if isinstance(item, dict):
                            real_prices.append({
                                'price': item.get('price', ''),
                                'type': item.get('type', ''),
                                'source': 'BING',
                                'confidence': item.get('confidence', '')
                            })
            except:
                pass
        
        if real_prices:
            for i, price in enumerate(real_prices[:5]):  # 只显示前5个
                print(f"     {i+1}. {price['type']}: {price['price']} 来源: {price['source']} 置信度: {price['confidence']}")
            if len(real_prices) > 5:
                print(f"     ... 还有 {len(real_prices) - 5} 个价格样本")
        else:
            print("     无真实价格样本")
        
        print()
    
    # 统计国贸区域的预测价格分布
    print("\n=== 国贸区域预测价格统计 ===\n")
    
    peak_prices = []
    off_peak_prices = []
    
    for court_id, name, lat, lng, predict_prices, merged_prices, bing_prices in guomao_courts:
        if predict_prices:
            try:
                pred = json.loads(predict_prices)
                if pred.get('peak_price'):
                    peak_prices.append(pred['peak_price'])
                if pred.get('off_peak_price'):
                    off_peak_prices.append(pred['off_peak_price'])
            except:
                continue
    
    if peak_prices:
        print(f"黄金时段价格统计:")
        print(f"  数量: {len(peak_prices)}")
        print(f"  范围: {min(peak_prices)} - {max(peak_prices)} 元")
        print(f"  平均值: {sum(peak_prices) / len(peak_prices):.1f} 元")
        print(f"  中位数: {sorted(peak_prices)[len(peak_prices)//2]} 元")
    
    if off_peak_prices:
        print(f"\n非黄金时段价格统计:")
        print(f"  数量: {len(off_peak_prices)}")
        print(f"  范围: {min(off_peak_prices)} - {max(off_peak_prices)} 元")
        print(f"  平均值: {sum(off_peak_prices) / len(off_peak_prices):.1f} 元")
        print(f"  中位数: {sorted(off_peak_prices)[len(off_peak_prices)//2]} 元")
    
    conn.close()

if __name__ == "__main__":
    main() 