# 价格功能更新摘要

## 概述
本文档记录了网球场地信息系统中价格功能的完整实现，包括智能价格预测、多源价格获取、价格融合和批量更新等功能。

## 功能模块

### 1. 智能价格预测器 (app/scrapers/price_predictor.py)
**功能**: 基于场馆特征智能预测价格

**预测因素**:
- **区域基准价格**: 不同区域的价格基准
- **场地类型调整**: 室内/室外/专业场馆的价格倍数
- **设施加成**: 各种设施对价格的影响

**区域价格基准**:
```python
area_base_prices = {
    "wangjing": {"min": 80, "max": 150, "avg": 120},    # 望京科技商务区
    "dongba": {"min": 60, "max": 120, "avg": 90},       # 东坝-第四使馆区
    "jiuxianqiao": {"min": 70, "max": 130, "avg": 100}, # 酒仙桥
    "guomao": {"min": 100, "max": 200, "avg": 150},     # 国贸CBD核心区
    "sanlitun": {"min": 120, "max": 250, "avg": 180},   # 三里屯-工体时尚区
    # ... 其他区域
}
```

**场地类型调整**:
```python
court_type_multipliers = {
    "室内": 1.2,    # 室内场地价格更高
    "室外": 0.9,    # 室外场地价格较低
    "网球场": 1.0,  # 标准价格
    "网球馆": 1.3   # 专业场馆价格更高
}
```

**设施加成**:
```python
facility_bonuses = {
    "免费停车": 5,
    "淋浴设施": 10,
    "更衣室": 8,
    "休息区": 5,
    "专业教练": 15,
    "器材出租": 8,
    "空调": 12,
    "WiFi": 3
}
```

### 2. 批量价格获取器 (batch_price_fetcher.py)
**功能**: 从多个来源批量获取价格数据

**工作流程**:
1. **智能预测**: 使用价格预测器生成预测价格
2. **真实价格获取**: 从详情爬虫获取真实价格
3. **价格融合**: 将预测价格和真实价格融合
4. **数据库更新**: 更新主表和详情表

**并发处理**: 支持多线程并发获取，提高效率

### 3. 价格融合策略
**优先级**:
1. **真实价格** (置信度: 1.0) - 从点评/美团等平台获取
2. **预测价格** (置信度: 0.8-0.9) - 智能预测生成

**价格类型**:
- 黄金时间价格
- 非黄金时间价格  
- 会员价格

## 使用方法

### 1. 单个场馆价格预测
```python
from app.scrapers.price_predictor import PricePredictor

predictor = PricePredictor()
prediction = predictor.predict_price(court)
print(prediction)
```

### 2. 批量价格获取
```python
from batch_price_fetcher import BatchPriceFetcher

fetcher = BatchPriceFetcher()
result = fetcher.batch_fetch_prices(max_workers=3, limit=20)
print(result)
```

### 3. 直接运行批量获取
```bash
python batch_price_fetcher.py
```

## 数据库更新

### 主表 (tennis_courts)
- `peak_price`: 黄金时间价格
- `off_peak_price`: 非黄金时间价格
- `member_price`: 会员价格
- `price_unit`: 价格单位
- `price_updated_at`: 价格更新时间

### 详情表 (court_details)
- `merged_prices`: 融合后的价格信息 (JSON格式)
- `updated_at`: 更新时间

## 前端显示

### 价格显示逻辑
1. **真实价格优先**: 显示从平台获取的真实价格
2. **预测价格标识**: 预测价格显示"预测"标签
3. **价格不可获得**: 显示"该数据不能获得"

### 价格卡片样式
```css
.predicted-price {
    background: #ffc107;
    color: #000;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.8em;
    margin-right: 5px;
}

.price-value.unavailable {
    color: #dc3545;
}
```

## 性能优化

### 1. 并发处理
- 使用ThreadPoolExecutor进行并发价格获取
- 默认并发数: 3个线程
- 可配置并发数避免被反爬

### 2. 缓存机制
- 价格数据缓存24小时
- 避免重复获取相同数据

### 3. 错误处理
- 完善的异常处理机制
- 失败重试机制
- 详细的日志记录

## 监控和日志

### 日志文件
- `batch_price_fetch.log`: 批量获取日志
- `batch_price_results_YYYYMMDD_HHMMSS.json`: 结果文件

### 监控指标
- 成功率统计
- 处理时间统计
- 错误类型分析

## 更新历史

### 2025-06-27
- ✅ 实现智能价格预测器
- ✅ 实现批量价格获取器
- ✅ 实现价格融合策略
- ✅ 完善前端价格显示
- ✅ 添加价格更新摘要文档

## 注意事项

1. **反爬虫**: 批量获取时注意控制频率，避免被平台封禁
2. **数据准确性**: 预测价格仅供参考，真实价格更准确
3. **更新频率**: 建议每天更新一次价格数据
4. **备份**: 更新前建议备份数据库

## 未来改进

1. **机器学习**: 使用ML模型提高预测准确性
2. **更多数据源**: 增加更多价格数据源
3. **实时更新**: 实现价格实时更新机制
4. **价格趋势**: 分析价格变化趋势 