#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.scrapers.detail_scraper import DetailScraper
import json

def test_optimized_xiaohongshu():
    """测试优化后的小红书爬虫"""
    scraper = DetailScraper()
    
    # 测试场馆列表
    test_courts = [
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆", 
        "球星网球汇(合生汇球星运动中心店)",
        "乾坤体育网球学练馆(望京SOHOT1商场店)"
    ]
    
    print("🎾 优化后小红书爬虫测试")
    print("=" * 60)
    
    results = []
    
    for i, court_name in enumerate(test_courts, 1):
        print(f"\n{i}. 测试场馆: {court_name}")
        print("-" * 40)
        
        try:
            # 直接调用小红书爬虫
            xiaohongshu_data = scraper.scrape_xiaohongshu(court_name)
            
            if xiaohongshu_data:
                print("✅ 小红书数据获取成功:")
                print(f"   描述: {xiaohongshu_data.get('description', '无')}")
                print(f"   评分: {xiaohongshu_data.get('rating', '无')}")
                print(f"   评论数: {xiaohongshu_data.get('review_count', '无')}")
                print(f"   营业时间: {xiaohongshu_data.get('business_hours', '无')}")
                print(f"   设施: {xiaohongshu_data.get('facilities', '无')}")
                print(f"   价格: {len(xiaohongshu_data.get('prices', []))} 项")
                print(f"   评论: {len(xiaohongshu_data.get('reviews', []))} 条")
                print(f"   图片: {len(xiaohongshu_data.get('images', []))} 张")
                
                # 显示评论内容
                if xiaohongshu_data.get('reviews'):
                    print("   评论内容:")
                    for j, review in enumerate(xiaohongshu_data['reviews'][:2], 1):
                        print(f"     {j}. {review['content'][:100]}...")
                
                # 显示价格信息
                if xiaohongshu_data.get('prices'):
                    print("   价格信息:")
                    for j, price in enumerate(xiaohongshu_data['prices'][:2], 1):
                        print(f"     {j}. {price['type']}: {price['price']}")
                
                results.append({
                    "court": court_name,
                    "status": "成功",
                    "data": xiaohongshu_data
                })
            else:
                print("❌ 小红书数据获取失败")
                results.append({
                    "court": court_name,
                    "status": "失败",
                    "data": None
                })
                
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            results.append({
                "court": court_name,
                "status": "错误",
                "error": str(e)
            })
    
    # 统计结果
    print(f"\n📊 测试结果统计")
    print("=" * 60)
    success_count = len([r for r in results if r["status"] == "成功"])
    total_count = len(results)
    
    print(f"总测试场馆: {total_count}")
    print(f"成功获取数据: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 数据质量分析
    if success_count > 0:
        print(f"\n📈 数据质量分析")
        print("-" * 40)
        
        successful_results = [r for r in results if r["status"] == "成功"]
        
        # 统计各字段的获取情况
        fields = ["description", "rating", "review_count", "business_hours", 
                 "facilities", "prices", "reviews", "images"]
        
        for field in fields:
            field_count = 0
            for result in successful_results:
                data = result["data"]
                if data.get(field):
                    if isinstance(data[field], list):
                        if len(data[field]) > 0:
                            field_count += 1
                    else:
                        field_count += 1
            
            print(f"{field}: {field_count}/{success_count} ({field_count/success_count*100:.1f}%)")
    
    # 保存详细结果到文件
    with open("xiaohongshu_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果已保存到: xiaohongshu_test_results.json")
    
    return results

if __name__ == "__main__":
    test_optimized_xiaohongshu() 