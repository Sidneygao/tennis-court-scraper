#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析国贸区域有真实价格场馆在预测时未被采纳的原因
"""
import sqlite3
import json
from math import radians, cos, sin, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

def main():
    print("\n=== 国贸区域真实价格Opt Out原因分析 ===\n")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    # 获取国贸区域有真实价格的场馆
    cursor.execute("""
        SELECT tc.id, tc.name, tc.latitude, tc.longitude, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.area = 'guomao' AND cd.merged_prices IS NOT NULL AND cd.merged_prices != '' AND cd.merged_prices != '[]'
    """)
    results = cursor.fetchall()
    for cid, name, lat, lng, merged_prices in results:
        print(f"🏟️ {name} (ID: {cid})")
        if not lat or not lng:
            print("  ⚠️ 无坐标，无法参与距离计算")
            continue
        try:
            prices = json.loads(merged_prices)
        except:
            print("  ⚠️ 价格数据解析失败")
            continue
        if not prices:
            print("  ⚠️ 价格数据为空")
            continue
        # 检查每条价格是否有异常
        optout_reasons = []
        for item in prices:
            price_val = None
            try:
                price_val = int(''.join(filter(str.isdigit, str(item.get('price','')))))
            except:
                pass
            conf = item.get('confidence', 0.0)
            if price_val is None or price_val <= 0:
                optout_reasons.append('价格无效')
            elif price_val < 10 or price_val > 2000:
                optout_reasons.append(f'价格异常:{price_val}')
            elif conf < 0.1:
                optout_reasons.append(f'置信度过低:{conf:.2f}')
        if not optout_reasons:
            print("  ✅ 价格数据理论可用，需进一步排查是否被距离过滤")
        else:
            print("  ⚠️ Opt Out原因: " + '，'.join(set(optout_reasons)))
    conn.close()

if __name__ == "__main__":
    main() 