from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json

db = next(get_db())
court = db.query(TennisCourt).filter(TennisCourt.name == '大富网球俱乐部(4、7号场地)').first()

if court:
    print(f"场馆ID: {court.id}")
    print(f"场馆名称: {court.name}")
    print(f"当前区域: {court.area}")
    print(f"当前坐标: {court.latitude}, {court.longitude}")
    print(f"地址: {court.address}")
    
    # 检查当前类型判断
    predictor = PricePredictor()
    current_type = predictor.determine_court_type(court.name, court.address)
    print(f"当前类型判断: {current_type}")
    
    # 检查当前预测价格
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
    if detail and detail.predict_prices:
        print(f"\n=== 当前预测价格 ===")
        current_predict = json.loads(detail.predict_prices)
        print(json.dumps(current_predict, ensure_ascii=False, indent=2))
    else:
        print(f"\n❌ 未找到预测价格数据")
    
    # 重新预测价格
    print(f"\n=== 重新预测价格 ===")
    new_predict = predictor.predict_price_for_court(court)
    if new_predict:
        print(json.dumps(new_predict, ensure_ascii=False, indent=2))
        
        # 更新数据库
        if detail:
            detail.predict_prices = json.dumps(new_predict, ensure_ascii=False)
            db.commit()
            print(f"\n✅ 预测结果已更新到数据库")
        else:
            # 创建详情记录
            detail = CourtDetail(court_id=court.id)
            detail.predict_prices = json.dumps(new_predict, ensure_ascii=False)
            db.add(detail)
            db.commit()
            print(f"\n✅ 预测结果已保存到数据库")
    else:
        print("❌ 预测失败")
else:
    print("❌ 未找到大富网球俱乐部(4、7号场地)") 