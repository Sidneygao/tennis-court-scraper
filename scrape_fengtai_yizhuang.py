#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
丰台区和亦庄网球场馆爬取脚本
目标：丰台区100家，亦庄40家
"""
import json
import time
import sqlite3
from datetime import datetime
from app.scrapers.amap_scraper import AmapScraper
from app.config import settings

# 丰台区和亦庄区域定义 - 需要添加到配置中
AREAS = {
    "fengtai_east": {
        "name": "丰台区东部",
        "center": "116.2800,39.8600",
        "radius": 8000
    },
    "fengtai_west": {
        "name": "丰台区西部", 
        "center": "116.2200,39.8600",
        "radius": 8000
    },
    "yizhuang": {
        "name": "亦庄经济技术开发区",
        "center": "116.5000,39.8000", 
        "radius": 6000
    }
}

def add_areas_to_config():
    """将新区域添加到配置中"""
    # 临时添加区域配置
    for area_code, area_config in AREAS.items():
        if area_code not in settings.target_areas:
            settings.target_areas[area_code] = area_config

def scrape_areas():
    """爬取丰台区和亦庄的网球场馆"""
    print("🎾 开始爬取丰台区和亦庄网球场馆...")
    
    # 添加区域配置
    add_areas_to_config()
    
    scraper = AmapScraper()
    all_courts = []
    
    for area_code, area_config in AREAS.items():
        print(f"\n📍 正在爬取 {area_config['name']}...")
        
        try:
            # 使用高德API搜索网球场馆
            courts = scraper.search_tennis_courts(area_code)
            
            # 转换为字典格式并添加区域信息
            court_dicts = []
            for court in courts:
                court_dict = {
                    'name': court.name,
                    'address': court.address or '',
                    'latitude': court.latitude or 0,
                    'longitude': court.longitude or 0,
                    'phone': court.phone or '',
                    'business_hours': court.business_hours or '',
                    'area': area_code,
                    'area_name': area_config['name'],
                    'data_source': 'amap_fengtai_yizhuang',
                    'created_at': datetime.now().isoformat()
                }
                court_dicts.append(court_dict)
            
            print(f"✅ {area_config['name']}: 找到 {len(court_dicts)} 个场馆")
            all_courts.extend(court_dicts)
            
            # 避免API限制
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ {area_config['name']} 爬取失败: {e}")
            continue
    
    print(f"\n📊 总计爬取到 {len(all_courts)} 个场馆")
    return all_courts

def save_to_database(courts):
    """保存到数据库"""
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 不清空现有数据，只添加新数据
    print(f"💾 正在保存 {len(courts)} 个场馆到数据库...")
    
    for court in courts:
        # 插入主表
        cursor.execute("""
            INSERT INTO tennis_courts (
                name, address, latitude, longitude, area, area_name,
                phone, business_hours, data_source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            court['name'],
            court.get('address', ''),
            court.get('latitude', 0),
            court.get('longitude', 0),
            court.get('area', ''),
            court.get('area_name', ''),
            court.get('phone', ''),
            court.get('business_hours', ''),
            court.get('data_source', ''),
            court.get('created_at', '')
        ))
        
        court_id = cursor.lastrowid
        
        # 插入详情表
        cursor.execute("""
            INSERT INTO court_details (
                court_id, created_at
            ) VALUES (?, ?)
        """, (
            court_id,
            court.get('created_at', '')
        ))
    
    conn.commit()
    conn.close()
    print("✅ 数据保存完成")

def save_to_json(courts):
    """保存到JSON文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fengtai_yizhuang_courts_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(courts, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据已保存到 {filename}")

def main():
    """主函数"""
    print("🚀 丰台区和亦庄网球场馆爬取开始")
    print("=" * 50)
    
    # 爬取数据
    courts = scrape_areas()
    
    if not courts:
        print("❌ 没有爬取到任何数据")
        return
    
    # 保存数据
    save_to_json(courts)
    save_to_database(courts)
    
    # 统计结果
    area_stats = {}
    for court in courts:
        area = court.get('area', 'unknown')
        area_stats[area] = area_stats.get(area, 0) + 1
    
    print("\n📈 爬取结果统计:")
    for area, count in area_stats.items():
        area_name = next((config['name'] for code, config in AREAS.items() if code == area), area)
        print(f"  {area_name}: {count} 个场馆")
    
    print(f"\n🎉 丰台区和亦庄爬取完成！总计 {len(courts)} 个场馆")

if __name__ == "__main__":
    main() 