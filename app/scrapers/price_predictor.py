#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2KM类别步进融合价格预测算法
基于场馆地理位置的智能价格预测
"""

import json
import math
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.database import get_db
from app.models import TennisCourt, CourtDetail

logger = logging.getLogger(__name__)

class PricePredictor:
    """2KM类别步进融合价格预测器"""
    
    def __init__(self):
        self.db = next(get_db())
        self.initial_radius = 2.0  # 初始搜索半径2KM
        self.step_radius = 1.0     # 扩展步长1KM
        self.min_data_count = 2    # 最小有效数据量，降为2家
        self.max_radius = 16.0     # 最大搜索半径16KM
        
        # 三层次判断模型 - 场馆类型识别关键词
        self.indoor_keywords = [
            '室内', '馆', '学练馆', '训练馆', '练习馆', 
            '健身', '酒店', '商场', '大厦', '广场', '写字楼', '商务楼',
            'TennisGym', 'Tennislife', 'RockTennis', 'EYESIN', 'NEXTCHAMP'
        ]
        
        self.outdoor_keywords = [
            '室外', '公园', '网球场', '球场', '基地', '村', 
            '家园', '小区', '社区', '花园', '园', '场', '地'
        ]
    
    def determine_court_type(self, court_name: str, address: str = "") -> str:
        """
        使用三层判断法确定场馆类型
        1. 硬TAG判断
        2. 直接关键字判断
        3. 间接关键字判断
        如果都无法确定，返回"未知"
        """
        if not court_name:
            return "未知"
        
        name_lower = court_name.lower()
        address_lower = (address or "").lower()
        full_text = name_lower + " " + address_lower
        
        # 特殊处理：包含"游泳池"的场馆直接返回空
        if "游泳池" in name_lower or "游泳池" in address_lower:
            return ""
        
        # 特例：万源网球俱乐部，直接判定为室外
        if "万源网球俱乐部" in court_name:
            return "室外"
        
        # 特例：OPeN STAR网球俱乐部(肖村超级光合店)，直接判定为室外
        if "OPeN STAR网球俱乐部(肖村超级光合店)" in court_name:
            return "室外"
        
        # 特例：毅思趣网球俱乐部，直接判定为室外
        if "毅思趣网球俱乐部" in court_name:
            return "室外"
        
        # 特例：蓝星网球，直接判定为室内
        if "蓝星网球" in court_name:
            return "室内"
        
        # 特例：金徽网球中心，直接判定为室内
        if "金徽网球中心" in court_name:
            return "室内"
        
        # 特例：星纬网球中心，直接判定为室内
        if "星纬网球中心" in court_name:
            return "室内"
        
        # 特例：雨露润泽网球俱乐部(清芷园店)，直接判定为未知
        if "雨露润泽网球俱乐部(清芷园店)" in court_name:
            return "未知"
        
        # 特例：清芷园网球，直接判定为室外
        if "清芷园网球" in court_name:
            return "室外"
        
        # 特例：拓能壹加网球基地(浩鸿园店)，直接判定为室外
        if "拓能壹加网球基地(浩鸿园店)" in court_name:
            return "室外"
        
        # 特例：齐动力网球(亚运村姜庄湖店)，直接判定为室内
        if "齐动力网球(亚运村姜庄湖店)" in court_name:
            return "室内"
        
        # 特例：金地网球，直接判定为室内
        if "金地网球" in court_name:
            return "室内"
        
        # 特例：得乐网球培训，直接判定为室外
        if "得乐网球培训" in court_name:
            return "室外"
        
        # 特例：国家网球中心莲花球场，直接判定为室内
        if "国家网球中心莲花球场" in court_name:
            return "室内"
        
        # 特例：国家网球中心映月球场，直接判定为室内
        if "国家网球中心映月球场" in court_name:
            return "室内"
        
        # 特例：国家网球中心-钻石球场，直接判定为室内
        if "国家网球中心-钻石球场" in court_name:
            return "室内"
        
        # 特例：国家网球中心-布拉德球场，直接判定为室内
        if "国家网球中心-布拉德球场" in court_name:
            return "室内"
        
        # 特例：木叶网球俱乐部，直接判定为室外
        if "木叶网球俱乐部" in court_name:
            return "室外"
        
        # 特例：球星网球汇(合生汇球星运动中心店)，直接判定为室内
        if "球星网球汇(合生汇球星运动中心店)" in court_name:
            return "室内"
        
        # 特例：观唐网球俱乐部，直接判定为室外
        if "观唐网球俱乐部" in court_name:
            return "室外"
        
        # 特例：名人都网球俱乐部，直接判定为室内
        if "名人都网球俱乐部" in court_name:
            return "室内"
        
        # 第一层：硬TAG判断
        if "室内" in name_lower or "气膜" in name_lower:
            return "室内"
        if "室外" in name_lower:
            return "室外"
        
        # 第二层：直接关键字判断
        # 室外关键字（优先判断）
        outdoor_keywords = ["网球场", "网球公园", "网球基地"]
        for keyword in outdoor_keywords:
            if keyword in name_lower or keyword in address_lower:
                return "室外"
        
        # 室内关键字
        indoor_keywords = ["网球馆", "网球汇", "网球学练馆", "网球训练馆", "体育馆"]
        for keyword in indoor_keywords:
            if keyword in name_lower or keyword in address_lower:
                return "室内"
        
        # 第三层：间接关键字判断
        # 室内间接关键字
        indoor_indirect = ['层', '楼', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5', '电梯', '馆内']
        for keyword in indoor_indirect:
            if keyword in full_text:
                return "室内"
        
        # 室外间接关键字
        outdoor_indirect = ['网球场', '室外', '露天', '户外']
        for keyword in outdoor_indirect:
            if keyword in full_text:
                return "室外"
        
        # 如果三层判断都无法确定，返回"未知"
        return "未知"
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两个坐标点之间的距离（KM）"""
        try:
            # 使用Haversine公式计算球面距离
            R = 6371  # 地球半径（KM）
            
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
        except Exception as e:
            logger.error(f"计算距离失败: {e}")
            return float('inf')
    
    def get_courts_without_real_prices(self) -> List[TennisCourt]:
        """获取没有真实价格缓存的场馆"""
        courts = self.db.query(TennisCourt).all()
        result = []
        
        for court in courts:
            # 检查主表价格字段
            has_main_price = bool(court.peak_price or court.off_peak_price or court.member_price)
            
            # 检查详情表真实价格字段
            detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            has_real_price = False
            
            if detail:
                for field in [detail.bing_prices, detail.dianping_prices, detail.meituan_prices, detail.merged_prices]:
                    try:
                        if field:
                            price_data = json.loads(field)
                            if price_data and len(price_data) > 0:
                                has_real_price = True
                                break
                    except:
                        continue
            
            # 只有主表和详情表都没有真实价格，且没有预测价格的场馆才需要预测
            if not has_main_price and not has_real_price:
                if detail and detail.predict_prices:
                    try:
                        predict_data = json.loads(detail.predict_prices)
                        if predict_data and predict_data.get('peak_price'):
                            continue  # 已有预测价格，跳过
                    except:
                        pass
                
                result.append(court)
        
        return result
    
    def find_nearby_courts_with_prices(self, target_court: TennisCourt, radius: float, filter_by_type: bool = True) -> List[Dict]:
        """在指定半径内查找有真实价格数据的邻域场馆"""
        if not target_court.latitude or not target_court.longitude:
            return []
        
        # 获取目标场馆类型
        target_court_type = self.determine_court_type(target_court.name)
        if filter_by_type:
            logger.info(f"查找同类型场馆: {target_court.name} -> {target_court_type}")
        else:
            logger.info(f"查找所有类型场馆: {target_court.name} -> {target_court_type}")
        
        nearby_courts = []
        all_courts = self.db.query(TennisCourt).all()
        
        for court in all_courts:
            if court.id == target_court.id:
                continue  # 跳过自己
            
            # 排除包含"游泳池"的非网球场馆
            if '游泳池' in court.name:
                continue
            
            if not court.latitude or not court.longitude:
                continue
            
            # 类型过滤（可选）
            if filter_by_type:
                court_type = self.determine_court_type(court.name)
                if court_type != target_court_type:
                    continue  # 跳过不同类型场馆
            
            # 计算距离
            distance = self.calculate_distance(
                target_court.latitude, target_court.longitude,
                court.latitude, court.longitude
            )
            
            if distance <= radius:
                # 检查是否有真实价格数据
                detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if detail:
                    real_prices = self._extract_real_prices(detail)
                    if real_prices:
                        nearby_courts.append({
                            'court': court,
                            'distance': distance,
                            'prices': real_prices
                        })
        
        if filter_by_type:
            logger.info(f"找到 {len(nearby_courts)} 个同类型({target_court_type})邻域样本")
        else:
            logger.info(f"找到 {len(nearby_courts)} 个所有类型邻域样本")
        return nearby_courts
    
    def _extract_real_prices(self, detail: CourtDetail) -> Optional[Dict]:
        """从详情记录中提取真实价格数据"""
        try:
            # 优先使用融合价格
            if detail.merged_prices:
                price_data = json.loads(detail.merged_prices)
                if price_data and isinstance(price_data, list) and len(price_data) > 0:
                    return self._parse_price_data(price_data)
            
            # 其次使用BING价格
            if detail.bing_prices:
                price_data = json.loads(detail.bing_prices)
                if price_data and isinstance(price_data, list) and len(price_data) > 0:
                    return self._parse_price_data(price_data)
            
            # 再次使用点评价格
            if detail.dianping_prices:
                price_data = json.loads(detail.dianping_prices)
                if price_data and isinstance(price_data, list) and len(price_data) > 0:
                    return self._parse_price_data(price_data)
            
            # 最后使用美团价格
            if detail.meituan_prices:
                price_data = json.loads(detail.meituan_prices)
                if price_data and isinstance(price_data, list) and len(price_data) > 0:
                    return self._parse_price_data(price_data)
            
            return None
        except Exception as e:
            logger.error(f"提取真实价格失败: {e}")
            return None
    
    def _parse_price_data(self, price_data: List[Dict]) -> Optional[Dict]:
        """解析价格数据，提取黄金价格和非黄金价格"""
        try:
            peak_price = None
            off_peak_price = None
            standard_prices = []  # 新增：收集标准价格
            
            for price_item in price_data:
                if isinstance(price_item, dict):
                    price_type = price_item.get('type', '').lower()
                    price_str = price_item.get('price', '')
                    
                    # 提取价格数值
                    price_value = self._extract_price_value(price_str)
                    if price_value is None:
                        continue
                    
                    # 分类价格
                    if any(keyword in price_type for keyword in ['黄金', '高峰', 'peak', '黄金时间']):
                        peak_price = price_value
                    elif any(keyword in price_type for keyword in ['非黄金', '非高峰', 'off', '非黄金时间']):
                        off_peak_price = price_value
                    elif any(keyword in price_type for keyword in ['标准价格', '标准', '综合报价', '综合']):
                        # 处理标准价格和综合报价类型
                        standard_prices.append(price_value)
            
            # 新增：如果没有明确的黄金/非黄金价格，使用标准价格
            if not peak_price and not off_peak_price and standard_prices:
                # 对标准价格进行统计分析
                if len(standard_prices) >= 2:
                    # 如果有多个标准价格，取中位数作为基准
                    sorted_prices = sorted(standard_prices)
                    median_price = sorted_prices[len(sorted_prices) // 2]
                    
                    # 根据价格分布设置黄金和非黄金价格
                    # 黄金时段通常比标准价格高30%
                    # 非黄金时段通常比标准价格低30%
                    peak_price = int(median_price * 1.30)  # 黄金时段 +30%
                    off_peak_price = int(median_price * 0.70)  # 非黄金时段 -30%
                else:
                    # 只有一个标准价格，直接使用
                    peak_price = standard_prices[0]
                    off_peak_price = standard_prices[0]
            
            if peak_price or off_peak_price:
                return {
                    'peak_price': peak_price,
                    'off_peak_price': off_peak_price
                }
            
            return None
        except Exception as e:
            logger.error(f"解析价格数据失败: {e}")
            return None
    
    def _extract_price_value(self, price_str: str) -> Optional[int]:
        """从价格字符串中提取数值"""
        try:
            # 匹配数字
            matches = re.findall(r'(\d+)', price_str)
            if matches:
                return int(matches[0])
            return None
        except:
            return None
    
    def predict_price_for_court(self, court: TennisCourt) -> Optional[Dict]:
        """为单个场馆预测价格"""
        try:
            logger.info(f"开始预测场馆价格: {court.name}")
            
            # 使用三层次判断模型识别场馆类型
            court_type = self.determine_court_type(court.name)
            logger.info(f"场馆类型判断: {court.name} -> {court_type}")
            
            # 区域自定义步进上限（核心区1-3KM，非核心1-4KM）
            area_3km = ['fengtai_east', 'guomao', 'aoyuncun', 'yizhuang', 'shuangjing', 'sanyuanqiao']
            # 新增：室外最大半径6KM，步进[1,2,3,4,5,6]
            if court_type == '室外':
                max_radius = 6
                step_list = [1, 2, 3, 4, 5, 6]
            else:
                max_radius = 3 if getattr(court, 'area', None) in area_3km else 4
                step_list = [1, 2, 3] if max_radius == 3 else [1, 2, 3, 4]
            found = False
            for current_radius in step_list:
                # 查找邻域样本（严格同类型过滤）
                nearby_courts = self.find_nearby_courts_with_prices(court, current_radius, filter_by_type=True)
                if len(nearby_courts) >= 2:
                    found = True
                    break
            if not found:
                logger.warning(f"场馆 {court.name}({getattr(court, 'area', None)}) {max_radius}KM内无有效邻域样本，无法预测")
                return {'predict_failed': True, 'reason': f'{max_radius}KM内无有效邻域样本'}
            
            # 计算分位数加权价格
            peak_prices = []
            off_peak_prices = []
            for nearby in nearby_courts:
                prices = nearby['prices']
                if prices.get('peak_price'):
                    peak_prices.append(prices['peak_price'])
                if prices.get('off_peak_price'):
                    off_peak_prices.append(prices['off_peak_price'])
            
            # 分位数加权中位数算法
            def quantile_weighted_median(prices_list, time_type):
                """
                分位数加权中位数算法
                黄金时段：偏向高价格分位数（75%分位数）
                非黄金时段：偏向低价格分位数（25%分位数）
                """
                if not prices_list:
                    return None
                
                sorted_prices = sorted(prices_list)
                n = len(sorted_prices)
                
                if time_type == "peak":
                    # 黄金时段：偏向高价格分位数（75%分位数）
                    quantile_index = int(n * 0.75)
                    if quantile_index >= n:
                        quantile_index = n - 1
                    result = sorted_prices[quantile_index]
                else:
                    # 非黄金时段：偏向低价格分位数（25%分位数）
                    quantile_index = int(n * 0.25)
                    if quantile_index < 0:
                        quantile_index = 0
                    result = sorted_prices[quantile_index]
                
                return result
            
            # 计算预测价格（取整到10）
            predicted_peak = None
            predicted_off_peak = None
            
            if peak_prices:
                quantile_peak = quantile_weighted_median(peak_prices, "peak")
                predicted_peak = round(quantile_peak / 10) * 10 if quantile_peak is not None else None
            if off_peak_prices:
                quantile_off = quantile_weighted_median(off_peak_prices, "off_peak")
                predicted_off_peak = round(quantile_off / 10) * 10 if quantile_off is not None else None
            if not predicted_peak and not predicted_off_peak:
                logger.warning(f"场馆 {court.name} 无法提取有效价格数据")
                return None
            # 构建预测结果
            result = {
                'peak_price': predicted_peak,
                'off_peak_price': predicted_off_peak,
                'data_count': len(nearby_courts),
                'search_radius': current_radius,
                'predict_time': datetime.now().isoformat(),
                'source_courts': [
                    {
                        'id': nearby['court'].id,
                        'name': nearby['court'].name,
                        'distance': round(nearby['distance'], 1)
                    }
                    for nearby in nearby_courts
                ],
                'predict_method': '邻域分位数加权法'
            }
            logger.info(f"场馆 {court.name} 价格预测完成: 黄金{predicted_peak}元, 非黄金{predicted_off_peak}元（分位数加权法）")
            return result
        except Exception as e:
            logger.error(f"预测场馆 {court.name} 价格失败: {e}")
            return None
    
    def batch_predict_prices(self, max_workers: int = 2, limit: int = 1000) -> Dict:
        """批量预测价格"""
        start_time = datetime.now()
        logger.info(f"开始批量2KM类别步进融合价格预测，限制: {limit}，并发数: {max_workers}")
        
        # 获取需要预测的场馆
        courts = self.get_courts_without_real_prices()
        if limit:
            courts = courts[:limit]
        
        logger.info(f"找到 {len(courts)} 个需要预测价格的场馆")
        
        success_count = 0
        failed_count = 0
        
        for court in courts:
            try:
                # 预测价格
                predict_result = self.predict_price_for_court(court)
                
                if predict_result:
                    # 保存预测结果
                    detail = self.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                    if not detail:
                        # 创建详情记录
                        detail = CourtDetail(court_id=court.id)
                        self.db.add(detail)
                        self.db.commit()
                        self.db.refresh(detail)
                    
                    # 更新预测价格
                    detail.predict_prices = json.dumps(predict_result, ensure_ascii=False)
                    self.db.commit()
                    
                    success_count += 1
                    logger.info(f"成功更新预测价格缓存: detail_id={detail.id}")
                else:
                    failed_count += 1
                    logger.warning(f"场馆 {court.name} 价格预测失败")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"处理场馆 {court.name} 失败: {e}")
                try:
                    self.db.rollback()
                except:
                    pass
        
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'total_courts': len(courts),
            'success_count': success_count,
            'failed_count': failed_count,
            'duration_seconds': duration
        }
        
        logger.info(f"批量价格预测完成: {result}")
        return result 