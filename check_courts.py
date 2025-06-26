#!/usr/bin/env python3
"""
检查场馆数据
"""

from app.database import get_db
from app.models import TennisCourt

def main():
    """主函数"""
    try:
        db = next(get_db())
        
        # 检查场馆总数
        total_courts = db.query(TennisCourt).count()
        print(f"场馆总数: {total_courts}")
        
        if total_courts == 0:
            print("❌ 数据库中没有场馆数据")
            print("需要运行场馆抓取脚本")
            return
        
        # 显示前10个场馆
        print("\n前10个场馆:")
        courts = db.query(TennisCourt).limit(10).all()
        for court in courts:
            print(f"  {court.id}: {court.name} - {court.address}")
        
        # 检查区域分布
        print("\n区域分布:")
        areas = db.query(TennisCourt.area).distinct().all()
        for area in areas:
            if area[0]:
                count = db.query(TennisCourt).filter(TennisCourt.area == area[0]).count()
                print(f"  {area[0]}: {count}个场馆")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    main() 