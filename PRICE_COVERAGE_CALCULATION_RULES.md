# 价格覆盖率计算规则

## 🚨 重要规则：价格覆盖率计算必须区分字段存在和实际数据

### ❌ 错误的计算方法
- 统计所有有 `bing_prices` 字段的场馆数量
- 将字段存在等同于有实际数据
- 导致覆盖率虚高（如显示100%）

### ✅ 正确的计算方法

#### 1. 字段覆盖率（仅供参考）
```sql
-- 统计有bing_prices字段的场馆数
SELECT COUNT(*) FROM tennis_courts tc
LEFT JOIN court_details cd ON tc.id = cd.court_id
WHERE cd.bing_prices IS NOT NULL
```

#### 2. 实际数据覆盖率（必须使用）
```sql
-- 统计有实际BING价格数据的场馆数
SELECT COUNT(*) FROM tennis_courts tc
LEFT JOIN court_details cd ON tc.id = cd.court_id
WHERE cd.bing_prices IS NOT NULL 
AND cd.bing_prices != '[]'
AND cd.bing_prices != 'null'
AND json_array_length(cd.bing_prices) > 0
```

#### 3. 有效价格覆盖率（最准确）
```python
# 统计有有效价格数据的场馆数
def count_real_bing_coverage():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT tc.id, tc.name, cd.bing_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        ORDER BY tc.id
    """)
    
    results = cursor.fetchall()
    
    total_courts = len(results)
    has_bing_prices_field = 0
    has_actual_prices = 0
    empty_arrays = 0
    null_fields = 0
    
    for court_id, name, bing_prices in results:
        if bing_prices is None:
            null_fields += 1
        else:
            has_bing_prices_field += 1
            try:
                prices = json.loads(bing_prices)
                if isinstance(prices, list) and len(prices) > 0:
                    has_actual_prices += 1
                else:
                    empty_arrays += 1
            except:
                empty_arrays += 1
    
    print(f"总场馆数: {total_courts}")
    print(f"有bing_prices字段: {has_bing_prices_field}")
    print(f"有实际价格数据: {has_actual_prices}")
    print(f"空数组: {empty_arrays}")
    print(f"空字段: {null_fields}")
    print(f"实际覆盖率: {has_actual_prices}/{total_courts} = {has_actual_prices/total_courts*100:.1f}%")
```

## 🚨 价格预测算法规则

### ❌ 错误的做法
- 发现16KM内有效数据不足2家时，立即放弃进入通用算法
- 不检查算法逻辑，直接使用粗糙的通用模型
- 没有验证数据不足的真实原因

### ✅ 正确的做法

#### 1. 算法检查步骤
```python
def check_prediction_algorithm():
    """
    当发现有效数据不足时，按以下步骤检查：
    """
    # 步骤1: 检查数据源
    check_data_sources()
    
    # 步骤2: 检查算法参数
    check_algorithm_parameters()
    
    # 步骤3: 检查距离计算
    check_distance_calculation()
    
    # 步骤4: 检查价格字段识别
    check_price_field_recognition()
    
    # 步骤5: 检查置信度模型
    check_confidence_model()
    
    # 步骤6: 只有在确认算法无误后才使用通用模型
    if all_checks_passed:
        use_general_algorithm()
    else:
        fix_algorithm_issues()
```

#### 2. 数据源检查
- 确认 `bing_prices` 字段是否被正确识别
- 确认 `merged_prices` 字段是否包含有效数据
- 确认价格预测算法是否支持所有价格字段

#### 3. 算法参数检查
- 检查16KM距离阈值是否合理
- 检查最少有效数据要求（2家）是否过高
- 检查价格字段权重分配是否合理

#### 4. 距离计算检查
- 确认GeoJSON坐标计算是否正确
- 确认经纬度数据是否有效
- 确认距离计算公式是否准确

#### 5. 价格字段识别检查
- 确认算法能识别 `bing_prices` 字段
- 确认算法能识别 `merged_prices` 字段
- 确认价格数据格式解析是否正确

#### 6. 置信度模型检查
- 确认置信度模型是否正常工作
- 确认正态分布模型是否基于最新数据
- 确认置信度计算是否动态更新

### 📋 验证清单
在进入通用算法之前，必须完成以下检查：

- [ ] 数据源完整性检查
- [ ] 算法参数合理性检查
- [ ] 距离计算准确性检查
- [ ] 价格字段识别检查
- [ ] 置信度模型状态检查
- [ ] 历史数据有效性检查

### 🎯 永久规则
**如果发现成功价格预测逻辑基础数据不足，不要急于放弃进入粗糙的通用模型，必须先检查算法。**

这个规则确保：
1. 不会因为算法问题而误判数据不足
2. 不会因为配置错误而使用低质量预测
3. 保证预测结果的准确性和可靠性

## 📊 历史错误记录

### 2025-06-29 错误案例
- **错误描述**: 误报BING价格覆盖率100%，实际只有15.8%
- **错误原因**: 混淆了字段存在和实际数据的概念
- **解决方案**: 建立正确的统计方法，区分字段覆盖率和数据覆盖率
- **预防措施**: 使用三层统计方法，确保数据准确性

### 2025-06-29 算法检查案例
- **问题描述**: 价格预测算法报告16KM内有效数据不足
- **检查结果**: 发现算法未正确识别 `bing_prices` 字段
- **解决方案**: 修改算法支持所有价格字段
- **预防措施**: 建立算法检查清单，避免误判

## ⚠️ 注意事项

1. **永远不要做多余的事儿**，尤其不要自作主张修改前端渲染
2. **临时性测试脚本1小时后删除**
3. **如果声明是某计算的永久规则，就不要再改回**
4. **Always respond in Chinese-simplified**
5. **修改代码时，不要修改和增加无关部分，如果需要修改和增加请征求同意**
6. **每次计算场馆类型时，使用三层判断法**
7. **场馆类型的三层次判断法和GeoJSON+2KM步进法不经确认不可以删改**
8. **BING爬取价格的置信度模型必须基于真实价格驱动的迭代动态模型**

### 📝 历史错误记录

**错误时间**: 2025-06-29
**错误描述**: 将BING价格覆盖率计算为100% (552/552)
**错误原因**: 混淆了字段存在和实际数据的概念
**正确结果**: 实际覆盖率约为15.8% (87/552)
**影响**: 误导了数据质量评估

### 🔄 修正措施

1. 建立此规则文档
2. 修改所有相关统计脚本
3. 定期验证统计准确性
4. 在报告中使用正确的覆盖率数据

---

**规则制定时间**: 2025-06-30
**规则状态**: 永久规则，不得修改
**适用范围**: 所有价格覆盖率计算 

# 价格覆盖率与2KM步进法算法规则

## 【永久规则】2KM步进法数据利用

- 2KM步进法如发现有效数据不足，**必须先检查算法实现和数据识别**，不能直接进入粗糙的通用模型。
- 所有场馆均需优先利用BING/真实价格数据，只有在算法确认无有效数据时才允许进入通用模型。
- 每次算法升级需以典型区域（如双井、国贸、望京等）为例进行专项验证，确保逻辑无误后方可批量应用。
- 验证内容包括：
  1. 算法能否正确识别并利用BING/真实价格
  2. 不能因字段解析或类型不符导致误判"有效数据不足"
  3. 典型区域专项验证通过后，方可全量批量预测

---

## 典型错误示例归档
- 字段存在但无实际数据时，不能计入覆盖率
- 价格类型不符导致算法无法利用真实数据，需及时修正
- 典型区域专项验证未通过时，禁止批量应用 