from app.database import SessionLocal
from app.models import CourtDetail

def clear_details():
    session = SessionLocal()
    session.query(CourtDetail).delete()
    session.commit()
    session.close()
    print("已清空court_details表")

if __name__ == "__main__":
    clear_details() 