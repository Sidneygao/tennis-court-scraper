#!/usr/bin/env python3
"""
Render部署启动脚本
专门用于Render环境的应用启动
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """设置环境"""
    logger.info("设置Render部署环境...")
    
    # 设置工作目录
    if os.path.exists("/opt/render/project/src"):
        os.chdir("/opt/render/project/src")
        logger.info("切换到Render项目目录: /opt/render/project/src")
    
    # 确保模板目录存在
    template_dir = "/opt/render/project/src/app/templates"
    os.makedirs(template_dir, exist_ok=True)
    
    # 如果index.html不存在，创建一个基本模板
    index_path = os.path.join(template_dir, "index.html")
    if not os.path.exists(index_path):
        logger.info("创建基本模板文件...")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>北京网球场馆信息抓取系统</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #333; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .status { 
            text-align: center; 
            color: #666; 
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .api-links { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            justify-content: center; 
            margin: 30px 0; 
        }
        .api-link { 
            padding: 15px 25px; 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white; 
            text-decoration: none; 
            border-radius: 8px; 
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .api-link:hover { 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.4);
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .info-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #007bff;
        }
        .info-card h3 {
            margin-top: 0;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎾 北京网球场馆信息抓取系统</h1>
        
        <div class="status">
            <h2>✅ 系统运行正常</h2>
            <p>模板文件已自动生成，系统已成功部署到Render</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📊 系统功能</h3>
                <ul>
                    <li>场馆信息抓取</li>
                    <li>价格预测分析</li>
                    <li>评论数据收集</li>
                    <li>实时数据更新</li>
                </ul>
            </div>
            <div class="info-card">
                <h3>🔧 技术栈</h3>
                <ul>
                    <li>FastAPI 后端</li>
                    <li>SQLite 数据库</li>
                    <li>Jinja2 模板</li>
                    <li>Uvicorn 服务器</li>
                </ul>
            </div>
        </div>
        
        <div class="api-links">
            <a href="/api/docs" class="api-link">📚 API文档</a>
            <a href="/api/courts/" class="api-link">🏟️ 场馆列表</a>
            <a href="/api/health" class="api-link">💚 健康检查</a>
            <a href="/api/info" class="api-link">ℹ️ 系统信息</a>
        </div>
        
        <div class="status">
            <p><strong>部署环境:</strong> Render</p>
            <p><strong>状态:</strong> 运行中</p>
            <p><strong>版本:</strong> v1.0.0</p>
        </div>
    </div>
</body>
</html>""")
        logger.info("基本模板文件创建完成")
    
    # 确保静态文件目录存在
    static_dir = "/opt/render/project/src/app/static"
    os.makedirs(static_dir, exist_ok=True)
    
    # 创建基本的CSS文件
    css_dir = os.path.join(static_dir, "css")
    os.makedirs(css_dir, exist_ok=True)
    css_path = os.path.join(css_dir, "style.css")
    if not os.path.exists(css_path):
        with open(css_path, "w", encoding="utf-8") as f:
            f.write("/* 基本样式文件 */\nbody { font-family: Arial, sans-serif; }")
    
    logger.info("环境设置完成")

def main():
    """主函数"""
    try:
        # 设置环境
        setup_environment()
        
        # 获取端口
        port = int(os.getenv("PORT", 8000))
        host = "0.0.0.0"
        
        logger.info(f"启动应用服务器...")
        logger.info(f"主机: {host}")
        logger.info(f"端口: {port}")
        logger.info(f"工作目录: {os.getcwd()}")
        
        # 启动服务器
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False  # Render环境中不需要reload
        )
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 