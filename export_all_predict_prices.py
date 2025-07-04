from app.database import get_db
from app.models import CourtDetail

def main():
    db = next(get_db())
    for d in db.query(CourtDetail).all():
        print(f'id: {d.id}, predict_prices: {d.predict_prices}')
    db.close()

if __name__ == '__main__':
    main() 