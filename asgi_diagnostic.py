#!/usr/bin/env python3
"""
ASGI错误诊断脚本
专门用于诊断和解决ASGI应用程序异常
"""
import os
import sys
import traceback
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """检查环境配置"""
    logger.info("=== 环境检查 ===")
    
    # Python版本
    logger.info(f"Python版本: {sys.version}")
    
    # 工作目录
    logger.info(f"当前工作目录: {os.getcwd()}")
    
    # 环境变量
    env_vars = ['PORT', 'DATABASE_URL', 'DEBUG', 'PYTHONPATH']
    for var in env_vars:
        value = os.getenv(var, '未设置')
        logger.info(f"环境变量 {var}: {value}")
    
    return True

def check_dependencies():
    """检查依赖"""
    logger.info("=== 依赖检查 ===")
    
    dependencies = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'sqlalchemy',
        'requests',
        'beautifulsoup4'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', '未知版本')
            logger.info(f"✅ {dep}: {version}")
        except ImportError:
            logger.error(f"❌ {dep}: 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        logger.error(f"缺少依赖: {missing_deps}")
        return False
    
    return True

def check_file_structure():
    """检查文件结构"""
    logger.info("=== 文件结构检查 ===")
    
    required_files = [
        'app/main.py',
        'app/templates/index.html',
        'app/static/css/style.css',
        'requirements.txt',
        'render.yaml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path}: 不存在")
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"缺少文件: {missing_files}")
        return False
    
    return True

def test_app_import():
    """测试应用导入"""
    logger.info("=== 应用导入测试 ===")
    
    try:
        # 添加当前目录到Python路径
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        # 测试导入各个模块
        logger.info("测试导入 app.config...")
        from app import config
        
        logger.info("测试导入 app.database...")
        from app import database
        
        logger.info("测试导入 app.models...")
        from app import models
        
        logger.info("测试导入 app.main...")
        from app.main import app
        
        logger.info("✅ 所有模块导入成功")
        
        # 检查应用配置
        logger.info(f"应用标题: {app.title}")
        logger.info(f"应用版本: {app.version}")
        logger.info(f"路由数量: {len(app.routes)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 应用导入失败: {e}")
        logger.error(traceback.format_exc())
        return False

def test_template_loading():
    """测试模板加载"""
    logger.info("=== 模板加载测试 ===")
    
    try:
        from app.main import templates, TEMPLATE_DIR
        
        if templates is None:
            logger.error("❌ 模板系统未初始化")
            return False
        
        # 检查模板目录
        logger.info(f"模板目录: {TEMPLATE_DIR}")
        
        if not os.path.exists(TEMPLATE_DIR):
            logger.error(f"❌ 模板目录不存在: {TEMPLATE_DIR}")
            return False
        
        # 检查index.html
        index_path = os.path.join(TEMPLATE_DIR, 'index.html')
        if not os.path.exists(index_path):
            logger.error(f"❌ index.html不存在: {index_path}")
            return False
        
        logger.info("✅ 模板加载测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 模板加载测试失败: {e}")
        logger.error(traceback.format_exc())
        return False

def test_database_connection():
    """测试数据库连接"""
    logger.info("=== 数据库连接测试 ===")
    
    try:
        from app.database import init_db
        
        # 初始化数据库
        init_db()
        logger.info("✅ 数据库初始化成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """主函数"""
    logger.info("🔍 开始ASGI错误诊断...")
    
    # 执行各项检查
    checks = [
        check_environment,
        check_dependencies,
        check_file_structure,
        test_app_import,
        test_template_loading,
        test_database_connection
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            logger.error(f"检查失败: {e}")
            results.append(False)
    
    # 总结
    logger.info("=== 诊断总结 ===")
    passed = sum(results)
    total = len(results)
    
    logger.info(f"通过检查: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ 所有检查通过，应用应该可以正常启动")
        return True
    else:
        logger.error("❌ 部分检查失败，请查看上面的错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 