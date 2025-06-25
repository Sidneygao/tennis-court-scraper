from app.database import get_db
from app.models import TennisCourt

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).filter(TennisCourt.name.like('%测试场馆%')).all()
    for c in courts:
        print(f"删除: {c.name}")
        db.delete(c)
    db.commit()
    print('已删除DUMMY测试场馆')

if __name__ == '__main__':
    main() 