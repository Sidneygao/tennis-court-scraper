import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.config import settings
from app.models import TennisCourt
from app.database import get_db

# 合法区域
valid_areas = set(settings.target_areas.keys())
def main():
    db = next(get_db())
    print("--- 修复前统计 ---")
    print("所有 area:", db.query(TennisCourt.area).distinct().all())
    print("非法 area:", db.query(TennisCourt).filter(~TennisCourt.area.in_(valid_areas)).count())
    print("空/无效 data_source:", db.query(TennisCourt).filter((TennisCourt.data_source == None) | (TennisCourt.data_source == '')).count())

    # 修复非法 area
    courts = db.query(TennisCourt).filter(~TennisCourt.area.in_(valid_areas)).all()
    for court in courts:
        print(f"修正场馆ID {court.id} 的 area: {court.area} -> wangjing")
        court.area = 'wangjing'
    # 修复空/无效 data_source
    courts = db.query(TennisCourt).filter((TennisCourt.data_source == None) | (TennisCourt.data_source == '')).all()
    for court in courts:
        print(f"修正场馆ID {court.id} 的 data_source: {court.data_source} -> amap")
        court.data_source = 'amap'
    db.commit()

    print("--- 修复后统计 ---")
    print("所有 area:", db.query(TennisCourt.area).distinct().all())
    print("非法 area:", db.query(TennisCourt).filter(~TennisCourt.area.in_(valid_areas)).count())
    print("空/无效 data_source:", db.query(TennisCourt).filter((TennisCourt.data_source == None) | (TennisCourt.data_source == '')).count())

if __name__ == "__main__":
    main() 