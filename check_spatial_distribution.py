import sqlite3
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

def check_shuangjing_area():
    """检查双井一带的场馆分布（放宽范围）"""
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 放宽双井一带的经纬度范围
    min_lon, max_lon = 116.44, 116.50
    min_lat, max_lat = 39.88, 39.92
    
    # 查询该区域内的所有场馆
    cursor.execute("""
        SELECT t.id, t.name, t.latitude, t.longitude, 
               d.merged_prices, d.predict_prices
        FROM tennis_courts t
        LEFT JOIN court_details d ON t.id = d.court_id
        WHERE t.longitude BETWEEN ? AND ? 
        AND t.latitude BETWEEN ? AND ?
        ORDER BY t.id
    """, (min_lon, max_lon, min_lat, max_lat))
    
    courts = cursor.fetchall()
    print(f"双井一带（{min_lon}-{max_lon}, {min_lat}-{max_lat}）的场馆：")
    print("=" * 80)
    
    real_price_courts = []
    no_price_courts = []
    
    for court in courts:
        court_id, name, lat, lon, merged_prices, predict_prices = court
        print(f"ID: {court_id}, 名称: {name}")
        print(f"  坐标: ({lat}, {lon})")
        print(f"  merged_prices: {'有' if merged_prices else '无'}")
        print(f"  predict_prices: {'有' if predict_prices else '无'}")
        
        if merged_prices:
            real_price_courts.append((court_id, name, lat, lon))
        else:
            no_price_courts.append((court_id, name, lat, lon))
        print()
    
    print(f"该区域总计: {len(courts)}家场馆")
    print(f"有真实价格: {len(real_price_courts)}家")
    print(f"无真实价格: {len(no_price_courts)}家")
    print()
    
    # 检查无真实价格场馆的预测情况
    if no_price_courts:
        print("无真实价格场馆的预测分析：")
        print("=" * 50)
        
        for court_id, name, lat, lon in no_price_courts:
            print(f"\n检查 {name} (ID: {court_id}) 的邻居：")
            
            # 查找16KM内的真实价格场馆
            nearby_real_courts = []
            for real_court in real_price_courts:
                real_lat, real_lon = real_court[2], real_court[3]
                distance = haversine_distance(lat, lon, real_lat, real_lon)
                if distance <= 16:
                    nearby_real_courts.append((real_court[0], real_court[1], distance))
            
            nearby_real_courts.sort(key=lambda x: x[2])  # 按距离排序
            
            print(f"  16KM内真实价格场馆数量: {len(nearby_real_courts)}")
            if nearby_real_courts:
                print("  最近的几家:")
                for i, (nearby_id, nearby_name, dist) in enumerate(nearby_real_courts[:5]):
                    print(f"    {i+1}. {nearby_name} (ID: {nearby_id}) - {dist:.2f}KM")
            else:
                print("  无16KM内的真实价格场馆")
    
    conn.close()

def check_geojson_shuangjing():
    """直接遍历geojson，统计双井一带的点"""
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    
    min_lon, max_lon = 116.46, 116.48
    min_lat, max_lat = 39.89, 39.91
    
    hits = []
    for feat in geo['features']:
        lon = feat['geometry']['coordinates'][0]
        lat = feat['geometry']['coordinates'][1]
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            hits.append(feat)
    
    print(f"GeoJSON中双井一带（{min_lon}-{max_lon}, {min_lat}-{max_lat}）的场馆共{len(hits)}家：")
    for feat in hits:
        props = feat['properties']
        print(f"ID: {props.get('court_id')}, 名称: {props.get('name')}, 坐标: ({lat}, {lon})")

def geojson_stats():
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    lons = []
    lats = []
    for feat in geo['features']:
        lons.append(feat['geometry']['coordinates'][0])
        lats.append(feat['geometry']['coordinates'][1])
    print(f"GeoJSON总计{len(lons)}家场馆")
    print(f"经度范围: {min(lons):.6f} ~ {max(lons):.6f}")
    print(f"纬度范围: {min(lats):.6f} ~ {max(lats):.6f}")

def geojson_shuangjing_distance():
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    min_lon, max_lon = 116.46, 116.48
    min_lat, max_lat = 39.89, 39.91
    points = []
    for feat in geo['features']:
        lon = feat['geometry']['coordinates'][0]
        lat = feat['geometry']['coordinates'][1]
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            points.append((feat['properties']['name'], lat, lon))
    n = len(points)
    if n < 2:
        print(f"双井区域内点数不足2个，无法计算距离")
        return
    dists = []
    for i in range(n):
        for j in range(i+1, n):
            d = haversine_distance(points[i][1], points[i][2], points[j][1], points[j][2])
            dists.append(d)
    print(f"双井区域内{n}家场馆，两两平均距离: {sum(dists)/len(dists):.3f} KM，最小: {min(dists):.3f} KM，最大: {max(dists):.3f} KM")
    print("详细距离矩阵：")
    for i in range(n):
        for j in range(i+1, n):
            print(f"{points[i][0]} <-> {points[j][0]}: {haversine_distance(points[i][1], points[i][2], points[j][1], points[j][2]):.3f} KM")

def geojson_shuangjing_predict():
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    min_lon, max_lon = 116.46, 116.48
    min_lat, max_lat = 39.89, 39.91
    # 只取双井区域点
    points = []
    for feat in geo['features']:
        lon = feat['geometry']['coordinates'][0]
        lat = feat['geometry']['coordinates'][1]
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            # 假设真实价格写在props['price']，如无则用模拟值
            price = feat['properties'].get('price', 100)  # 这里用100做演示
            points.append({'name': feat['properties']['name'], 'lat': lat, 'lon': lon, 'price': price})
    n = len(points)
    print(f"双井区域内{n}家场馆，基于16KM邻居均值预测：")
    for i, p in enumerate(points):
        neighbors = []
        for j, q in enumerate(points):
            if i == j:
                continue
            d = haversine_distance(p['lat'], p['lon'], q['lat'], q['lon'])
            if d <= 16:
                neighbors.append(q['price'])
        if neighbors:
            pred = sum(neighbors) / len(neighbors)
            print(f"{p['name']} 预测价格: {pred:.2f}（邻居数: {len(neighbors)}）")
        else:
            print(f"{p['name']} 无邻居，无法预测")

def geojson_shuangjing_2km_steps():
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    min_lon, max_lon = 116.46, 116.48
    min_lat, max_lat = 39.89, 39.91
    # 只取双井区域点
    points = []
    for feat in geo['features']:
        lon = feat['geometry']['coordinates'][0]
        lat = feat['geometry']['coordinates'][1]
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            price = feat['properties'].get('price', 100)  # 这里用100做演示
            points.append({'name': feat['properties']['name'], 'lat': lat, 'lon': lon, 'price': price})
    n = len(points)
    print(f"双井区域内{n}家场馆，2KM步进法预测：")
    for p in points:
        print(f"\n场馆：{p['name']}")
        for step in range(2, 18, 2):
            neighbors = []
            for q in points:
                if p is q:
                    continue
                d = haversine_distance(p['lat'], p['lon'], q['lat'], q['lon'])
                if d <= step:
                    neighbors.append(q['price'])
            if neighbors:
                pred = sum(neighbors) / len(neighbors)
                print(f"  {step}KM内邻居数: {len(neighbors)}，均值预测: {pred:.2f}")
            else:
                print(f"  {step}KM内无邻居")

def geojson_shuangjing_real_predict():
    # 读取真实价格数据
    with open('real_courts_price_stats.json', 'r', encoding='utf-8') as f:
        price_data = json.load(f)
    # 建立court_id到价格的映射
    price_map = {}
    for court in price_data['courts']:
        court_id = court['court_id']
        # 取黄金和非黄金价格的平均值
        peak_price = court.get('peak_price', 0)
        offpeak_price = court.get('offpeak_price', 0)
        if peak_price and offpeak_price:
            avg_price = (peak_price + offpeak_price) / 2
        elif peak_price:
            avg_price = peak_price
        elif offpeak_price:
            avg_price = offpeak_price
        else:
            avg_price = 0
        price_map[court_id] = avg_price
    
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geo = json.load(f)
    min_lon, max_lon = 116.46, 116.48
    min_lat, max_lat = 39.89, 39.91
    # 只取双井区域点
    points = []
    for feat in geo['features']:
        lon = feat['geometry']['coordinates'][0]
        lat = feat['geometry']['coordinates'][1]
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            court_id = feat['properties']['court_id']
            price = price_map.get(court_id, 0)
            points.append({'name': feat['properties']['name'], 'lat': lat, 'lon': lon, 'price': price, 'court_id': court_id})
    n = len(points)
    print(f"双井区域内{n}家场馆，1KM步进法真实价格预测：")
    for p in points:
        print(f"\n场馆：{p['name']} (ID: {p['court_id']})")
        print(f"  真实价格: {p['price']:.2f}")
        for step in range(1, 17, 1):  # 从1KM开始，步长1KM
            neighbors = []
            for q in points:
                if p is q:
                    continue
                d = haversine_distance(p['lat'], p['lon'], q['lat'], q['lon'])
                if d <= step and q['price'] > 0:
                    neighbors.append(q['price'])
            if neighbors:
                pred = sum(neighbors) / len(neighbors)
                print(f"  {step}KM内邻居数: {len(neighbors)}，均值预测: {pred:.2f}")
            else:
                print(f"  {step}KM内无有效邻居")

if __name__ == "__main__":
    check_shuangjing_area()
    print('\n' + '='*80 + '\n')
    check_geojson_shuangjing()
    print('\n' + '='*80 + '\n')
    geojson_stats()
    print('\n' + '='*80 + '\n')
    geojson_shuangjing_distance()
    print('\n' + '='*80 + '\n')
    geojson_shuangjing_predict()
    print('\n' + '='*80 + '\n')
    geojson_shuangjing_2km_steps()
    print('\n' + '='*80 + '\n')
    geojson_shuangjing_real_predict() 