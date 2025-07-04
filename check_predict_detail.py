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
        # 输出predict_prices字段全部内容
        if detail.predict_prices:
            print("\n【predict_prices 字段内容】")
            try:
                predict = json.loads(detail.predict_prices)
                print(json.dumps(predict, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"解析predict_prices失败: {e}")
        else:
            print('predict_prices字段为空')
        # 输出bing_prices字段全部内容
        if detail.bing_prices:
            print("\n【bing_prices 字段内容】")
            try:
                bing = json.loads(detail.bing_prices)
                print(json.dumps(bing, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"解析bing_prices失败: {e}")
        else:
            print('bing_prices字段为空')
    finally:
        db.close()

if __name__ == '__main__':
    main() 