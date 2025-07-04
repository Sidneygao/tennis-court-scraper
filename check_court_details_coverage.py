from app.database import get_db
from app.models import TennisCourt, CourtDetail

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).all()
    details = db.query(CourtDetail).all()
    detail_ids = set(d.court_id for d in details)
    no_detail = [c for c in courts if c.id not in detail_ids]
    print(f"TennisCourt总数: {len(courts)}")
    print(f"CourtDetail总数: {len(details)}")
    print(f"无详情的场馆数量: {len(no_detail)}")
    if no_detail:
        print("无详情场馆id和名称:")
        for c in no_detail:
            print(f"id: {c.id}, name: {c.name}")
    db.close()

if __name__ == '__main__':
    main() 