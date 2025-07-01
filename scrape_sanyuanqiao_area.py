#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门爬取三元桥-太阳宫国际生活区的网球场馆
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.amap_scraper import AmapScraper
from app.database import SessionLocal
from app.models import TennisCourt
from datetime import datetime

def main():
    print("🌉 开始爬取三元桥-太阳宫国际生活区网球场馆...")
    scraper = AmapScraper()
    db = SessionLocal()
    total_found = 0
    total_added = 0
    try:
        results = scraper.search_tennis_courts('sanyuanqiao')
        print(f"  找到 {len(results)} 个结果")
        for court_data in results:
            total_found += 1
            existing = db.query(TennisCourt).filter(
                TennisCourt.name == court_data.name
            ).first()
            if existing:
                print(f"    ⚠️  已存在: {court_data.name}")
                continue
            new_court = TennisCourt(
                name=court_data.name,
                address=court_data.address or '',
                longitude=court_data.longitude,
                latitude=court_data.latitude,
                area='sanyuanqiao',
                data_source='amap_sanyuanqiao',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(new_court)
            total_added += 1
            print(f"    ✅ 新增: {court_data.name}")
        db.commit()
        print(f"\n📊 爬取完成!")
        print(f"  总找到: {total_found} 个场馆")
        print(f"  新增: {total_added} 个场馆")
        sanyuanqiao_count = db.query(TennisCourt).filter(
            TennisCourt.area == 'sanyuanqiao'
        ).count()
        print(f"  三元桥区域总场馆数: {sanyuanqiao_count}")
    except Exception as e:
        print(f"❌ 爬取过程中出错: {e}")
        db.rollback()
    finally:
        db.close()
    print(f"\n✅ 三元桥区域爬取完成!")

if __name__ == "__main__":
    main() 