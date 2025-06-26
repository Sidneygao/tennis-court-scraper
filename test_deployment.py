#!/usr/bin/env python3
"""
部署测试脚本 - 检查Render部署环境
"""
import os
import sys

def check_paths():
    """检查关键路径"""
    print("=== 路径检查 ===")
    
    # 检查当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查关键文件
    key_files = [
        "app/main.py",
        "app/templates/index.html",
        "app/static/css/style.css",
        "requirements.txt",
        "render.yaml"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
    
    # 检查目录结构
    print("\n=== 目录结构 ===")
    for root, dirs, files in os.walk("app", topdown=True):
        level = root.replace("app", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:  # 只显示前5个文件
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... 还有 {len(files) - 5} 个文件")

def check_imports():
    """检查关键模块导入"""
    print("\n=== 模块导入检查 ===")
    
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI 导入失败: {e}")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn 导入失败: {e}")
    
    try:
        import jinja2
        print(f"✅ Jinja2 {jinja2.__version__}")
    except ImportError as e:
        print(f"❌ Jinja2 导入失败: {e}")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ SQLAlchemy 导入失败: {e}")

def check_app_import():
    """检查应用导入"""
    print("\n=== 应用导入检查 ===")
    
    try:
        from app.main import app
        print("✅ 应用导入成功")
        
        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"✅ 找到 {len(routes)} 个路由")
        for route in routes[:5]:
            print(f"  - {route}")
        
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        import traceback
        traceback.print_exc()

def check_template_loading():
    """检查模板加载"""
    print("\n=== 模板加载检查 ===")
    
    try:
        from fastapi.templating import Jinja2Templates
        import os
        
        # 获取app目录的绝对路径
        app_dir = os.path.dirname(os.path.abspath("app/main.py"))
        template_dir = os.path.join(app_dir, "templates")
        
        print(f"模板目录: {template_dir}")
        print(f"模板目录存在: {os.path.exists(template_dir)}")
        
        if os.path.exists(template_dir):
            templates = Jinja2Templates(directory=template_dir)
            template = templates.get_template("index.html")
            print("✅ 模板加载成功")
        else:
            print("❌ 模板目录不存在")
            
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始部署环境检查...\n")
    
    check_paths()
    check_imports()
    check_app_import()
    check_template_loading()
    
    print("\n✅ 部署环境检查完成") 