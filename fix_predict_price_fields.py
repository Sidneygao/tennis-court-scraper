from app.database import get_db
from app.models import CourtDetail
import json

def fix_predict_fields():
    db = next(get_db())
    count = 0
    for d in db.query(CourtDetail).all():
        changed = False
        # 修正 merged_prices
        if d.merged_prices:
            try:
                prices = json.loads(d.merged_prices)
                if isinstance(prices, list):
                    for p in prices:
                        if p.get('is_predicted'):
                            if p.get('source') != '预测':
                                p['source'] = '预测'
                                changed = True
                    if changed:
                        d.merged_prices = json.dumps(prices, ensure_ascii=False)
            except Exception:
                pass
        # 修正 predict_prices
        if d.predict_prices:
            try:
                pred = json.loads(d.predict_prices)
                if isinstance(pred, dict):
                    if pred.get('peak_price') or pred.get('off_peak_price'):
                        if pred.get('predict_method') != '邻域分位数加权法':
                            pred['predict_method'] = '邻域分位数加权法'
                            changed = True
                    if changed:
                        d.predict_prices = json.dumps(pred, ensure_ascii=False)
            except Exception:
                pass
        if changed:
            count += 1
    db.commit()
    db.close()
    print(f'已修正 {count} 条记录')

if __name__ == '__main__':
    fix_predict_fields() 