import json
import math
import sqlite3

def haversine_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（公里）"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def predict_all_courts():
    # 读取真实价格数据
    with open('real_courts_price_stats.json', 'r', encoding='utf-8') as f:
        price_data = json.load(f)
    
    # 建立court_id到价格的映射
    price_map = {}
    for court in price_data['courts']:
        court_id = court['court_id']
        peak_price = court.get('peak_price', 0)
        offpeak_price = court.get('offpeak_price', 0)
        price_map[court_id] = {'peak': peak_price, 'offpeak': offpeak_price}
    
    # 读取数据库中的所有场馆
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.latitude, t.longitude, d.merged_prices
        FROM tennis_courts t
        LEFT JOIN court_details d ON t.id = d.court_id
        WHERE t.latitude IS NOT NULL AND t.longitude IS NOT NULL
        ORDER BY t.id
    """)
    all_courts = cursor.fetchall()
    conn.close()
    
    # 分离有价格和无价格的场馆
    real_price_courts = []
    no_price_courts = []
    
    for court in all_courts:
        court_id, name, lat, lon, merged_prices = court
        
        if court_id in price_map and price_map[court_id]['peak'] > 0:
            real_price_courts.append({
                'court_id': court_id,
                'name': name,
                'lat': lat,
                'lon': lon,
                'peak_price': price_map[court_id]['peak'],
                'offpeak_price': price_map[court_id]['offpeak']
            })
        else:
            no_price_courts.append({
                'court_id': court_id,
                'name': name,
                'lat': lat,
                'lon': lon
            })
    
    print(f"有真实价格场馆: {len(real_price_courts)}家")
    print(f"无真实价格场馆: {len(no_price_courts)}家")
    print("=" * 80)
    
    # 对无价格场馆进行2KM步进预测
    results = []
    for court in no_price_courts:
        print(f"\n预测场馆: {court['name']} (ID: {court['court_id']})")
        
        # 2KM步进法预测
        for step in range(2, 18, 2):
            peak_neighbors = []
            offpeak_neighbors = []
            
            for neighbor in real_price_courts:
                distance = haversine_distance(court['lat'], court['lon'], neighbor['lat'], neighbor['lon'])
                if distance <= step:
                    peak_neighbors.append(neighbor['peak_price'])
                    offpeak_neighbors.append(neighbor['offpeak_price'])
            
            if len(peak_neighbors) >= 2:  # 至少2个邻居
                peak_pred = sum(peak_neighbors) / len(peak_neighbors)
                offpeak_pred = sum(offpeak_neighbors) / len(offpeak_neighbors)
                
                result = {
                    'court_id': court['court_id'],
                    'name': court['name'],
                    'distance_km': step,
                    'neighbor_count': len(peak_neighbors),
                    'peak_price_pred': round(peak_pred, 2),
                    'offpeak_price_pred': round(offpeak_pred, 2)
                }
                results.append(result)
                
                print(f"  {step}KM内邻居数: {len(peak_neighbors)}")
                print(f"  黄金时段预测: {peak_pred:.2f}元/小时")
                print(f"  非黄金时段预测: {offpeak_pred:.2f}元/小时")
                break  # 找到足够邻居就停止
            else:
                print(f"  {step}KM内邻居数: {len(peak_neighbors)} (不足2个)")
    
    # 保存结果
    with open('geojson_predict_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n预测完成，共{len(results)}家场馆获得预测结果")
    print("结果已保存到 geojson_predict_results.json")

if __name__ == "__main__":
    predict_all_courts() 