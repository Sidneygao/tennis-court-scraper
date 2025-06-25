from app.database import get_db
from app.models import TennisCourt
from datetime import datetime

test_courts = [
    {
        'name': '测试场馆A（东坝）',
        'address': '东坝测试路1号',
        'phone': '13800000001',
        'area': 'dongba',
        'area_name': '东坝',
        'latitude': 116.5601,
        'longitude': 39.9581,
        'peak_price': '120元/小时',
        'off_peak_price': '80元/小时',
        'member_price': '60元/小时',
        'business_hours': '8:00-22:00',
        'data_source': 'test',
        'source_url': '',
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    },
    {
        'name': '测试场馆B（望京）',
        'address': '望京测试路2号',
        'phone': '13800000002',
        'area': 'wangjing',
        'area_name': '望京',
        'latitude': 116.4829,
        'longitude': 39.9969,
        'peak_price': '100元/小时',
        'off_peak_price': '60元/小时',
        'member_price': '50元/小时',
        'business_hours': '7:00-23:00',
        'data_source': 'test',
        'source_url': '',
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    },
    {
        'name': '测试场馆C（酒仙桥）',
        'address': '酒仙桥测试路3号',
        'phone': '13800000003',
        'area': 'jiuxianqiao',
        'area_name': '酒仙桥',
        'latitude': 116.5203,
        'longitude': 39.9842,
        'peak_price': '90元/小时',
        'off_peak_price': '40元/小时',
        'member_price': '30元/小时',
        'business_hours': '9:00-21:00',
        'data_source': 'test',
        'source_url': '',
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
    },
]

def main():
    db = next(get_db())
    for court in test_courts:
        db.add(TennisCourt(**court))
    db.commit()
    print('测试场馆已插入！')

if __name__ == '__main__':
    main() 