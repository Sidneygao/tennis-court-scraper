#!/usr/bin/env python3
"""
简化的Render启动脚本
"""

import os
import sys
import uvicorn

def setup_render_environment():
    """设置Render环境"""
    print("🔧 设置Render环境...")
    
    # 设置工作目录
    if os.path.exists("/opt/render/project/src"):
        os.chdir("/opt/render/project/src")
        print("✅ 切换到Render项目目录")
    
    # 确保模板目录存在
    template_dir = "/opt/render/project/src/app/templates"
    os.makedirs(template_dir, exist_ok=True)
    print(f"✅ 模板目录: {template_dir}")
    
    # 创建index.html
    index_path = os.path.join(template_dir, "index.html")
    if not os.path.exists(index_path):
        print("📝 创建index.html...")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>北京网球场馆信息抓取系统</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .links { text-align: center; margin: 20px 0; }
        .link { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎾 北京网球场馆信息抓取系统</h1>
        <p style="text-align: center; color: #666;">系统运行正常</p>
        <div class="links">
            <a href="/api/docs" class="link">API文档</a>
            <a href="/api/courts/" class="link">场馆列表</a>
            <a href="/api/health" class="link">健康检查</a>
        </div>
    </div>
</body>
</html>""")
        print("✅ index.html创建完成")
    
    # 确保静态文件目录存在
    static_dir = "/opt/render/project/src/app/static"
    os.makedirs(static_dir, exist_ok=True)
    print(f"✅ 静态文件目录: {static_dir}")
    
    print("✅ 环境设置完成")

def main():
    """主函数"""
    try:
        # 设置环境
        setup_render_environment()
        
        # 获取端口
        port = int(os.getenv("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"🚀 启动应用服务器...")
        print(f"   主机: {host}")
        print(f"   端口: {port}")
        print(f"   工作目录: {os.getcwd()}")
        
        # 启动服务器
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 