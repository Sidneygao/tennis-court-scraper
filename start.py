#!/usr/bin/env python3
"""
Render部署启动脚本
"""
import os
import sys
import uvicorn

def check_environment():
    """检查部署环境"""
    print("=== 部署环境检查 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print(f"环境变量PORT: {os.getenv('PORT', '未设置')}")
    
    # 检查关键文件
    key_files = [
        "app/main.py",
        "app/templates/index.html",
        "requirements.txt"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 不存在")
            return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动北京网球场馆信息抓取系统...")
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，退出")
        sys.exit(1)
    
    # 获取端口
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🌐 启动服务器: {host}:{port}")
    
    try:
        # 启动应用
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 