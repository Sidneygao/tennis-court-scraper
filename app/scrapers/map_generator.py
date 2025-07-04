import os
import json
import requests
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class MapGenerator:
    """地图生成器 - 以经纬度为中心生成地图图片"""
    def __init__(self, amap_key: Optional[str] = None):
        self.cache_dir = "data/map_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        # 优先使用传入的API Key，其次使用环境变量
        self.amap_key = amap_key or os.getenv("AMAP_KEY")
        
    def generate_smart_map(self, court_name: str, latitude: float, longitude: float) -> Optional[str]:
        """
        以经纬度为中心生成地图图片，优先OSM，高德地图作为兜底
        """
        try:
            filename = f"{court_name}_{latitude}_{longitude}.png"
            filename = filename.replace("/", "_").replace("\\", "_")
            filepath = os.path.join(self.cache_dir, filename)
            
            # 如果文件已存在，直接返回
            if os.path.exists(filepath):
                return filepath
            
            # 优先使用OSM
            osm_result = self._generate_osm_image(latitude, longitude, filepath)
            if osm_result:
                return osm_result
            
            # OSM失败时使用高德地图API作为兜底
            if self.amap_key:
                return self._generate_amap_image(latitude, longitude, filepath)
            else:
                print("❌ 无可用地图服务")
                return None
                
        except Exception as e:
            print(f"生成地图图片失败: {e}")
            return None
    
    def _generate_amap_image(self, latitude: float, longitude: float, filepath: str) -> Optional[str]:
        """使用高德地图API生成图片"""
        try:
            url = "https://restapi.amap.com/v3/staticmap"
            params = {
                'location': f"{longitude},{latitude}",
                'zoom': 16,
                'size': '600*300',
                'key': self.amap_key,
                'markers': f"{longitude},{latitude},red"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 高德地图生成成功: {filepath}")
                return filepath
            else:
                print(f"❌ 高德地图API返回错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 高德地图生成失败: {e}")
            return None

    def _generate_osm_image(self, latitude: float, longitude: float, filepath: str) -> Optional[str]:
        """使用OpenStreetMap生成图片（兜底方案）"""
        try:
            url = "https://staticmap.openstreetmap.de/staticmap.php"
            params = {
                'center': f"{latitude},{longitude}",
                'zoom': 16,
                'size': '600x300',
                'markers': f"{latitude},{longitude},red-pushpin"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ OSM地图生成成功: {filepath}")
                return filepath
            else:
                print(f"❌ OSM地图API返回错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ OSM地图生成失败: {e}")
            return None
    
    def _get_nearby_traffic(self, lat: float, lng: float) -> Dict[str, Any]:
        """获取附近交通信息（模拟数据）"""
        # 这里可以接入真实的地图API
        # 目前使用模拟数据
        return {
            "subway_stations": [
                {"name": "国贸站", "distance": 800, "lat": lat + 0.008, "lng": lng + 0.008},
                {"name": "双井站", "distance": 1200, "lat": lat - 0.012, "lng": lng - 0.012},
            ],
            "bus_stations": [
                {"name": "国贸桥北站", "distance": 300, "lat": lat + 0.003, "lng": lng + 0.003},
                {"name": "双井桥北站", "distance": 600, "lat": lat - 0.006, "lng": lng - 0.006},
            ]
        }
    
    def _calculate_smart_zoom(self, court_lat: float, court_lng: float, 
                            traffic_info: Dict[str, Any]) -> Tuple[int, float, float]:
        """计算智能比例尺"""
        # 检查2KM内是否有地铁站
        subway_in_2km = any(station["distance"] <= 2000 for station in traffic_info["subway_stations"])
        
        if subway_in_2km:
            # 有地铁站，使用较大比例尺显示2KM范围
            zoom_level = 14
            # 计算包含所有2KM内地铁站的中心点
            points = [(court_lat, court_lng)]
            for station in traffic_info["subway_stations"]:
                if station["distance"] <= 2000:
                    points.append((station["lat"], station["lng"]))
            
            center_lat = sum(p[0] for p in points) / len(points)
            center_lng = sum(p[1] for p in points) / len(points)
        else:
            # 没有地铁站，检查1KM内是否有公交站
            bus_in_1km = any(station["distance"] <= 1000 for station in traffic_info["bus_stations"])
            
            if bus_in_1km:
                # 有公交站，使用中等比例尺显示1KM范围
                zoom_level = 15
                points = [(court_lat, court_lng)]
                for station in traffic_info["bus_stations"]:
                    if station["distance"] <= 1000:
                        points.append((station["lat"], station["lng"]))
                
                center_lat = sum(p[0] for p in points) / len(points)
                center_lng = sum(p[1] for p in points) / len(points)
            else:
                # 没有交通站点，使用场馆为中心的小范围显示
                zoom_level = 16
                center_lat = court_lat
                center_lng = court_lng
        
        return zoom_level, center_lat, center_lng
    
    def _generate_map_image(self, court_name: str, court_lat: float, court_lng: float,
                           center_lat: float, center_lng: float, zoom_level: int,
                           traffic_info: Dict[str, Any], address: str) -> str:
        """生成地图图片"""
        # 创建图片
        width, height = 800, 600
        image = Image.new('RGB', (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # 绘制背景
        draw.rectangle([0, 0, width, height], fill=(245, 245, 245))
        
        # 绘制地图网格（简化版）
        self._draw_map_grid(draw, width, height, center_lat, center_lng, zoom_level)
        
        # 绘制场馆标记
        court_x, court_y = self._latlng_to_pixel(court_lat, court_lng, center_lat, center_lng, zoom_level, width, height)
        self._draw_court_marker(draw, court_x, court_y, court_name)
        
        # 绘制交通站点
        self._draw_traffic_stations(draw, traffic_info, center_lat, center_lng, zoom_level, width, height)
        
        # 添加标题
        self._draw_title(draw, court_name, address, width, height)
        
        # 保存图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"map_{court_name.replace(' ', '_')}_{timestamp}.png"
        filepath = os.path.join(self.cache_dir, filename)
        
        image.save(filepath, "PNG")
        return filepath
    
    def _draw_map_grid(self, draw: ImageDraw.Draw, width: int, height: int, 
                      center_lat: float, center_lng: float, zoom_level: int):
        """绘制地图网格"""
        # 绘制简单的网格线
        grid_size = 50
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=1)
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill=(200, 200, 200), width=1)
    
    def _latlng_to_pixel(self, lat: float, lng: float, center_lat: float, center_lng: float,
                        zoom_level: int, width: int, height: int) -> Tuple[int, int]:
        """经纬度转换为像素坐标"""
        # 简化的坐标转换
        lat_diff = lat - center_lat
        lng_diff = lng - center_lng
        
        # 根据缩放级别调整比例
        scale = 2 ** (16 - zoom_level)
        
        x = width // 2 + int(lng_diff * scale * 10000)
        y = height // 2 - int(lat_diff * scale * 10000)
        
        return x, y
    
    def _draw_court_marker(self, draw: ImageDraw.Draw, x: int, y: int, court_name: str):
        """绘制场馆标记"""
        # 绘制红色圆点
        radius = 8
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(255, 0, 0))
        
        # 绘制场馆名称
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        draw.text((x + 10, y - 10), court_name, fill=(0, 0, 0), font=font)
    
    def _draw_traffic_stations(self, draw: ImageDraw.Draw, traffic_info: Dict[str, Any],
                             center_lat: float, center_lng: float, zoom_level: int,
                             width: int, height: int):
        """绘制交通站点"""
        # 绘制地铁站
        for station in traffic_info["subway_stations"]:
            x, y = self._latlng_to_pixel(station["lat"], station["lng"], 
                                       center_lat, center_lng, zoom_level, width, height)
            # 蓝色圆点表示地铁站
            radius = 6
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(0, 0, 255))
            
            # 绘制站点名称
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except:
                font = ImageFont.load_default()
            
            draw.text((x + 8, y - 8), station["name"], fill=(0, 0, 255), font=font)
        
        # 绘制公交站
        for station in traffic_info["bus_stations"]:
            x, y = self._latlng_to_pixel(station["lat"], station["lng"], 
                                       center_lat, center_lng, zoom_level, width, height)
            # 绿色圆点表示公交站
            radius = 4
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(0, 255, 0))
            
            # 绘制站点名称
            try:
                font = ImageFont.truetype("arial.ttf", 9)
            except:
                font = ImageFont.load_default()
            
            draw.text((x + 6, y - 6), station["name"], fill=(0, 128, 0), font=font)
    
    def _draw_title(self, draw: ImageDraw.Draw, court_name: str, address: str, width: int, height: int):
        """绘制标题"""
        try:
            title_font = ImageFont.truetype("arial.ttf", 16)
            subtitle_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # 绘制标题背景
        title_height = 60
        draw.rectangle([0, 0, width, title_height], fill=(255, 255, 255))
        draw.line([(0, title_height), (width, title_height)], fill=(200, 200, 200), width=2)
        
        # 绘制场馆名称
        draw.text((10, 10), court_name, fill=(0, 0, 0), font=title_font)
        
        # 绘制地址
        if address:
            draw.text((10, 35), address, fill=(100, 100, 100), font=subtitle_font)
        
        # 绘制图例
        legend_y = height - 80
        draw.text((10, legend_y), "● 场馆", fill=(255, 0, 0), font=subtitle_font)
        draw.text((100, legend_y), "● 地铁站", fill=(0, 0, 255), font=subtitle_font)
        draw.text((200, legend_y), "● 公交站", fill=(0, 255, 0), font=subtitle_font) 