from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
import time
from datetime import datetime

def recalculate_all_predictions():
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取所有场馆
    all_courts = db.query(TennisCourt).all()
    total_courts = len(all_courts)
    
    print(f"开始重新计算所有场馆预测价格...")
    print(f"总场馆数: {total_courts}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    success_count = 0
    failed_count = 0
    failed_courts = []
    
    start_time = time.time()
    
    for i, court in enumerate(all_courts, 1):
        try:
            print(f"[{i}/{total_courts}] 处理: {court.name} (ID: {court.id})")
            
            # 检查类型判断
            court_type = predictor.determine_court_type(court.name, court.address)
            print(f"  类型: {court_type}")
            
            # 重新预测价格
            new_predict = predictor.predict_price_for_court(court)
            
            if new_predict:
                # 更新或创建详情记录
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if detail:
                    detail.predict_prices = json.dumps(new_predict, ensure_ascii=False)
                else:
                    detail = CourtDetail(court_id=court.id)
                    detail.predict_prices = json.dumps(new_predict, ensure_ascii=False)
                    db.add(detail)
                
                success_count += 1
                if 'peak_price' in new_predict and new_predict['peak_price']:
                    print(f"  ✅ 成功 - 黄金: {new_predict.get('peak_price')}元, 非黄金: {new_predict.get('off_peak_price')}元")
                else:
                    print(f"  ⚠️  预测失败 - {new_predict.get('reason', '未知原因')}")
            else:
                failed_count += 1
                failed_courts.append({
                    'id': court.id,
                    'name': court.name,
                    'area': court.area,
                    'type': court_type
                })
                print(f"  ❌ 失败")
                
        except Exception as e:
            failed_count += 1
            failed_courts.append({
                'id': court.id,
                'name': court.name,
                'area': court.area,
                'error': str(e)
            })
            print(f"  ❌ 异常: {str(e)}")
    
    # 提交所有更改
    db.commit()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("-" * 60)
    print(f"重新计算完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"执行时间: {execution_time:.2f}秒")
    print(f"成功: {success_count}个场馆")
    print(f"失败: {failed_count}个场馆")
    print(f"成功率: {success_count/total_courts*100:.1f}%")
    
    if failed_courts:
        print(f"\n失败场馆列表:")
        for court in failed_courts:
            print(f"  - {court['name']} (ID: {court['id']}, 区域: {court['area']})")
            if 'error' in court:
                print(f"    错误: {court['error']}")
            if 'type' in court:
                print(f"    类型: {court['type']}")
    
    # 保存结果到文件
    result_data = {
        'execution_time': execution_time,
        'total_courts': total_courts,
        'success_count': success_count,
        'failed_count': failed_count,
        'success_rate': success_count/total_courts*100,
        'failed_courts': failed_courts,
        'timestamp': datetime.now().isoformat()
    }
    
    filename = f"batch_recalculate_results_final_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {filename}")

if __name__ == "__main__":
    recalculate_all_predictions() 