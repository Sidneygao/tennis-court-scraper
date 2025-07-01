import sqlite3
import json
import math
import re

def extract_peak_offpeak(price_data):
    peak = None
    offpeak = None
    if not isinstance(price_data, list):
        return peak, offpeak
    for item in price_data:
        if not isinstance(item, dict):
            continue
        price_type = item.get('type', '').lower()
        price_str = item.get('price', '')
        matches = re.findall(r'(\d+)', price_str)
        price_value = int(matches[0]) if matches else None
        if price_value is None:
            continue
        if any(k in price_type for k in ['黄金', '高峰', 'peak', '黄金时间']) and not ('非' in price_type or 'off' in price_type):
            peak = price_value
        elif any(k in price_type for k in ['非黄金', '非高峰', 'off', '非黄金时间']) or '非' in price_type or 'off' in price_type:
            offpeak = price_value
    return peak, offpeak

def export_price_fields():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.court_id, c.name, d.merged_prices
        FROM court_details d
        LEFT JOIN tennis_courts c ON d.court_id = c.id
        WHERE d.merged_prices IS NOT NULL AND d.merged_prices != ''
    ''')
    rows = cursor.fetchall()
    result = []
    peak_count = 0
    offpeak_count = 0
    for row in rows:
        cid, name, merged = row
        try:
            merged_obj = json.loads(merged) if merged else None
        except:
            merged_obj = None
        peak, offpeak = extract_peak_offpeak(merged_obj)
        if peak is not None:
            peak_count += 1
        if offpeak is not None:
            offpeak_count += 1
        result.append({
            'court_id': cid,
            'name': name,
            'merged_prices': merged_obj,
            'has_peak_price': peak is not None,
            'has_offpeak_price': offpeak is not None,
            'peak_price': peak,
            'offpeak_price': offpeak
        })
    stats = {
        'total': len(result),
        'peak_count': peak_count,
        'offpeak_count': offpeak_count,
        'courts': result
    }
    with open('real_courts_price_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f'已导出 {len(result)} 家有真实价格的场馆及黄金/非黄金识别统计到 real_courts_price_stats.json')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半径，单位KM
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calc_avg_distance():
    with open('real_courts_locations.json', 'r', encoding='utf-8') as f:
        courts = json.load(f)
    n = len(courts)
    if n < 2:
        print('场馆数量不足2家，无法计算平均距离')
        return
    total_dist = 0
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            lat1, lon1 = courts[i]['latitude'], courts[i]['longitude']
            lat2, lon2 = courts[j]['latitude'], courts[j]['longitude']
            dist = haversine(lat1, lon1, lat2, lon2)
            total_dist += dist
            count += 1
    avg_dist = total_dist / count if count else 0
    print(f'这{n}家场馆的两两平均距离为: {avg_dist:.2f} KM')

def export_geojson():
    with open('real_courts_locations.json', 'r', encoding='utf-8') as f:
        courts = json.load(f)
    features = []
    for court in courts:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [court['latitude'], court['longitude']]
            },
            "properties": {
                "court_id": court['court_id'],
                "name": court['name']
            }
        })
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    with open('real_courts_locations.geojson', 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print('已导出 real_courts_locations.geojson，可用于地图可视化')

if __name__ == "__main__":
    export_price_fields()
    calc_avg_distance()
    export_geojson()
