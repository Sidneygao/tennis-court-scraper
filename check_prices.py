#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.database import SessionLocal
from app.models import TennisCourt

def check_prices():
    db = SessionLocal()
    try:
        courts = db.query(TennisCourt).limit(5).all()
        print("=== 价格数据检查 ===")
        for court in courts:
            print(f"场馆: {court.name}")
            print(f"  黄金时间: {court.peak_price}")
            print(f"  非黄金时间: {court.off_peak_price}")
            print(f"  会员价: {court.member_price}")
            print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    check_prices() 