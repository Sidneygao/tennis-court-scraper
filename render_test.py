#!/usr/bin/env python3
"""
Render环境测试脚本
模拟Render部署环境进行测试
"""
import os
import sys

def simulate_render_environment():
    """模拟Render环境"""
    print("=== 模拟Render环境测试 ===")
    
    # 设置环境变量
    os.environ['PORT'] = '8000'
    os.environ['DATABASE_URL'] = 'sqlite:///./data/courts.db'
    os.environ['DEBUG'] = 'false'
    
    print(f"环境变量设置完成:")
    print(f"  PORT: {os.environ.get('PORT')}")
    print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"  DEBUG: {os.environ.get('DEBUG')}")

def test_path_resolution():
    """测试路径解析"""
    print("\n=== 路径解析测试 ===")
    
    # 获取当前工作目录
    cwd = os.getcwd()
    print(f"当前工作目录: {cwd}")
    
    # 测试app目录路径
    app_paths = [
        "app",
        "app/main.py", 
        "app/templates",
        "app/templates/index.html",
        "app/static",
        "app/static/css/style.css"
    ]
    
    for path in app_paths:
        full_path = os.path.join(cwd, path)
        exists = os.path.exists(full_path)
        print(f"{'✅' if exists else '❌'} {path}: {full_path}")
    
    return all(os.path.exists(os.path.join(cwd, path)) for path in app_paths)

def test_template_loading():
    """测试模板加载"""
    print("\n=== 模板加载测试 ===")
    
    try:
        from fastapi.templating import Jinja2Templates
        import os
        
        # 获取app目录的绝对路径
        cwd = os.getcwd()
        template_dir = os.path.join(cwd, "app", "templates")
        
        print(f"模板目录: {template_dir}")
        print(f"模板目录存在: {os.path.exists(template_dir)}")
        
        if os.path.exists(template_dir):
            templates = Jinja2Templates(directory=template_dir)
            template = templates.get_template("index.html")
            print("✅ 模板加载成功")
            return True
        else:
            print("❌ 模板目录不存在")
            return False
            
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_import():
    """测试应用导入"""
    print("\n=== 应用导入测试 ===")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.getcwd())
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_initialization():
    """测试数据库初始化"""
    print("\n=== 数据库初始化测试 ===")
    
    try:
        # 确保数据目录存在
        os.makedirs("data", exist_ok=True)
        print("✅ 数据目录创建/确认成功")
        
        # 测试数据库连接
        from app.database import init_db
        init_db()
        print("✅ 数据库初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始Render环境模拟测试...\n")
    
    # 模拟Render环境
    simulate_render_environment()
    
    # 运行各项测试
    tests = [
        ("路径解析", test_path_resolution),
        ("模板加载", test_template_loading),
        ("应用导入", test_app_import),
        ("数据库初始化", test_database_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！应用应该可以在Render上正常部署。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 