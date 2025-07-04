from app.database import get_db
from app.models import TennisCourt

def main():
    db = next(get_db())
    count = db.query(TennisCourt).count()
    print(f'TennisCourt 总数: {count}')
    db.close()

if __name__ == '__main__':
    main() 