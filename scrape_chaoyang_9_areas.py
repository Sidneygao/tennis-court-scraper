#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朝阳区9个区域网球场馆爬取脚本
目标：580家场馆
"""
import json
import time
import sqlite3
from datetime import datetime
from app.scrapers.amap_scraper import AmapScraper
from app.config import settings

# 朝阳区9个区域定义 - 适配现有配置格式
CHAOYANG_AREAS = {
    "guomao": {
        "name": "国贸CBD核心区",
        "center": "116.4500,39.9080",
        "radius": 5000
    },
    "sanlitun": {
        "name": "三里屯-工体时尚区", 
        "center": "116.4550,39.9380",
        "radius": 4000
    },
    "wangjing": {
        "name": "望京科技商务区",
        "center": "116.4800,39.9900",
        "radius": 5000
    },
    "aoyuncun": {
        "name": "奥运村-亚运村文体区",
        "center": "116.3900,40.0000", 
        "radius": 6000
    },
    "chaoyangpark": {
        "name": "朝阳公园-蓝色港湾生态区",
        "center": "116.4700,39.9300",
        "radius": 4000
    },
    "dawanglu": {
        "name": "大望路-华贸商业区", 
        "center": "116.4800,39.9000",
        "radius": 4000
    },
    "shuangjing": {
        "name": "双井-富力城居住区",
        "center": "116.4600,39.8900",
        "radius": 4000
    },
    "gaobeidian": {
        "name": "高碑店-传媒文化区",
        "center": "116.5200,39.9100",
        "radius": 5000
    },
    "dongba": {
        "name": "东坝-第四使馆区",
        "center": "116.5400,39.9200",
        "radius": 5000
    }
}

def main():
    print("🏆 开始爬取朝阳区9个区域网球场馆...")
    print(f"目标：580家场馆")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查API密钥
    if not settings.amap_api_key:
        print("❌ 错误：未配置高德地图API密钥")
        print("请在 .env 文件中设置 AMAP_API_KEY")
        return
    
    # 初始化爬虫
    scraper = AmapScraper()
    
    # 存储所有结果
    all_courts = []
    area_stats = {}
    
    # 遍历每个区域
    for area_code, area_info in CHAOYANG_AREAS.items():
        print(f"\n📍 正在爬取 {area_info['name']} ({area_code})...")
        
        try:
            # 使用现有的搜索方法
            courts = scraper.search_tennis_courts(area_code)
            
            # 转换为标准格式
            formatted_courts = []
            for court in courts:
                formatted_court = {
                    'name': court.name,
                    'address': court.address,
                    'latitude': court.latitude,
                    'longitude': court.longitude,
                    'phone': court.phone,
                    'business_hours': court.business_hours,
                    'description': court.description,
                    'area': area_code,
                    'area_name': area_info['name'],
                    'data_source': 'amap_chaoyang_9_areas',
                    'scraped_at': datetime.now().isoformat()
                }
                formatted_courts.append(formatted_court)
            
            area_stats[area_code] = {
                'name': area_info['name'],
                'count': len(formatted_courts),
                'courts': formatted_courts
            }
            
            all_courts.extend(formatted_courts)
            
            print(f"  ✅ {area_info['name']} 完成，共 {len(formatted_courts)} 个场馆")
            
        except Exception as e:
            print(f"  ❌ {area_info['name']} 爬取失败: {e}")
            continue
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存到JSON文件
    output_file = f'chaoyang_9_areas_courts_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_count': len(all_courts),
            'area_stats': area_stats,
            'courts': all_courts
        }, f, ensure_ascii=False, indent=2)
    
    # 保存到数据库
    save_to_database(all_courts)
    
    # 输出统计
    print(f"\n📊 爬取完成统计:")
    print(f"总场馆数: {len(all_courts)}")
    for area_code, stats in area_stats.items():
        print(f"  {stats['name']}: {stats['count']} 个")
    
    print(f"\n💾 数据已保存到:")
    print(f"  JSON: {output_file}")
    print(f"  数据库: data/courts.db")

def save_to_database(courts):
    """保存到数据库"""
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 清空现有数据（保留结构）
    cursor.execute("DELETE FROM tennis_courts")
    cursor.execute("DELETE FROM court_details")
    
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
            datetime.now()
        ))
        
        court_id = cursor.lastrowid
        
        # 插入详情表 - 只插入实际存在的字段
        cursor.execute("""
            INSERT INTO court_details (
                court_id, created_at
            ) VALUES (?, ?)
        """, (
            court_id,
            datetime.now()
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ 已保存 {len(courts)} 个场馆到数据库")

if __name__ == "__main__":
    main() 