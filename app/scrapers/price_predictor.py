#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网球场地价格预测模型
基于场地类型和周边价格进行智能预测
"""

import math
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import statistics

class CourtType(Enum):
    """场地类型枚举"""
    INDOOR = "室内"
    AIR_DOME = "气膜"
    OUTDOOR = "室外"

@dataclass
class PriceRange:
    """价格范围数据类"""
    min_price: float
    max_price: float
    mid_price: float
    
    @property
    def range(self) -> float:
        """价格范围"""
        return self.max_price - self.min_price

@dataclass
class PredictedPrice:
    """预测价格数据类"""
    predicted_min: float
    predicted_max: float
    predicted_mid: float
    confidence: float  # 置信度 0-1
    court_type: CourtType
    nearby_prices: List[float]

# 统一价格过滤区间
MIN_VALID_PRICE = 50
MAX_VALID_PRICE = 500

def filter_valid_prices(prices, min_price=MIN_VALID_PRICE, max_price=MAX_VALID_PRICE):
    """过滤掉不合理的价格"""
    return [p for p in prices if isinstance(p, (int, float)) and min_price <= p <= max_price]

class PricePredictor:
    """价格预测器"""
    
    def __init__(self):
        # 场地类型基础价格系数
        self.type_multipliers = {
            CourtType.INDOOR: 1.3,    # 室内场地价格较高
            CourtType.AIR_DOME: 1.1,  # 气膜场地价格中等
            CourtType.OUTDOOR: 0.8    # 室外场地价格较低
        }
        
        # 场地类型基础价格范围
        self.type_base_prices = {
            CourtType.INDOOR: PriceRange(120, 200, 160),
            CourtType.AIR_DOME: PriceRange(100, 180, 140),
            CourtType.OUTDOOR: PriceRange(80, 150, 115)
        }
        
        # 价格影响因素权重
        self.weights = {
            'type_base': 0.4,      # 场地类型基础价格权重
            'nearby_avg': 0.4,     # 周边平均价格权重
            'location_factor': 0.2  # 地理位置因子权重
        }
    
    def detect_court_type(self, venue_name: str, description: str = "") -> CourtType:
        """检测场地类型"""
        text = (venue_name + " " + description).lower()
        
        # 室内场地关键词
        indoor_keywords = ['室内', 'indoor', '地下', '地库', '商场', '大厦', '中心', '俱乐部']
        # 气膜场地关键词
        air_dome_keywords = ['气膜', 'air dome', '充气', '膜结构', '穹顶']
        # 室外场地关键词
        outdoor_keywords = ['室外', 'outdoor', '露天', '屋顶', '天台', '公园']
        
        if any(keyword in text for keyword in air_dome_keywords):
            return CourtType.AIR_DOME
        elif any(keyword in text for keyword in indoor_keywords):
            return CourtType.INDOOR
        elif any(keyword in text for keyword in outdoor_keywords):
            return CourtType.OUTDOOR
        else:
            # 默认根据场馆名称判断
            if any(word in venue_name for word in ['中心', '俱乐部', '大厦', '广场']):
                return CourtType.INDOOR
            elif any(word in venue_name for word in ['公园', '体育场', '运动场']):
                return CourtType.OUTDOOR
            else:
                return CourtType.AIR_DOME  # 默认气膜
    
    def get_nearby_prices(self, venue_name: str, all_venues: List[Dict]) -> List[float]:
        """获取周边2000米内的价格数据"""
        # 这里简化处理，实际应该根据经纬度计算距离
        # 暂时返回所有场馆的价格作为参考
        nearby_prices = []
        
        for venue in all_venues:
            if venue.get('prices'):
                for price_info in venue['prices']:
                    price_str = price_info.get('price', '')
                    if price_str and '元/小时' in price_str:
                        try:
                            price = float(price_str.replace('元/小时', ''))
                            nearby_prices.append(price)
                        except ValueError:
                            continue
        
        return nearby_prices if nearby_prices else [100, 150, 200]  # 默认价格
    
    def calculate_location_factor(self, venue_name: str) -> float:
        """计算地理位置因子"""
        # 根据场馆名称判断地理位置等级
        premium_areas = ['国贸', 'cbd', '三里屯', '朝阳公园', '工体', '鸟巢', '水立方', '王府井', '西单']
        standard_areas = ['望京', '酒仙桥', '双井', '劲松', '潘家园', '百子湾', '四惠', '大望路']
        
        venue_lower = venue_name.lower()
        
        if any(area in venue_lower for area in premium_areas):
            return 1.3  # 高端区域
        elif any(area in venue_lower for area in standard_areas):
            return 1.0  # 标准区域
        else:
            return 0.9  # 其他区域
    
    def predict_price_range(self, venue_name: str, description: str = "", 
                          all_venues: List[Dict] = None) -> PredictedPrice:
        """预测价格范围"""
        if all_venues is None:
            all_venues = []
        
        # 1. 检测场地类型
        court_type = self.detect_court_type(venue_name, description)
        
        # 2. 获取周边价格
        nearby_prices = self.get_nearby_prices(venue_name, all_venues)
        # 新增：过滤极端值
        nearby_prices = filter_valid_prices(nearby_prices)
        
        # 3. 计算地理位置因子
        location_factor = self.calculate_location_factor(venue_name)
        
        # 4. 获取场地类型基础价格
        base_prices = self.type_base_prices[court_type]
        type_multiplier = self.type_multipliers[court_type]
        
        # 5. 计算周边价格统计
        if nearby_prices:
            nearby_min = min(nearby_prices)
            nearby_max = max(nearby_prices)
            nearby_avg = sum(nearby_prices) / len(nearby_prices)
        else:
            nearby_min = nearby_max = nearby_avg = 150
        
        # 6. 预测价格计算
        # 最低价格 = 基础最低价 * 类型系数 * 位置因子 * 0.8
        predicted_min = base_prices.min_price * type_multiplier * location_factor * 0.8
        
        # 最高价格 = 基础最高价 * 类型系数 * 位置因子 * 1.2
        predicted_max = base_prices.max_price * type_multiplier * location_factor * 1.2
        
        # 中点价格 = (最低 + 最高) / 2
        predicted_mid = (predicted_min + predicted_max) / 2
        
        # 新增：clip预测结果
        predicted_min = max(min(predicted_min, MAX_VALID_PRICE), MIN_VALID_PRICE)
        predicted_max = max(min(predicted_max, MAX_VALID_PRICE), MIN_VALID_PRICE)
        predicted_mid = max(min(predicted_mid, MAX_VALID_PRICE), MIN_VALID_PRICE)
        
        # 7. 计算置信度
        confidence = min(0.9, 0.5 + len(nearby_prices) * 0.1)
        
        return PredictedPrice(
            predicted_min=round(predicted_min, 0),
            predicted_max=round(predicted_max, 0),
            predicted_mid=round(predicted_mid, 0),
            confidence=confidence,
            court_type=court_type,
            nearby_prices=nearby_prices
        )
    
    def format_price_labels(self, actual_prices: List[Dict], 
                          predicted_prices: PredictedPrice) -> List[Dict]:
        """格式化价格标签"""
        formatted_prices = []
        
        # 处理实际价格
        for price_info in actual_prices:
            price_type = price_info.get('type', '')
            price_str = price_info.get('price', '')
            
            # 添加标签
            if '黄金' in price_type:
                label = "黄金时段"
            elif '非黄金' in price_type:
                label = "非黄时段"
            elif '会员' in price_type:
                label = "会员低至"
            else:
                label = price_type
            
            formatted_prices.append({
                **price_info,
                'label': label,
                'is_actual': True
            })
        
        # 添加预测价格
        formatted_prices.extend([
            {
                'type': '预测最低',
                'price': f"{predicted_prices.predicted_min}元/小时",
                'time_range': '预测',
                'label': '预测最低',
                'is_actual': False,
                'confidence': predicted_prices.confidence
            },
            {
                'type': '预测中点',
                'price': f"{predicted_prices.predicted_mid}元/小时",
                'time_range': '预测',
                'label': '预测中点',
                'is_actual': False,
                'confidence': predicted_prices.confidence
            },
            {
                'type': '预测最高',
                'price': f"{predicted_prices.predicted_max}元/小时",
                'time_range': '预测',
                'label': '预测最高',
                'is_actual': False,
                'confidence': predicted_prices.confidence
            }
        ])
        
        return formatted_prices

# 全局预测器实例
price_predictor = PricePredictor() 