"""
跨境电商税收舆论采集 - 全局配置文件
"""

import os
import json
from pathlib import Path

# ============================================================================
# 项目路径配置
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
LOGS_DIR = PROJECT_ROOT / "logs"

# 创建目录
for dir_path in [DATA_DIR, RAW_DATA_DIR, CLEAN_DATA_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 平台数据目录（新增：优先使用已有的数据）
EXISTING_XHS_DIR = PROJECT_ROOT / "MediaCrawler" / "data" / "xhs" / "json"

# 优先使用现有数据，否则使用标准目录
WEIBO_RAW_DIR = RAW_DATA_DIR / "weibo"
ZHIHU_RAW_DIR = RAW_DATA_DIR / "zhihu"
XIAOHONGSHU_RAW_DIR = EXISTING_XHS_DIR if EXISTING_XHS_DIR.exists() else (RAW_DATA_DIR / "xiaohongshu")

for dir_path in [WEIBO_RAW_DIR, ZHIHU_RAW_DIR, RAW_DATA_DIR / "xiaohongshu"]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 关键词配置
# ============================================================================

KEYWORDS = {
    # 核心模式关键词（精简版）
    "modes": [
        "0110", "9610", "9710", "9810", "1039", "Temu"
    ],
    
    # 税收相关（精简版）
    "tax": [
        "增值税", "跨境电商", "税收政策", "补税", "纳税",
        "报税", "合规"
    ],
    
    # 情感和讨论词（精简版）
    "sentiment": [
        "困难", "焦虑", "方案", "讨论", "怎么办",
        "求助", "分享"
    ]
}

# 扁平化关键词列表（用于爬虫）
FLAT_KEYWORDS = []
for category in KEYWORDS.values():
    FLAT_KEYWORDS.extend(category)

# 去重
FLAT_KEYWORDS = list(set(FLAT_KEYWORDS))

print(f"OK - Loaded keywords: {len(FLAT_KEYWORDS)} keywords")

# ============================================================================
# 数据采集配置
# ============================================================================

# 时间范围（关键：影响政策舆论的关键期）
DATE_RANGE = {
    "start": "2025-06-01",  # 政策讨论初期
    "end": "2025-12-31"     # 政策实施期
}

# 各平台采集目标
TARGET_VOLUMES = {
    "weibo": 2500,          # 微博：热度最高，最容易采集
    "zhihu": 1500,          # 知乎：讨论深度最好
    "xiaohongshu": 800,     # 小红书：消费者视角
    "total": 4800           # 总目标（允许10%损耗）
}

# 采集参数
CRAWL_CONFIG = {
    "weibo": {
        "max_pages": 15,           # 每个关键词最多爬15页（从50减少）
        "proxy_enabled": False,    # 不用代理（MediaCrawler自己处理反爬）
        "delay_min": 0.5,          # 最小延迟（秒）
        "delay_max": 1,            # 最大延迟（秒）
        "timeout": 10,             # 超时时间
        "retry_times": 3           # 重试次数
    },
    "zhihu": {
        "max_pages": 10,           # 每个关键词最多爬10页（从30减少）
        "proxy_enabled": False,
        "delay_min": 1,
        "delay_max": 2,
        "timeout": 10,
        "retry_times": 3
    },
    "xiaohongshu": {
        "max_pages": 20,
        "proxy_enabled": False,
        "delay_min": 2,
        "delay_max": 5,
        "timeout": 10,
        "retry_times": 3
    }
}

# ============================================================================
# 数据清洁配置
# ============================================================================

CLEAN_CONFIG = {
    # 文本长度（字符）
    "min_length": 10,      # 太短的文本过滤
    "max_length": 500,     # 太长的文本截断
    
    # 去重标准
    "dedup_method": "hash",  # 'hash'（快速）或 'semantic'（精确）
    "dedup_threshold": 0.95,  # 相似度阈值
    
    # 过滤规则
    "remove_ads": True,      # 过滤广告
    "remove_duplicates": True,  # 过滤重复
    "remove_urls": True,     # 移除URL
    "remove_mentions": True, # 移除@提及
    "remove_hashtags": False,  # 保留#话题
    "remove_emojis": True,   # 移除emoji
    
    # 编码
    "encoding": "utf-8",
    "normalize_unicode": True
}

# ============================================================================
# 输出文件配置
# ============================================================================

OUTPUT_CONFIG = {
    # 最终输出文件
    "clean_opinions_file": CLEAN_DATA_DIR / "opinions_clean_5000.txt",
    "clean_json_file": CLEAN_DATA_DIR / "opinions_clean_5000.json",
    "clean_excel_file": CLEAN_DATA_DIR / "opinions_clean_5000.xlsx",
    
    # 中间数据
    "merged_raw_file": RAW_DATA_DIR / "merged_raw_data.json",
    "dedup_stats_file": LOGS_DIR / "dedup_stats.json",
    
    # 日志
    "crawl_log_file": LOGS_DIR / "crawl.log",
    "clean_log_file": LOGS_DIR / "clean.log"
}

# ============================================================================
# 日志配置
# ============================================================================

LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# ============================================================================
# LLM 分析配置（后续用）
# ============================================================================

LLM_CONFIG = {
    # 智谱清言配置
    "provider": "zhipu",
    "model": "glm-4-flash",
    "api_key": os.getenv("ZHIPU_API_KEY"),  # 从环境变量读取
    
    # 分析参数
    "temperature": 0.3,
    "top_p": 0.8,
    "max_tokens": 500,
    
    # 批处理
    "batch_size": 50,
    "retry_times": 3,
    "delay_between_batches": 1  # 秒
}

# ============================================================================
# 验证配置
# ============================================================================

def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查目录
    for dir_path in [DATA_DIR, RAW_DATA_DIR, CLEAN_DATA_DIR, LOGS_DIR]:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")
    
    # 检查关键词
    if not FLAT_KEYWORDS:
        errors.append("Keyword library is empty")
    
    # 检查时间范围
    if DATE_RANGE["start"] > DATE_RANGE["end"]:
        errors.append("Start date after end date")
    
    if errors:
        print("ERROR - Config validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("OK - Config validation passed")
    return True

# 模块导入时自动验证
if __name__ != "__main__":
    validate_config()

# ============================================================================
# 便捷函数
# ============================================================================

def get_keywords_for_platform(platform):
    """获取特定平台的关键词"""
    if platform == "weibo":
        # 微博：用所有关键词
        return FLAT_KEYWORDS
    elif platform == "zhihu":
        # 知乎：用热门模式词 + 政策词
        return KEYWORDS["9610"] + KEYWORDS["9810"] + KEYWORDS["policies"]
    elif platform == "xiaohongshu":
        # 小红书：用简洁的关键词
        return ["9610", "Temu", "增值税", "跨境电商"]
    else:
        return FLAT_KEYWORDS

def get_target_count(platform):
    """获取特定平台的目标采集数"""
    return TARGET_VOLUMES.get(platform, 0)

if __name__ == "__main__":
    print("\n[CONFIG INFO]")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data dir: {DATA_DIR}")
    print(f"Keywords: {len(FLAT_KEYWORDS)}")
    print(f"Date range: {DATE_RANGE['start']} to {DATE_RANGE['end']}")
    print(f"Target: {TARGET_VOLUMES['total']} posts")
    print(f"  - Weibo: {TARGET_VOLUMES['weibo']}")
    print(f"  - Zhihu: {TARGET_VOLUMES['zhihu']}")
    print(f"  - XHS: {TARGET_VOLUMES['xiaohongshu']}")
    print("\nOK - Config loaded successfully")
