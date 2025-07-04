#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将所有场馆的predict_prices同步写入merged_prices字段，标记为预测，便于前端显示。
"""
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
from datetime import datetime

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).all()
    total = len(courts)
    updated = 0
    skipped = 0
    for i, court in enumerate(courts, 1):
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail:
            continue
        merged = []
        if detail.merged_prices:
            try:
                merged = json.loads(detail.merged_prices)
            except:
                merged = []
        # 检查是否有原始爬取价格（点评/美团/真实）
        has_real = False
        for item in merged:
            src = str(item.get('source', ''))
            if any(x in src for x in ['点评', '美团', '真实']):
                has_real = True
                break
        if has_real:
            skipped += 1
            continue  # 有真实价格，保留不覆盖
        # 强制覆盖：无论原有内容，只要没有真实价格就写入预测
        predict = []
        if detail.predict_prices:
            try:
                p = json.loads(detail.predict_prices)
                # 兼容多种结构
                if isinstance(p, list):
                    predict = p
                elif isinstance(p, dict):
                    # 结构如 {'peak_price': 200, ...}
                    for k, v in p.items():
                        if 'price' in k and v:
                            predict.append({
                                'type': k,
                                'price': v,
                                'is_predicted': True,
                                'source': '预测'
                            })
            except:
                predict = []
        if predict:
            detail.merged_prices = json.dumps(predict, ensure_ascii=False)
            updated += 1
        else:
            skipped += 1
        if i % 20 == 0:
            print(f"进度: {i}/{total}")
    db.commit()
    print(f"共处理{total}个场馆，覆盖写入{updated}，跳过{skipped}（含真实价格或无预测）")

if __name__ == '__main__':
    main() 