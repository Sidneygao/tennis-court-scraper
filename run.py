#!/usr/bin/env python3
"""
网球场地信息抓取系统启动脚本
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    # 强制检查当前工作目录
    if Path.cwd().name != 'tennis_court_scraper':
        print("\n" + "❌" * 20)
        print("错误：必须在 'tennis_court_scraper' 目录下运行此脚本！")
        print(f"当前目录是: {Path.cwd()}")
        print("请先执行 `cd tennis_court_scraper` 进入正确目录后再运行。")
        print("❌" * 20 + "\n")
        sys.exit(1)
        
    print("🎾 北京网球场馆信息抓取系统")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 启动应用
    print("正在启动应用...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def check_environment():
    """检查运行环境"""
    print("检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要目录
    data_dir = project_root / "data"
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        print("✅ 创建数据目录")
    
    # 检查环境变量
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  警告：未找到.env文件，将使用默认配置")
        print("   请复制env.example为.env并配置必要的环境变量")
    
    print("✅ 环境检查完成")

if __name__ == "__main__":
    main() 