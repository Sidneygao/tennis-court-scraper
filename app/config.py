import os
from typing import Optional, Dict, List, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "北京网球场馆信息抓取系统"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "sqlite:///./data/courts.db"
    
    # 高德地图API配置
    amap_api_key: Optional[str] = None
    amap_base_url: str = "https://restapi.amap.com/v3"
    
    # 爬虫配置
    request_delay: float = 1.0  # 请求间隔（秒）
    max_retries: int = 3
    timeout: int = 30
    
    # 用户代理配置
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]
    
    target_areas: Dict[str, dict] = {
        "guomao": {
            "name": "国贸CBD核心区",
            "center": "116.468,39.914",
            "radius": 5000
        },
        "sanlitun": {
            "name": "三里屯-工体时尚区",
            "center": "116.453,39.933",
            "radius": 5000
        },
        "wangjing": {
            "name": "望京科技商务区",
            "center": "116.4828,39.9968",
            "radius": 5000
        },
        "aoyuncun": {
            "name": "奥运村-亚运村文体区",
            "center": "116.396,40.008",
            "radius": 5000
        },
        "chaoyangpark": {
            "name": "朝阳公园-蓝色港湾生态区",
            "center": "116.478,39.946",
            "radius": 5000
        },
        "dawanglu": {
            "name": "大望路-华贸商业区",
            "center": "116.489,39.914",
            "radius": 5000
        },
        "shuangjing": {
            "name": "双井-富力城居住区",
            "center": "116.468,39.894",
            "radius": 5000
        },
        "gaobeidian": {
            "name": "高碑店-传媒文化区",
            "center": "116.525,39.908",
            "radius": 5000
        },
        "dongba": {
            "name": "东坝-第四使馆区",
            "center": "116.5607,39.9582",
            "radius": 5000
        },
        "changying": {
            "name": "常营-东坝边缘居住区",
            "center": "116.601,39.933",
            "radius": 5000
        },
        "sanyuanqiao": {
            "name": "三元桥-太阳宫国际生活区",
            "center": "116.456,39.967",
            "radius": 5000
        }
    }
    
    class Config:
        env_file = ".env"

# 目标区域配置
TARGET_AREAS = {
    "guomao": {
        "name": "国贸CBD核心区",
        "center": "116.468,39.914",
        "radius": 5000
    },
    "sanlitun": {
        "name": "三里屯-工体时尚区",
        "center": "116.453,39.933",
        "radius": 5000
    },
    "wangjing": {
        "name": "望京科技商务区",
        "center": "116.4828,39.9968",
        "radius": 5000
    },
    "aoyuncun": {
        "name": "奥运村-亚运村文体区",
        "center": "116.396,40.008",
        "radius": 5000
    },
    "chaoyangpark": {
        "name": "朝阳公园-蓝色港湾生态区",
        "center": "116.478,39.946",
        "radius": 5000
    },
    "dawanglu": {
        "name": "大望路-华贸商业区",
        "center": "116.489,39.914",
        "radius": 5000
    },
    "shuangjing": {
        "name": "双井-富力城居住区",
        "center": "116.468,39.894",
        "radius": 5000
    },
    "gaobeidian": {
        "name": "高碑店-传媒文化区",
        "center": "116.525,39.908",
        "radius": 5000
    },
    "dongba": {
        "name": "东坝-第四使馆区",
        "center": "116.5607,39.9582",
        "radius": 5000
    },
    "changying": {
        "name": "常营-东坝边缘居住区",
        "center": "116.601,39.933",
        "radius": 5000
    },
    "sanyuanqiao": {
        "name": "三元桥-太阳宫国际生活区",
        "center": "116.456,39.967",
        "radius": 5000
    }
}

# 创建全局设置实例
settings = Settings()

# 将目标区域添加到settings对象中
settings.target_areas = TARGET_AREAS

# 从环境变量加载配置
def load_env_config():
    """从环境变量加载配置"""
    if os.getenv("AMAP_API_KEY"):
        settings.amap_api_key = os.getenv("AMAP_API_KEY")
    
    if os.getenv("DATABASE_URL"):
        settings.database_url = os.getenv("DATABASE_URL")
    
    if os.getenv("DEBUG"):
        settings.debug = os.getenv("DEBUG").lower() == "true"

# 初始化时加载配置
load_env_config() 