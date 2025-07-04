#!/usr/bin/env python3
from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def main():
    db = SessionLocal()
    try:
        court = db.query(TennisCourt).filter(TennisCourt.name.like('%WoowTennis%国贸%')).first()
        if not court:
            print('未找到目标场馆')
            return
        print(f"场馆: {court.name}")
        print(f"地址: {court.address}")
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail:
            print('无详情数据')
            return
        fields = ['merged_prices', 'predict_prices', 'bing_prices', 'dianping_prices', 'meituan_prices', 'prices']
        found = False
        for field in fields:
            value = getattr(detail, field, None)
            if not value:
                continue
            try:
                data = json.loads(value)
            except:
                continue
            # 统一处理list和dict
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if '82' in str(v):
                                print(f"字段: {field} 第{i+1}项 {k}: {v}")
                                found = True
                    elif '82' in str(item):
                        print(f"字段: {field} 第{i+1}项: {item}")
                        found = True
            elif isinstance(data, dict):
                for k, v in data.items():
                    if '82' in str(v):
                        print(f"字段: {field} {k}: {v}")
                        found = True
            elif '82' in str(data):
                print(f"字段: {field}: {data}")
                found = True
        if not found:
            print('未在所有价格相关字段中找到82元')
    finally:
        db.close()

if __name__ == '__main__':
    main() 