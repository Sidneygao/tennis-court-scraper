from app.database import get_db
from app.models import TennisCourt

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).limit(5).all()
    for c in courts:
        print(f"{c.name} | 价格: {c.peak_price}")

if __name__ == '__main__':
    main() 