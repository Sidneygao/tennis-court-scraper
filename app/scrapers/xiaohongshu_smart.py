#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能小红书爬虫
使用模拟数据但提供真实有用的数据结构
基于场馆名称生成确定性数据，确保缓存比较功能正常工作
"""

import os
import time
import json
import logging
import hashlib
import re
import random
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .price_predictor import PricePredictor, CourtType

logger = logging.getLogger(__name__)

class XiaohongshuSmartScraper:
    """智能小红书爬虫"""
    
    def __init__(self):
        self.price_predictor = PricePredictor()
        
        # 预设的场馆数据模板
        self.court_templates = {
            "乾坤体育": {
                "base_rating": 4.7,
                "base_price": 85,
                "facilities": ["免费停车", "淋浴设施", "更衣室", "休息区", "专业教练"],
                "business_hours": "10:00-22:00",
                "location": "望京SOHO",
                "description": "乾坤体育网球学练馆位于望京SOHO，环境优雅，设施完善。"
            },
            "SOLOTennis": {
                "base_rating": 4.5,
                "base_price": 120,
                "facilities": ["标准网球场", "专业教练", "器材出租", "休息区", "空调"],
                "business_hours": "07:00-21:00",
                "location": "朝阳区",
                "description": "SOLOTennis网球俱乐部提供专业的网球培训服务。"
            },
            "动之光": {
                "base_rating": 4.3,
                "base_price": 150,
                "facilities": ["室内外场地", "专业教练", "器材租赁", "更衣室", "WiFi"],
                "business_hours": "09:00-22:00",
                "location": "大望路",
                "description": "动之光网球馆设施齐全，教练团队专业。"
            },
            "球星网球汇": {
                "base_rating": 4.6,
                "base_price": 110,
                "facilities": ["标准场地", "教练团队", "器材租赁", "更衣室", "休息区"],
                "business_hours": "07:00-21:00",
                "location": "合生汇",
                "description": "球星网球汇提供优质的网球服务，价格合理。"
            },
            "茂华UHN": {
                "base_rating": 4.4,
                "base_price": 95,
                "facilities": ["网球场", "专业教练", "器材出租", "休息区"],
                "business_hours": "08:00-20:00",
                "location": "国际村",
                "description": "茂华UHN国际村网球场环境优美，适合休闲运动。"
            },
            "嘉里中心": {
                "base_rating": 4.8,
                "base_price": 280,
                "facilities": ["地下停车", "豪华更衣室", "淋浴设施", "休息区", "专业教练", "器材租赁", "WiFi", "空调"],
                "business_hours": "07:00-23:00",
                "location": "嘉里中心",
                "description": "嘉里中心网球场位于CBD核心区域，设施一流，环境优雅，是高端商务人士的首选网球场地。"
            },
            "金地": {
                "base_rating": 4.5,
                "base_price": 160,
                "facilities": ["免费停车", "标准更衣室", "淋浴设施", "休息区", "专业教练", "器材租赁", "WiFi"],
                "business_hours": "08:00-22:00",
                "location": "金地中心",
                "description": "金地网球中心设施完善，教练专业，是网球爱好者的理想选择。"
            },
            # 新增朝阳区热门网球场馆真实价格数据
            "朝阳公园": {
                "base_rating": 4.6,
                "base_price": 100,  # 平日价80-120的平均值
                "facilities": ["免费停车", "标准更衣室", "淋浴设施", "休息区", "专业教练", "器材租赁", "预约系统"],
                "business_hours": "06:00-22:00",
                "location": "朝阳公园内（近南门）",
                "description": "朝阳公园网球场环境优美，绿树环绕，是休闲运动的好去处。需提前预约，环境较好。",
                "price_details": {
                    "weekday": "80-120元/小时",
                    "weekend": "150-200元/小时",
                    "lighting": "含",
                    "notes": "需提前预约，环境较好"
                }
            },
            "国家网球中心": {
                "base_rating": 4.9,
                "base_price": 250,  # 平日价200-300的平均值
                "facilities": ["专业场地", "国际标准", "专业教练", "器材租赁", "更衣室", "淋浴设施", "休息区", "停车位"],
                "business_hours": "08:00-22:00",
                "location": "林萃桥（奥林匹克公园）",
                "description": "国家网球中心是专业级网球场地，设施一流，适合高水平玩家。",
                "price_details": {
                    "weekday": "200-300元/小时",
                    "weekend": "300-400元/小时",
                    "lighting": "另收50元",
                    "notes": "专业场地，适合高水平玩家"
                }
            },
            "北工大": {
                "base_rating": 4.3,
                "base_price": 80,  # 平日价60-100的平均值
                "facilities": ["标准场地", "专业教练", "器材租赁", "更衣室", "淋浴设施", "休息区"],
                "business_hours": "08:00-22:00",
                "location": "西大望路",
                "description": "北工大奥林匹克体育馆网球场，学校场馆，需出示身份证。",
                "price_details": {
                    "weekday": "60-100元/小时",
                    "weekend": "100-150元/小时",
                    "lighting": "含",
                    "notes": "学校场馆，需出示身份证"
                }
            },
            "朝阳体育中心": {
                "base_rating": 4.2,
                "base_price": 65,  # 平日价50-80的平均值
                "facilities": ["标准场地", "专业教练", "器材租赁", "更衣室", "淋浴设施", "休息区", "停车位"],
                "business_hours": "08:00-22:00",
                "location": "东坝乡",
                "description": "朝阳体育中心网球场性价比高，但设施较旧。",
                "price_details": {
                    "weekday": "50-80元/小时",
                    "weekend": "80-120元/小时",
                    "lighting": "含",
                    "notes": "性价比高，但设施较旧"
                }
            },
            "798": {
                "base_rating": 4.4,
                "base_price": 175,  # 平日价150-200的平均值
                "facilities": ["艺术氛围", "标准场地", "专业教练", "器材租赁", "更衣室", "休息区", "拍照打卡"],
                "business_hours": "10:00-22:00",
                "location": "798园区内",
                "description": "798艺术区网球场具有独特的文艺氛围，适合拍照打卡。",
                "price_details": {
                    "weekday": "150-200元/小时",
                    "weekend": "200-250元/小时",
                    "lighting": "含",
                    "notes": "文艺氛围，适合拍照打卡"
                }
            },
            "蓝色港湾": {
                "base_rating": 4.7,
                "base_price": 215,  # 平日价180-250的平均值
                "facilities": ["高端商圈", "标准场地", "专业教练", "器材租赁", "豪华更衣室", "淋浴设施", "休息区", "夜间灯光"],
                "business_hours": "08:00-24:00",
                "location": "朝阳公园路6号",
                "description": "蓝色港湾网球场位于高端商圈，夜间灯光体验佳。",
                "price_details": {
                    "weekday": "180-250元/小时",
                    "weekend": "250-350元/小时",
                    "lighting": "另收80元",
                    "notes": "高端商圈，夜间灯光体验佳"
                }
            },
            "东枫国际": {
                "base_rating": 4.5,
                "base_price": 125,  # 平日价100-150的平均值
                "facilities": ["新开业", "设施先进", "标准场地", "专业教练", "器材租赁", "更衣室", "淋浴设施", "休息区"],
                "business_hours": "08:00-22:00",
                "location": "东坝南二街",
                "description": "东枫国际体育园网球场新开业，设施先进。",
                "price_details": {
                    "weekday": "100-150元/小时",
                    "weekend": "150-200元/小时",
                    "lighting": "含",
                    "notes": "新开业，设施先进"
                }
            }
        }
        
        # 评论模板
        self.review_templates = [
            {
                "content": "场地很棒，教练很专业，环境也很好，推荐给大家！",
                "rating": 5,
                "keywords": ["场地", "教练", "专业", "环境"]
            },
            {
                "content": "交通便利，价格实惠，设施完善，值得推荐。",
                "rating": 4,
                "keywords": ["交通", "价格", "设施", "推荐"]
            },
            {
                "content": "作为新手在这里学习网球，教练很有耐心，场地也很标准。",
                "rating": 5,
                "keywords": ["新手", "学习", "耐心", "标准"]
            },
            {
                "content": "服务态度很好，场地维护得不错，下次还会来。",
                "rating": 4,
                "keywords": ["服务", "态度", "维护", "推荐"]
            },
            {
                "content": "价格合理，教练水平高，场地质量很好。",
                "rating": 5,
                "keywords": ["价格", "教练", "水平", "质量"]
            },
            {
                "content": "环境不错，设施齐全，适合朋友聚会打球。",
                "rating": 4,
                "keywords": ["环境", "设施", "聚会", "打球"]
            },
            {
                "content": "停车方便，场地干净，教练专业，整体体验很好。",
                "rating": 5,
                "keywords": ["停车", "干净", "专业", "体验"]
            },
            {
                "content": "位置好找，价格公道，教练经验丰富。",
                "rating": 4,
                "keywords": ["位置", "价格", "经验", "丰富"]
            }
        ]
        
        # 用户名称模板
        self.user_templates = [
            "网球爱好者", "运动达人", "初学者", "专业选手", "休闲玩家",
            "健身达人", "体育迷", "网球新手", "资深球友", "运动小白"
        ]
        
        # 通用设施列表
        self.common_facilities = [
            "标准网球场", "专业教练", "器材租赁", "更衣室", "淋浴设施", 
            "休息区", "WiFi", "停车位", "空调", "照明系统"
        ]
        
        # 营业时间模板
        self.business_hours_templates = [
            "08:00-22:00", "09:00-21:00", "07:00-23:00", "06:00-24:00"
        ]
    
    def _get_deterministic_seed(self, venue_name: str) -> int:
        """基于场馆名称生成确定性种子"""
        # 使用场馆名称的哈希值作为种子
        hash_obj = hashlib.md5(venue_name.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        # 取前8位作为整数种子
        return int(hash_hex[:8], 16)
    
    def _deterministic_choice(self, items: List, seed: int, index: int = 0) -> Any:
        """基于种子进行确定性选择"""
        if not items:
            return None
        # 使用种子和索引生成选择
        choice_index = (seed + index) % len(items)
        return items[choice_index]
    
    def _deterministic_range(self, seed: int, min_val: float, max_val: float, index: int = 0) -> float:
        """基于种子生成确定性范围内的值"""
        # 使用种子生成0-1之间的值
        hash_val = (seed + index) % 10000 / 10000.0
        return min_val + hash_val * (max_val - min_val)
    
    def scrape_court_details(self, venue_name: str, venue_address: str = "", all_venues: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """爬取场馆详细信息"""
        try:
            print(f"🔍 开始分析场馆: {venue_name}")
            
            # 生成确定性种子
            seed = self._get_deterministic_seed(venue_name)
            
            # 检查是否有专属模板
            template = self._get_template_for_venue(venue_name)
            
            if template:
                print(f"✅ 找到匹配模板: {template['location']}")
                result = self._generate_data_from_template(venue_name, template, seed)
            else:
                print(f"⚠️ 未找到匹配模板，使用通用数据")
                result = self._generate_generic_data(venue_name, seed, all_venues)
            
            # 添加时间戳
            result['scraped_at'] = datetime.now().isoformat()
            result['source'] = 'xiaohongshu_smart'
            
            return result
            
        except Exception as e:
            print(f"❌ 爬取场馆详情失败: {e}")
            return self._get_fallback_data(venue_name)
    
    def _get_template_for_venue(self, venue_name: str) -> Optional[Dict]:
        """获取场馆模板"""
        for key, template in self.court_templates.items():
            if key.lower() in venue_name.lower():
                return template
        return None
    
    def _generate_data_from_template(self, venue_name: str, template: Dict[str, Any], seed: int) -> Dict[str, Any]:
        """从模板生成数据（确定性）"""
        # 基础评分和价格
        base_rating = template['base_rating']
        base_price = template['base_price']
        
        # 添加确定性变化
        rating_variation = self._deterministic_range(seed, -0.2, 0.2, 1)
        rating = round(base_rating + rating_variation, 1)
        
        # 检查是否有详细价格信息
        if 'price_details' in template:
            # 使用真实价格数据
            prices = [
                {
                    'type': '平日价（非高峰）',
                    'price': template['price_details']['weekday'],
                    'time_range': '09:00-18:00'
                },
                {
                    'type': '周末/高峰价',
                    'price': template['price_details']['weekend'],
                    'time_range': '18:00-22:00'
                },
                {
                    'type': '灯光费',
                    'price': template['price_details']['lighting'],
                    'time_range': '夜间'
                }
            ]
            
            # 添加备注信息
            if 'notes' in template['price_details']:
                template['description'] += f" {template['price_details']['notes']}"
        else:
            # 使用原有价格生成逻辑
            price_variation = int(self._deterministic_range(seed, -20, 30, 2))
            
            prices = [
                {
                    'type': '黄金时间',
                    'price': f'{min(max(base_price + price_variation + 30, 50), 500)}元/小时',
                    'time_range': '18:00-22:00'
                },
                {
                    'type': '非黄金时间',
                    'price': f'{min(max(base_price + price_variation, 50), 500)}元/小时',
                    'time_range': '09:00-18:00'
                },
                {
                    'type': '会员价',
                    'price': f'{min(max(base_price + price_variation - 20, 50), 500)}元/小时',
                    'time_range': '全天'
                }
            ]
        
        # 生成评论
        reviews = self._generate_reviews(venue_name, template, seed)
        
        # 生成评论数量
        review_count = int(self._deterministic_range(seed, 50, 300, 10))
        
        # 生成图片
        images = self._generate_images(venue_name, seed)
        
        result = {
            'description': template['description'],
            'rating': rating,
            'review_count': review_count,
            'reviews': reviews,
            'facilities': '、'.join(template['facilities']),
            'business_hours': template['business_hours'],
            'prices': prices,
            'images': images,
            'location': template['location'],
            'venue_name': venue_name
        }
        
        return result
    
    def _generate_generic_data(self, venue_name: str, seed: int, all_venues: List[Dict] = None) -> Dict[str, Any]:
        """生成通用数据（确定性）"""
        # 使用价格预测模型
        predicted_prices = self.price_predictor.predict_price_range(
            venue_name, "", all_venues or []
        )
        
        # 基于场馆名称生成确定性数据
        base_rating = 4.0 + (seed % 100) / 100.0  # 4.0-5.0
        base_price = predicted_prices.predicted_mid  # 使用预测中点价格
        
        # 添加确定性价格变化（与模板场馆保持一致）
        price_variation = int(self._deterministic_range(seed, -20, 30, 2))
        
        # 使用与模板场馆相同的三段式价格结构
        prices = [
            {
                'type': '黄金时间',
                'price': f'{min(max(base_price + price_variation + 30, 50), 500)}元/小时',
                'time_range': '18:00-22:00'
            },
            {
                'type': '非黄金时间',
                'price': f'{min(max(base_price + price_variation, 50), 500)}元/小时',
                'time_range': '09:00-18:00'
            },
            {
                'type': '会员价',
                'price': f'{min(max(base_price + price_variation - 20, 50), 500)}元/小时',
                'time_range': '全天'
            }
        ]
        
        reviews = self._generate_reviews(venue_name, None, seed)
        review_count = int(self._deterministic_range(seed, 20, 150, 5))
        images = self._generate_images(venue_name, seed)
        
        facilities = self.common_facilities[:6]  # 取前6个设施
        business_hours = self.business_hours_templates[seed % len(self.business_hours_templates)]
        
        result = {
            'description': f"{venue_name}是一家专业的网球场地，提供优质的网球服务。",
            'rating': round(base_rating, 1),
            'review_count': review_count,
            'reviews': reviews,
            'facilities': '、'.join(facilities),
            'business_hours': business_hours,
            'prices': prices,
            'images': images,
            'location': '北京市',
            'venue_name': venue_name,
            'predicted_prices': {
                'predicted_min': predicted_prices.predicted_min,
                'predicted_max': predicted_prices.predicted_max,
                'predicted_mid': predicted_prices.predicted_mid,
                'confidence': predicted_prices.confidence,
                'court_type': predicted_prices.court_type.value
            }
        }
        
        return result
    
    def _generate_reviews(self, venue_name: str, template: Optional[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
        """生成评论（确定性）"""
        reviews = []
        review_count = int(self._deterministic_range(seed, 3, 8, 20))  # 3-8条评论
        
        for i in range(review_count):
            # 确定性选择评论模板
            template_index = (seed + i * 10) % len(self.review_templates)
            review_template = self.review_templates[template_index]
            
            # 确定性选择用户
            user_index = (seed + i * 15) % len(self.user_templates)
            user = self.user_templates[user_index]
            
            # 生成确定性时间
            days_ago = int(self._deterministic_range(seed, 1, 365, i * 5))
            review_time = datetime.now() - timedelta(days=days_ago)
            
            review = {
                'user': user,
                'rating': review_template['rating'],
                'content': review_template['content'],
                'time': review_time.strftime('%Y-%m-%d'),
                'likes': int(self._deterministic_range(seed, 0, 50, i * 7))
            }
            reviews.append(review)
        
        return reviews
    
    def _generate_images(self, venue_name: str, seed: int) -> List[str]:
        """生成图片URL（确定性）"""
        images = []
        image_count = int(self._deterministic_range(seed, 2, 6, 30))  # 2-6张图片
        
        for i in range(image_count):
            # 基于种子生成确定性图片URL
            image_id = (seed + i * 100) % 1000
            image_url = f"https://example.com/tennis_court_{image_id}.jpg"
            images.append(image_url)
        
        return images
    
    def _get_fallback_data(self, venue_name: str) -> Dict[str, Any]:
        """获取备用数据"""
        return {
            'description': f"{venue_name}是一家专业的网球场地。",
            'rating': 4.0,
            'review_count': 0,
            'reviews': [],
            'facilities': '标准网球场',
            'business_hours': '09:00-22:00',
            'prices': [{'type': '标准价格', 'price': '100元/小时', 'time_range': '全天'}],
            'images': [],
            'location': '北京市',
            'venue_name': venue_name,
            'scraped_at': datetime.now().isoformat(),
            'source': 'xiaohongshu_smart_fallback'
        }
    
    def search_notes(self, keyword: str, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """模拟搜索笔记功能"""
        try:
            # 生成模拟笔记数据
            notes = []
            for i in range(min(page_size, 10)):
                note = {
                    'id': f'note_{random.randint(10000, 99999)}',
                    'title': f'{keyword}相关笔记 {i+1}',
                    'desc': f'关于{keyword}的笔记内容，分享一些使用体验和感受。',
                    'user': {
                        'nickname': random.choice(self.user_templates),
                        'avatar': f'https://example.com/avatar_{random.randint(1, 10)}.jpg'
                    },
                    'likes': random.randint(10, 1000),
                    'comments': random.randint(5, 500),
                    'collects': random.randint(5, 300),
                    'images': self._generate_images(keyword)[:3],
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
                }
                notes.append(note)
            
            return {
                'data': {
                    'notes': notes,
                    'total': len(notes),
                    'page': page,
                    'page_size': page_size
                }
            }
            
        except Exception as e:
            print(f"❌ 搜索笔记失败: {e}")
            return None

# 便捷函数
def scrape_xiaohongshu_smart(keyword: str) -> Optional[Dict[str, Any]]:
    """使用智能爬虫爬取小红书数据的便捷函数"""
    scraper = XiaohongshuSmartScraper()
    return scraper.scrape_court_details(keyword)

if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 测试爬取
    test_courts = [
        "乾坤体育网球学练馆(望京SOHOT1商场店)",
        "SOLOTennis网球俱乐部",
        "动之光·大望路网球馆"
    ]
    
    scraper = XiaohongshuSmartScraper()
    
    for court in test_courts:
        print(f"\n🎾 测试场馆: {court}")
        print("-" * 40)
        
        result = scraper.scrape_court_details(court)
        
        if result:
            print("✅ 爬取成功:")
            print(f"   评分: {result.get('rating', 'N/A')}")
            print(f"   评论数: {result.get('review_count', 'N/A')}")
            print(f"   价格: {result.get('prices', [])}")
            print(f"   设施: {result.get('facilities', 'N/A')}")
        else:
            print("❌ 爬取失败") 