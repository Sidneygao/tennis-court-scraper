#!/usr/bin/env python3
"""
Render部署环境诊断脚本
用于排查Render部署中的常见问题
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_file_exists(path, description):
    """检查文件是否存在"""
    exists = os.path.exists(path)
    status = "✅ 存在" if exists else "❌ 不存在"
    print(f"{description}: {status} ({path})")
    return exists

def check_directory_contents(path, description):
    """检查目录内容"""
    print(f"\n{description}: {path}")
    if os.path.exists(path):
        try:
            items = os.listdir(path)
            if items:
                for item in items[:10]:  # 只显示前10个
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        print(f"  📁 {item}/")
                    else:
                        print(f"  📄 {item}")
                if len(items) > 10:
                    print(f"  ... 还有 {len(items) - 10} 个文件")
            else:
                print("  (空目录)")
        except Exception as e:
            print(f"  ❌ 无法读取目录: {e}")
    else:
        print("  ❌ 目录不存在")

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{description}:")
    print(f"命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ 命令执行成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()}")
        else:
            print(f"❌ 命令执行失败 (返回码: {result.returncode})")
            if result.stderr.strip():
                print(f"错误: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

def main():
    """主诊断函数"""
    print("🔍 Render部署环境诊断")
    print(f"诊断时间: {os.popen('date').read().strip()}")
    
    # 1. 环境信息
    print_section("环境信息")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"用户: {os.getenv('USER', 'unknown')}")
    print(f"环境变量HOME: {os.getenv('HOME', 'not set')}")
    print(f"环境变量PWD: {os.getenv('PWD', 'not set')}")
    
    # 2. 文件系统检查
    print_section("文件系统检查")
    
    # 检查关键目录
    check_directory_contents("/opt/render/project/src", "Render项目根目录")
    check_directory_contents("/opt/render/project/src/app", "应用目录")
    check_directory_contents("/opt/render/project/src/app/templates", "模板目录")
    check_directory_contents("/opt/render/project/src/app/static", "静态文件目录")
    
    # 检查关键文件
    check_file_exists("/opt/render/project/src/requirements.txt", "requirements.txt")
    check_file_exists("/opt/render/project/src/app/main.py", "main.py")
    check_file_exists("/opt/render/project/src/app/templates/index.html", "index.html")
    check_file_exists("/opt/render/project/src/render.yaml", "render.yaml")
    
    # 3. Python环境检查
    print_section("Python环境检查")
    
    # 检查Python包
    run_command("pip list", "已安装的Python包")
    run_command("python -c 'import fastapi; print(f\"FastAPI版本: {fastapi.__version__}\")'", "FastAPI版本")
    run_command("python -c 'import uvicorn; print(f\"Uvicorn版本: {uvicorn.__version__}\")'", "Uvicorn版本")
    
    # 4. 应用启动测试
    print_section("应用启动测试")
    
    # 检查应用是否可以导入
    try:
        sys.path.insert(0, '/opt/render/project/src')
        import app.main
        print("✅ 应用模块导入成功")
        
        # 检查模板配置
        template_dir = app.main.TEMPLATE_DIR
        print(f"模板目录配置: {template_dir}")
        print(f"模板目录存在: {os.path.exists(template_dir)}")
        
        if os.path.exists(template_dir):
            index_path = os.path.join(template_dir, "index.html")
            print(f"index.html存在: {os.path.exists(index_path)}")
        
    except Exception as e:
        print(f"❌ 应用模块导入失败: {e}")
    
    # 5. 网络和端口检查
    print_section("网络和端口检查")
    run_command("netstat -tlnp", "监听端口")
    run_command("curl -s http://localhost:8000/api/health", "本地健康检查")
    
    # 6. 系统资源
    print_section("系统资源")
    run_command("df -h", "磁盘使用情况")
    run_command("free -h", "内存使用情况")
    run_command("ps aux | grep python", "Python进程")
    
    # 7. 日志检查
    print_section("日志检查")
    log_files = [
        "/var/log/render.log",
        "/opt/render/project/src/app.log",
        "/tmp/app.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"📄 日志文件: {log_file}")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    print(f"  最后10行:")
                    for line in lines[-10:]:
                        print(f"    {line.strip()}")
            except Exception as e:
                print(f"  ❌ 无法读取日志: {e}")
    
    print_section("诊断完成")
    print("如果发现问题，请检查:")
    print("1. 文件路径是否正确")
    print("2. 依赖是否安装完整")
    print("3. 环境变量是否配置正确")
    print("4. 端口是否被占用")
    print("5. 权限是否足够")

if __name__ == "__main__":
    main() 