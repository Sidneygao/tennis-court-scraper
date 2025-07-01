from app.database import SessionLocal
from app.models import CourtDetail
import sqlite3
import json

def clear_details():
    session = SessionLocal()
    session.query(CourtDetail).delete()
    session.commit()
    session.close()
    print("已清空court_details表")

def clear_invalid_merged_prices():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT court_id, merged_prices, dianping_prices, meituan_prices FROM court_details WHERE merged_prices IS NOT NULL AND merged_prices != ''")
    rows = cursor.fetchall()
    cleared = 0
    for cid, merged, dianping, meituan in rows:
        # 只要dianping_prices和meituan_prices都为空或无效，merged_prices就清空
        is_real = False
        for src in [dianping, meituan]:
            try:
                prices = json.loads(src) if src else []
            except:
                prices = []
            if isinstance(prices, list) and any(p.get('price') for p in prices):
                is_real = True
                break
        if not is_real:
            cursor.execute("UPDATE court_details SET merged_prices='' WHERE court_id=?", (cid,))
            cleared += 1
    conn.commit()
    print(f"已强制清空无真实渠道支撑的merged_prices字段，共{cleared}条")
    conn.close()

if __name__ == "__main__":
    clear_details()
    clear_invalid_merged_prices() 