import requests
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from ..config import settings
from ..models import ScrapedCourtData

class AmapScraper:
    """高德地图API爬虫"""
    
    def __init__(self):
        self.api_key = settings.amap_api_key
        self.base_url = settings.amap_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_tennis_courts(self, area_key: str) -> List[ScrapedCourtData]:
        """搜索指定区域的网球场馆"""
        if not self.api_key:
            print("警告：未配置高德地图API密钥")
            return []
        
        area_config = settings.target_areas.get(area_key)
        if not area_config:
            print(f"错误：未找到区域配置 {area_key}")
            return []
        
        courts = []
        page = 1
        max_pages = 10  # 最多抓取10页
        
        while page <= max_pages:
            try:
                # 构建搜索参数
                params = {
                    'key': self.api_key,
                    'keywords': '网球场',
                    'location': area_config['center'],
                    'radius': area_config['radius'],
                    'types': '体育休闲服务',
                    'page': page,
                    'offset': 20,  # 每页20条
                    'extensions': 'all'  # 返回详细信息
                }
                
                # 发送请求
                response = self.session.get(
                    f"{self.base_url}/place/around",
                    params=params,
                    timeout=settings.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') != '1':
                    print(f"API错误：{data.get('info', '未知错误')}")
                    break
                
                pois = data.get('pois', [])
                if not pois:
                    break
                
                # 处理POI数据
                for poi in pois:
                    court_data = self._parse_poi_data(poi, area_key, area_config['name'])
                    if court_data:
                        courts.append(court_data)
                
                # 检查是否还有更多数据
                if len(pois) < 20:
                    break
                
                page += 1
                time.sleep(settings.request_delay)  # 请求间隔
                
            except requests.RequestException as e:
                print(f"请求错误：{e}")
                break
            except Exception as e:
                print(f"处理错误：{e}")
                break
        
        print(f"从高德地图获取到 {len(courts)} 个网球场馆")
        return courts
    
    def _parse_poi_data(self, poi: Dict, area_key: str, area_name: str) -> Optional[ScrapedCourtData]:
        """解析POI数据"""
        try:
            name = poi.get('name', '').strip()
            if not name or (('皮克球' in name and '网球' not in name) or '网球' not in name):
                return None
            
            # 提取地址信息
            address = poi.get('address', '')
            if not address:
                address = poi.get('pname', '') + poi.get('cityname', '') + poi.get('adname', '')
            
            # 提取电话信息
            phone = poi.get('tel', '')
            if not isinstance(phone, str):
                phone = ''
            
            # 提取位置信息
            location = poi.get('location', '').split(',')
            latitude = float(location[0]) if len(location) > 0 else None
            longitude = float(location[1]) if len(location) > 1 else None
            
            # 提取营业时间
            business_hours = poi.get('business_area', '')
            if not isinstance(business_hours, str):
                business_hours = ''
            
            # 构建描述信息
            description_parts = []
            if poi.get('type'):
                description_parts.append(f"类型：{poi['type']}")
            if poi.get('distance'):
                description_parts.append(f"距离：{poi['distance']}米")
            
            description = ' | '.join(description_parts) if description_parts else None
            
            return ScrapedCourtData(
                name=name,
                address=address,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                business_hours=business_hours,
                description=description,
                data_source='amap',
                source_url=f"https://uri.amap.com/place/{poi.get('id', '')}",
                raw_data=poi
            )
            
        except Exception as e:
            print(f"解析POI数据错误：{e}")
            return None
    
    def get_court_detail(self, court_id: str) -> Optional[Dict]:
        """获取场馆详细信息"""
        if not self.api_key:
            return None
        
        try:
            params = {
                'key': self.api_key,
                'id': court_id,
                'extensions': 'all'
            }
            
            response = self.session.get(
                f"{self.base_url}/place/detail",
                params=params,
                timeout=settings.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == '1':
                return data.get('poi', {})
            
        except Exception as e:
            print(f"获取场馆详情错误：{e}")
        
        return None
    
    def search_all_areas(self) -> Dict[str, List[ScrapedCourtData]]:
        """搜索所有目标区域"""
        results = {}
        
        for area_key in settings.target_areas.keys():
            print(f"正在搜索 {settings.target_areas[area_key]['name']} 区域的网球场馆...")
            courts = self.search_tennis_courts(area_key)
            results[area_key] = courts
            time.sleep(2)  # 区域间间隔
        
        return results 

if __name__ == "__main__":
    from app.config import settings
    print("AMAP_API_KEY:", settings.amap_api_key)
    scraper = AmapScraper()
    results = scraper.search_all_areas()
    total = sum(len(courts) for courts in results.values())
    print(f"总共抓取到 {total} 个场馆") 