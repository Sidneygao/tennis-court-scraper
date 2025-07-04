from app.database import get_db
from app.models import CourtDetail
import json

def fix_bing_fields():
    db = next(get_db())
    count = 0
    for d in db.query(CourtDetail).all():
        changed = False
        if d.merged_prices:
            try:
                prices = json.loads(d.merged_prices)
                if isinstance(prices, list):
                    for p in prices:
                        if p.get('source') == 'BING_PROCESSED':
                            p['source'] = 'BING融合价'
                            changed = True
                    if changed:
                        d.merged_prices = json.dumps(prices, ensure_ascii=False)
            except Exception:
                pass
        if changed:
            count += 1
    db.commit()
    db.close()
    print(f'已修正BING融合价 {count} 条记录')

if __name__ == '__main__':
    fix_bing_fields() 