#!/usr/bin/env python3
"""
简化启动脚本 - 用于测试应用启动
"""
import os
import sys
import uvicorn
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """测试关键模块导入"""
    logger.info("=== 测试模块导入 ===")
    
    try:
        import fastapi
        logger.info(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        logger.error(f"❌ FastAPI 导入失败: {e}")
        return False
    
    try:
        import uvicorn
        logger.info(f"✅ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        logger.error(f"❌ Uvicorn 导入失败: {e}")
        return False
    
    try:
        import jinja2
        logger.info(f"✅ Jinja2 {jinja2.__version__}")
    except ImportError as e:
        logger.error(f"❌ Jinja2 导入失败: {e}")
        return False
    
    return True

def test_app_import():
    """测试应用导入"""
    logger.info("=== 测试应用导入 ===")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.getcwd())
        
        from app.main import app
        logger.info("✅ 应用导入成功")
        
        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        logger.info(f"✅ 找到 {len(routes)} 个路由")
        return True
        
    except Exception as e:
        logger.error(f"❌ 应用导入失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """主函数"""
    logger.info("🚀 开始简化启动测试...")
    
    # 检查环境
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"Python版本: {sys.version}")
    
    # 测试导入
    if not test_imports():
        logger.error("❌ 模块导入测试失败")
        return False
    
    if not test_app_import():
        logger.error("❌ 应用导入测试失败")
        return False
    
    # 获取端口
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🌐 启动服务器: {host}:{port}")
    
    try:
        # 启动应用
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 