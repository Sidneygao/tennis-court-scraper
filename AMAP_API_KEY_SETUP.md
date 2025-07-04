# 高德地图API Key配置指南

## 1. 申请高德地图API Key

### 步骤：
1. 访问高德开放平台：https://lbs.amap.com/
2. 注册/登录账号
3. 进入"控制台" → "应用管理" → "创建新应用"
4. 填写应用名称（如：网球场地图生成器）
5. 选择"Web服务"类型
6. 创建完成后，在应用详情页面获取API Key

### 注意事项：
- 选择"Web服务"类型，支持静态地图API
- 免费额度：每天30万次调用
- 支持HTTPS和HTTP调用

## 2. 配置API Key到项目

### 方法一：环境变量（推荐）
```bash
# Windows PowerShell
$env:AMAP_KEY="your_amap_api_key_here"

# 或者设置永久环境变量
[Environment]::SetEnvironmentVariable("AMAP_KEY", "your_amap_api_key_here", "User")
```

### 方法二：.env文件
在项目根目录创建`.env`文件：
```
AMAP_KEY=your_amap_api_key_here
```

### 方法三：直接传入
在代码中直接传入API Key（不推荐，会暴露密钥）

## 3. 验证配置

运行以下命令验证API Key是否有效：
```bash
python -c "
import requests
key = 'your_amap_api_key_here'
url = f'https://restapi.amap.com/v3/staticmap?location=116.397428,39.90923&zoom=10&size=400*300&key={key}'
response = requests.get(url)
print('状态码:', response.status_code)
print('响应头:', response.headers.get('content-type', ''))
if response.status_code == 200:
    print('✅ API Key配置成功！')
else:
    print('❌ API Key配置失败，请检查密钥是否正确')
"
```

## 4. 使用说明

配置完成后，地图生成器会自动：
1. 优先使用高德地图静态API生成地图图片
2. 以场馆经纬度为中心，生成400x300像素的地图
3. 自动缓存到`data/map_cache/`目录
4. 将图片路径写入数据库`map_image`字段

## 5. 费用说明

- 免费额度：每天30万次调用
- 超出免费额度：按调用次数收费
- 建议：批量生成地图时控制频率，避免超出免费额度

## 6. 故障排除

### 常见问题：
1. **API Key无效**：检查密钥是否正确，是否选择了Web服务类型
2. **调用超限**：检查是否超出免费额度
3. **网络问题**：检查网络连接，确保能访问高德API
4. **图片生成失败**：检查经纬度格式是否正确

### 调试命令：
```bash
# 检查环境变量
echo $env:AMAP_KEY

# 测试API调用
python -c "import os; print('AMAP_KEY:', os.getenv('AMAP_KEY', '未设置'))"
``` 