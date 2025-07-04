from app.database import get_db
from app.models import TennisCourt, CourtDetail

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).all()
    count = 0
    for c in courts:
        exists = db.query(CourtDetail).filter(CourtDetail.court_id == c.id).first()
        if not exists:
            db.add(CourtDetail(court_id=c.id))
            count += 1
    db.commit()
    print(f"已补全 {count} 条 CourtDetail 记录")
    db.close()

if __name__ == "__main__":
    main() 