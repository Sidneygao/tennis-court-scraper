#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BING爬取价格的置信度模型
基于正态分布和异常价格调整的动态置信度计算
"""
import json
import sqlite3
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PriceConfidenceModel:
    """价格置信度模型"""
    
    def __init__(self, db_path: str = 'data/courts.db'):
        self.db_path = db_path
        self.indoor_model = None
        self.outdoor_model = None
        self.indoor_peak_model = None
        self.indoor_offpeak_model = None
        self.outdoor_peak_model = None
        self.outdoor_offpeak_model = None
        
    def extract_price_value(self, price_str: str) -> Optional[float]:
        """从价格字符串中提取数值"""
        try:
            # 移除货币符号和单位
            price_str = price_str.replace('¥', '').replace('￥', '').replace('元', '').replace('/小时', '').replace('/时', '')
            return float(price_str)
        except:
            return None
    
    def get_real_prices_from_db(self) -> Dict[str, List[float]]:
        """从数据库获取所有真实价格数据（包括BING价格和融合价格）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有有真实价格的场馆（检查bing_prices和merged_prices字段）
        cursor.execute("""
            SELECT tc.name, tc.court_type, cd.merged_prices, cd.bing_prices
            FROM tennis_courts tc
            LEFT JOIN court_details cd ON tc.id = cd.court_id
            WHERE (cd.merged_prices IS NOT NULL AND cd.merged_prices != '' AND cd.merged_prices != '[]')
               OR (cd.bing_prices IS NOT NULL AND cd.bing_prices != '' AND cd.bing_prices != '[]')
        """)
        
        indoor_prices = []
        outdoor_prices = []
        indoor_peak_prices = []
        indoor_offpeak_prices = []
        outdoor_peak_prices = []
        outdoor_offpeak_prices = []
        
        total_courts = 0
        total_prices = 0
        
        for name, court_type, merged_prices, bing_prices in cursor.fetchall():
            try:
                # 处理融合价格
                if merged_prices:
                    prices_data = json.loads(merged_prices)
                    if isinstance(prices_data, list):
                        total_courts += 1
                        court_prices = 0
                        
                        for price_item in prices_data:
                            if not isinstance(price_item, dict):
                                continue
                                
                            price_str = price_item.get('price', '')
                            price_type = price_item.get('type', '').lower()
                            
                            price_value = self.extract_price_value(price_str)
                            if price_value is None or price_value <= 0:
                                continue
                            
                            court_prices += 1
                            total_prices += 1
                            
                            # 判断场馆类型
                            is_indoor = self._is_indoor_court(court_type, name)
                            
                            # 判断时段
                            is_peak = self._is_peak_time(price_type)
                            
                            # 分类价格
                            if is_indoor:
                                indoor_prices.append(price_value)
                                if is_peak:
                                    indoor_peak_prices.append(price_value)
                                else:
                                    indoor_offpeak_prices.append(price_value)
                            else:
                                outdoor_prices.append(price_value)
                                if is_peak:
                                    outdoor_peak_prices.append(price_value)
                                else:
                                    outdoor_offpeak_prices.append(price_value)
                
                # 处理BING价格
                if bing_prices:
                    bing_data = json.loads(bing_prices)
                    if isinstance(bing_data, list):
                        if not merged_prices:  # 如果没有融合价格，才增加场馆计数
                            total_courts += 1
                        
                        for price_item in bing_data:
                            if not isinstance(price_item, dict):
                                continue
                                
                            price_str = price_item.get('price', '')
                            price_type = price_item.get('type', '').lower()
                            
                            price_value = self.extract_price_value(price_str)
                            if price_value is None or price_value <= 0:
                                continue
                            
                            total_prices += 1
                            
                            # 判断场馆类型
                            is_indoor = self._is_indoor_court(court_type, name)
                            
                            # 判断时段
                            is_peak = self._is_peak_time(price_type)
                            
                            # 分类价格
                            if is_indoor:
                                indoor_prices.append(price_value)
                                if is_peak:
                                    indoor_peak_prices.append(price_value)
                                else:
                                    indoor_offpeak_prices.append(price_value)
                            else:
                                outdoor_prices.append(price_value)
                                if is_peak:
                                    outdoor_peak_prices.append(price_value)
                                else:
                                    outdoor_offpeak_prices.append(price_value)
                            
            except Exception as e:
                logger.warning(f"解析场馆 {name} 价格数据失败: {e}")
                continue
        
        conn.close()
        
        logger.info(f"获取真实价格数据完成:")
        logger.info(f"  总场馆数: {total_courts}")
        logger.info(f"  总价格数: {total_prices}")
        logger.info(f"  室内价格: {len(indoor_prices)} 个")
        logger.info(f"  室外价格: {len(outdoor_prices)} 个")
        logger.info(f"  室内黄金时段: {len(indoor_peak_prices)} 个")
        logger.info(f"  室内非黄金时段: {len(indoor_offpeak_prices)} 个")
        logger.info(f"  室外黄金时段: {len(outdoor_peak_prices)} 个")
        logger.info(f"  室外非黄金时段: {len(outdoor_offpeak_prices)} 个")
        
        return {
            'indoor': indoor_prices,
            'outdoor': outdoor_prices,
            'indoor_peak': indoor_peak_prices,
            'indoor_offpeak': indoor_offpeak_prices,
            'outdoor_peak': outdoor_peak_prices,
            'outdoor_offpeak': outdoor_offpeak_prices
        }
    
    def _is_indoor_court(self, court_type: str, name: str) -> bool:
        """判断是否为室内场馆"""
        if not court_type:
            court_type = ""
        if not name:
            name = ""
        
        # 例外清单：在硬TAG之前处理
        # 1. 嘉里中心-网球场直接判断为室内
        if '嘉里中心-网球场' in name:
            return True
        
        # 2. 所有带"游泳池"字样的场馆直接判断为空（不参与后续操作）
        if '游泳池' in name.lower():
            return False  # 返回False表示不参与后续操作
            
        indoor_keywords = ['室内', '气膜', 'indoor', '馆']
        outdoor_keywords = ['室外', 'outdoor', '场', '公园', '小区']
        
        text = (court_type + name).lower()
        
        # 优先检查明确的关键词
        for keyword in indoor_keywords:
            if keyword in text:
                return True
        for keyword in outdoor_keywords:
            if keyword in text:
                return False
        
        # 默认判断逻辑
        return '馆' in text
    
    def _is_peak_time(self, price_type: str) -> bool:
        """判断是否为黄金时段"""
        peak_keywords = ['黄金', '高峰', 'peak', '黄金时间', '黄金时段']
        offpeak_keywords = ['非黄金', '非高峰', 'off', '非黄金时间', '非黄金时段']
        
        price_type_lower = price_type.lower()
        
        for keyword in peak_keywords:
            if keyword in price_type_lower:
                return True
        for keyword in offpeak_keywords:
            if keyword in price_type_lower:
                return False
        
        # 默认为非黄金时段
        return False
    
    def build_normal_distribution_models(self):
        """建立正态分布模型"""
        prices_data = self.get_real_prices_from_db()
        
        # 建立基础模型
        if len(prices_data['indoor']) >= 3:
            self.indoor_model = self._fit_normal_distribution(prices_data['indoor'])
        if len(prices_data['outdoor']) >= 3:
            self.outdoor_model = self._fit_normal_distribution(prices_data['outdoor'])
        
        # 建立时段模型
        if len(prices_data['indoor_peak']) >= 3:
            self.indoor_peak_model = self._fit_normal_distribution(prices_data['indoor_peak'])
        if len(prices_data['indoor_offpeak']) >= 3:
            self.indoor_offpeak_model = self._fit_normal_distribution(prices_data['indoor_offpeak'])
        if len(prices_data['outdoor_peak']) >= 3:
            self.outdoor_peak_model = self._fit_normal_distribution(prices_data['outdoor_peak'])
        if len(prices_data['outdoor_offpeak']) >= 3:
            self.outdoor_offpeak_model = self._fit_normal_distribution(prices_data['outdoor_offpeak'])
        
        logger.info(f"建立置信度模型完成:")
        logger.info(f"  室内价格: {len(prices_data['indoor'])} 个")
        logger.info(f"  室外价格: {len(prices_data['outdoor'])} 个")
        logger.info(f"  室内黄金时段: {len(prices_data['indoor_peak'])} 个")
        logger.info(f"  室内非黄金时段: {len(prices_data['indoor_offpeak'])} 个")
        logger.info(f"  室外黄金时段: {len(prices_data['outdoor_peak'])} 个")
        logger.info(f"  室外非黄金时段: {len(prices_data['outdoor_offpeak'])} 个")
    
    def _fit_normal_distribution(self, prices: List[float]) -> Dict:
        """拟合正态分布"""
        if len(prices) < 3:
            return None
            
        prices_array = np.array(prices)
        mean = np.mean(prices_array)
        std = np.std(prices_array)
        
        return {
            'mean': mean,
            'std': std,
            'count': len(prices),
            'min': np.min(prices_array),
            'max': np.max(prices_array)
        }
    
    def calculate_confidence(self, price_value: float, court_type: str, name: str, 
                           price_type: str = "标准价格", base_confidence: float = 0.8) -> float:
        """计算价格置信度"""
        if price_value <= 0:
            return 0.0
        
        # 判断场馆类型和时段
        is_indoor = self._is_indoor_court(court_type, name)
        is_peak = self._is_peak_time(price_type)
        
        # 选择对应的模型
        model = None
        if is_indoor:
            if is_peak and self.indoor_peak_model:
                model = self.indoor_peak_model
            elif not is_peak and self.indoor_offpeak_model:
                model = self.indoor_offpeak_model
            else:
                model = self.indoor_model
        else:
            if is_peak and self.outdoor_peak_model:
                model = self.outdoor_peak_model
            elif not is_peak and self.outdoor_offpeak_model:
                model = self.outdoor_offpeak_model
            else:
                model = self.outdoor_model
        
        # 如果没有模型，返回基础置信度
        if not model:
            return base_confidence
        
        # 排除超低和超高价格
        if is_indoor:
            if price_value < 60 or price_value > 600:  # 室内价格范围
                return 0.0
        else:
            if price_value < 50 or price_value > 300:  # 室外价格范围
                return 0.0
        
        # 计算正态分布置信度
        z_score = abs(price_value - model['mean']) / model['std']
        normal_confidence = 1.0 - stats.norm.cdf(z_score)
        
        # 确保置信度在合理范围内
        normal_confidence = max(0.1, min(0.95, normal_confidence))
        
        # 对较高和较低置信度进行额外调整
        if normal_confidence > 0.8:
            # 高置信度降低
            normal_confidence = 0.8 + (normal_confidence - 0.8) * 0.7
        elif normal_confidence < 0.3:
            # 低置信度进一步降低
            normal_confidence = normal_confidence * 0.8
        
        # 异常价格调整（在合理范围内）
        adjustment = 0.0
        if is_indoor:
            if price_value <= 80 or price_value >= 400:
                adjustment = min(0.2, normal_confidence * 0.2)
        else:
            if price_value <= 56 or price_value >= 200:
                adjustment = min(0.2, normal_confidence * 0.2)
        
        # 最终置信度
        final_confidence = normal_confidence + adjustment
        return min(0.9, final_confidence)
    
    def update_models_with_new_data(self, new_prices: List[Dict]):
        """用新数据更新模型（迭代动态模型）"""
        # 这里可以实现增量更新逻辑
        # 暂时重新构建模型
        self.build_normal_distribution_models()
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            'indoor_model': self.indoor_model,
            'outdoor_model': self.outdoor_model,
            'indoor_peak_model': self.indoor_peak_model,
            'indoor_offpeak_model': self.indoor_offpeak_model,
            'outdoor_peak_model': self.outdoor_peak_model,
            'outdoor_offpeak_model': self.outdoor_offpeak_model
        }

# 全局实例
confidence_model = PriceConfidenceModel() 