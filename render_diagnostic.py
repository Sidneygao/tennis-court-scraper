#!/usr/bin/env python3
"""
Render环境诊断脚本
专门用于诊断Render部署环境中的路径问题
"""
import os
import sys

def check_render_environment():
    """检查Render环境"""
    print("=== Render环境诊断 ===")
    
    # 基本信息
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"环境变量:")
    for key in ['PORT', 'DATABASE_URL', 'DEBUG', 'RENDER']:
        value = os.getenv(key, '未设置')
        print(f"  {key}: {value}")
    
    # 检查目录结构
    print("\n=== 目录结构检查 ===")
    
    # 检查可能的项目根目录
    possible_roots = [
        os.getcwd(),
        "/opt/render/project/src",
        "/app",
        "/workspace"
    ]
    
    for root in possible_roots:
        if os.path.exists(root):
            print(f"\n检查目录: {root}")
            try:
                # 列出目录内容
                items = os.listdir(root)
                print(f"  目录内容: {items[:10]}...")  # 只显示前10个
                
                # 检查关键文件
                key_files = ['app', 'requirements.txt', 'render.yaml', 'start.py']
                for file in key_files:
                    path = os.path.join(root, file)
                    if os.path.exists(path):
                        print(f"  ✅ {file}: {path}")
                    else:
                        print(f"  ❌ {file}: 不存在")
                        
            except Exception as e:
                print(f"  无法访问目录: {e}")
    
    # 检查app目录结构
    print("\n=== App目录结构检查 ===")
    app_paths = [
        "app",
        "/opt/render/project/src/app",
        os.path.join(os.getcwd(), "app")
    ]
    
    for app_path in app_paths:
        if os.path.exists(app_path):
            print(f"\n检查App目录: {app_path}")
            try:
                # 检查templates目录
                templates_path = os.path.join(app_path, "templates")
                if os.path.exists(templates_path):
                    print(f"  ✅ templates目录存在: {templates_path}")
                    
                    # 检查index.html
                    index_path = os.path.join(templates_path, "index.html")
                    if os.path.exists(index_path):
                        print(f"  ✅ index.html存在: {index_path}")
                        # 检查文件大小
                        size = os.path.getsize(index_path)
                        print(f"    文件大小: {size} 字节")
                    else:
                        print(f"  ❌ index.html不存在")
                        
                    # 列出templates目录内容
                    try:
                        template_files = os.listdir(templates_path)
                        print(f"    templates目录内容: {template_files}")
                    except Exception as e:
                        print(f"    无法列出templates目录内容: {e}")
                else:
                    print(f"  ❌ templates目录不存在")
                
                # 检查static目录
                static_path = os.path.join(app_path, "static")
                if os.path.exists(static_path):
                    print(f"  ✅ static目录存在: {static_path}")
                else:
                    print(f"  ❌ static目录不存在")
                    
            except Exception as e:
                print(f"  检查App目录时出错: {e}")

def test_template_loading():
    """测试模板加载"""
    print("\n=== 模板加载测试 ===")
    
    try:
        from fastapi.templating import Jinja2Templates
        import os
        
        # 测试不同的模板路径
        test_paths = [
            "app/templates",
            "/opt/render/project/src/app/templates",
            os.path.join(os.getcwd(), "app", "templates"),
            os.path.join(os.getcwd(), "templates")
        ]
        
        for path in test_paths:
            print(f"\n测试路径: {path}")
            if os.path.exists(path):
                print(f"  ✅ 路径存在")
                if os.path.exists(os.path.join(path, "index.html")):
                    print(f"  ✅ index.html存在")
                    try:
                        templates = Jinja2Templates(directory=path)
                        template = templates.get_template("index.html")
                        print(f"  ✅ 模板加载成功")
                    except Exception as e:
                        print(f"  ❌ 模板加载失败: {e}")
                else:
                    print(f"  ❌ index.html不存在")
            else:
                print(f"  ❌ 路径不存在")
                
    except Exception as e:
        print(f"模板加载测试失败: {e}")

def main():
    """主函数"""
    print("🔍 开始Render环境诊断...\n")
    
    check_render_environment()
    test_template_loading()
    
    print("\n✅ 诊断完成")
    print("\n建议:")
    print("1. 检查Render构建日志中的文件路径")
    print("2. 确认所有文件都已正确推送到GitHub")
    print("3. 检查render.yaml配置是否正确")
    print("4. 查看Render的构建和部署日志")

if __name__ == "__main__":
    main() 