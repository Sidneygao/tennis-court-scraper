from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail

db = SessionLocal()
courts_count = db.query(TennisCourt).count()
details_count = db.query(CourtDetail).count()
db.close()

print(f"场馆总数: {courts_count}")
print(f"详情缓存数: {details_count}") 