from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
# from sqlalchemy.ext.declarative import declarative_base  # 删除本地Base定义
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.database import Base  # 统一使用 app.database.Base

class TennisCourt(Base):
    """网球场馆数据库模型"""
    __tablename__ = "tennis_courts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(String(500), nullable=False)
    phone = Column(String(50))
    area = Column(String(50), nullable=False, index=True)  # 区域：wangjing, dongba, jiuxianqiao
    area_name = Column(String(50), nullable=False)  # 区域名称：望京、东坝、酒仙桥
    
    # 位置信息
    latitude = Column(Float)
    longitude = Column(Float)
    
    # 场地信息
    court_type = Column(String(50))  # 网球场/网球馆
    has_roof = Column(Boolean, default=False)  # 是否有顶棚
    court_count = Column(Integer, default=1)  # 场地数量
    
    # 营业信息
    business_hours = Column(String(200))
    is_open = Column(Boolean, default=True)
    
    # 价格信息
    peak_price = Column(String(100))  # 黄金时间价格
    off_peak_price = Column(String(100))  # 非黄金时间价格
    member_price = Column(String(100))  # 会员价格
    price_unit = Column(String(50))  # 价格单位：小时/场次
    
    # 详细信息
    description = Column(Text)
    facilities = Column(Text)  # 设施信息
    traffic_info = Column(Text)  # 交通信息
    
    # 数据来源
    data_source = Column(String(100))  # 数据来源：amap, dianping, meituan
    source_url = Column(String(500))  # 来源URL
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    price_updated_at = Column(DateTime)  # 价格更新时间

# Pydantic模型用于API
class TennisCourtBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    area: str
    area_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    court_type: Optional[str] = None
    has_roof: Optional[bool] = False
    court_count: Optional[int] = 1
    business_hours: Optional[str] = None
    is_open: Optional[bool] = True
    peak_price: Optional[str] = None
    off_peak_price: Optional[str] = None
    member_price: Optional[str] = None
    price_unit: Optional[str] = None
    description: Optional[str] = None
    facilities: Optional[str] = None
    traffic_info: Optional[str] = None
    data_source: Optional[str] = None
    source_url: Optional[str] = None

class TennisCourtCreate(TennisCourtBase):
    pass

class TennisCourtUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    area: Optional[str] = None
    area_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    court_type: Optional[str] = None
    has_roof: Optional[bool] = None
    court_count: Optional[int] = None
    business_hours: Optional[str] = None
    is_open: Optional[bool] = None
    peak_price: Optional[str] = None
    off_peak_price: Optional[str] = None
    member_price: Optional[str] = None
    price_unit: Optional[str] = None
    description: Optional[str] = None
    facilities: Optional[str] = None
    traffic_info: Optional[str] = None
    data_source: Optional[str] = None
    source_url: Optional[str] = None

class TennisCourtResponse(TennisCourtBase):
    id: int
    created_at: datetime
    updated_at: datetime
    price_updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 爬虫数据模型
class ScrapedCourtData(BaseModel):
    """爬虫抓取的原始数据"""
    name: str
    address: str
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_hours: Optional[str] = None
    description: Optional[str] = None
    data_source: str
    source_url: Optional[str] = None
    raw_data: Optional[dict] = None  # 原始数据

class PriceInfo(BaseModel):
    """价格信息模型"""
    peak_price: Optional[str] = None
    off_peak_price: Optional[str] = None
    member_price: Optional[str] = None
    price_unit: Optional[str] = None
    price_updated_at: Optional[datetime] = None

# 融合详情相关模型
class CourtDetail(Base):
    """场馆融合详情数据库模型"""
    __tablename__ = "court_details"
    
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, nullable=False, index=True)  # 关联的场馆ID
    
    # 融合信息
    merged_description = Column(Text)  # 融合后的描述
    merged_facilities = Column(Text)   # 融合后的设施信息
    merged_traffic_info = Column(Text) # 融合后的交通信息
    merged_business_hours = Column(String(200))  # 融合后的营业时间
    
    # 价格信息（从点评/美团获取）
    prices = Column(Text)           # 真实价格信息（JSON格式）
    dianping_prices = Column(Text)  # 点评价格信息（JSON格式）
    meituan_prices = Column(Text)   # 美团价格信息（JSON格式）
    merged_prices = Column(Text)    # 融合后的价格信息（JSON格式）
    predict_prices = Column(Text)   # 2KM类别步进融合预测价格（JSON格式）
    bing_prices = Column(Text)      # BING搜索价格信息（JSON格式）
    
    # 评分信息
    dianping_rating = Column(Float)  # 点评评分
    meituan_rating = Column(Float)   # 美团评分
    merged_rating = Column(Float)    # 融合评分
    
    # 评论信息
    dianping_reviews = Column(Text)  # 点评评论（JSON格式）
    meituan_reviews = Column(Text)   # 美团评论（JSON格式）
    
    # 图片信息
    dianping_images = Column(Text)   # 点评图片（JSON格式）
    meituan_images = Column(Text)    # 美团图片（JSON格式）
    
    # 缓存信息
    last_dianping_update = Column(DateTime)  # 最后更新点评数据时间
    last_meituan_update = Column(DateTime)   # 最后更新美团数据时间
    cache_expires_at = Column(DateTime)      # 缓存过期时间
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CourtDetailCreate(BaseModel):
    court_id: int
    merged_description: Optional[str] = None
    merged_facilities: Optional[str] = None
    merged_traffic_info: Optional[str] = None
    merged_business_hours: Optional[str] = None
    dianping_prices: Optional[str] = None
    meituan_prices: Optional[str] = None
    merged_prices: Optional[str] = None
    dianping_rating: Optional[float] = None
    meituan_rating: Optional[float] = None
    merged_rating: Optional[float] = None
    dianping_reviews: Optional[str] = None
    meituan_reviews: Optional[str] = None
    dianping_images: Optional[str] = None
    meituan_images: Optional[str] = None

class CourtDetailResponse(BaseModel):
    id: int
    court_id: int
    merged_description: Optional[str] = None
    merged_facilities: Optional[str] = None
    merged_traffic_info: Optional[str] = None
    merged_business_hours: Optional[str] = None
    dianping_prices: Optional[str] = None
    meituan_prices: Optional[str] = None
    merged_prices: Optional[str] = None
    dianping_rating: Optional[float] = None
    meituan_rating: Optional[float] = None
    merged_rating: Optional[float] = None
    dianping_reviews: Optional[str] = None
    meituan_reviews: Optional[str] = None
    dianping_images: Optional[str] = None
    meituan_images: Optional[str] = None
    last_dianping_update: Optional[datetime] = None
    last_meituan_update: Optional[datetime] = None
    cache_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 爬虫数据模型
class DianpingData(BaseModel):
    """点评数据模型"""
    rating: Optional[float] = None
    review_count: Optional[int] = None
    prices: Optional[list] = None
    reviews: Optional[list] = None
    images: Optional[list] = None
    description: Optional[str] = None
    facilities: Optional[str] = None
    business_hours: Optional[str] = None

class MeituanData(BaseModel):
    """美团数据模型"""
    rating: Optional[float] = None
    review_count: Optional[int] = None
    prices: Optional[list] = None
    reviews: Optional[list] = None
    images: Optional[list] = None
    description: Optional[str] = None
    facilities: Optional[str] = None
    business_hours: Optional[str] = None 