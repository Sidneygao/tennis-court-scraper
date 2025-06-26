#!/usr/bin/env python3
"""
Render部署测试脚本
用于测试Render环境中的关键功能
"""

import os
import sys
import requests
import time
import json

def test_environment():
    """测试环境配置"""
    print("🔍 测试环境配置...")
    
    # 检查环境变量
    env_vars = ['PORT', 'DATABASE_URL', 'DEBUG', 'RENDER']
    for var in env_vars:
        value = os.getenv(var, '未设置')
        print(f"  {var}: {value}")
    
    # 检查文件系统
    paths = [
        '/opt/render/project/src',
        '/opt/render/project/src/app',
        '/opt/render/project/src/app/templates',
        '/opt/render/project/src/app/static'
    ]
    
    for path in paths:
        exists = os.path.exists(path)
        print(f"  {path}: {'✅ 存在' if exists else '❌ 不存在'}")
    
    print()

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        import fastapi
        print(f"  ✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"  ❌ FastAPI: {e}")
    
    try:
        import uvicorn
        print(f"  ✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"  ❌ Uvicorn: {e}")
    
    try:
        import sqlalchemy
        print(f"  ✅ SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"  ❌ SQLAlchemy: {e}")
    
    try:
        import jinja2
        print(f"  ✅ Jinja2: {jinja2.__version__}")
    except ImportError as e:
        print(f"  ❌ Jinja2: {e}")
    
    print()

def test_app_import():
    """测试应用导入"""
    print("🚀 测试应用导入...")
    
    try:
        # 添加项目路径
        sys.path.insert(0, '/opt/render/project/src')
        
        import app.main
        print("  ✅ 应用模块导入成功")
        
        # 检查模板配置
        template_dir = getattr(app.main, 'TEMPLATE_DIR', None)
        if template_dir:
            print(f"  ✅ 模板目录: {template_dir}")
            print(f"    目录存在: {os.path.exists(template_dir)}")
            
            index_path = os.path.join(template_dir, "index.html")
            print(f"    index.html存在: {os.path.exists(index_path)}")
        else:
            print("  ⚠️  模板目录未配置")
        
    except Exception as e:
        print(f"  ❌ 应用模块导入失败: {e}")
    
    print()

def test_web_server(base_url="http://localhost:8000"):
    """测试Web服务器"""
    print(f"🌐 测试Web服务器 ({base_url})...")
    
    endpoints = [
        "/",
        "/api/health",
        "/api/info",
        "/api/docs",
        "/api/courts/"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"  {status} {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint}: {e}")
    
    print()

def test_database():
    """测试数据库连接"""
    print("🗄️  测试数据库连接...")
    
    try:
        sys.path.insert(0, '/opt/render/project/src')
        from app.database import get_db
        from app.models import TennisCourt
        
        # 获取数据库会话
        db = next(get_db())
        
        # 测试查询
        court_count = db.query(TennisCourt).count()
        print(f"  ✅ 数据库连接成功")
        print(f"    场馆数量: {court_count}")
        
        db.close()
        
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {e}")
    
    print()

def main():
    """主测试函数"""
    print("🧪 Render部署测试")
    print("=" * 50)
    
    # 1. 环境测试
    test_environment()
    
    # 2. 模块导入测试
    test_imports()
    
    # 3. 应用导入测试
    test_app_import()
    
    # 4. 数据库测试
    test_database()
    
    # 5. Web服务器测试（如果服务器正在运行）
    print("🌐 尝试连接Web服务器...")
    print("注意: 如果服务器未运行，此测试将失败")
    test_web_server()
    
    print("✅ 测试完成")
    print("\n建议:")
    print("1. 如果所有测试都通过，说明部署配置正确")
    print("2. 如果有失败的测试，请检查相应的配置")
    print("3. 确保所有依赖都已正确安装")
    print("4. 检查环境变量是否正确设置")

if __name__ == "__main__":
    main() 