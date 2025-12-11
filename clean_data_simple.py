#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单版数据清洁脚本 - 直接处理已有的JSON文件
不需要依赖复杂的config
"""
import json
import hashlib
import re
import sys
from pathlib import Path

# 处理Windows编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# 配置
# ============================================================================

# 输入文件
INPUT_FILES = [
    Path("MediaCrawler/data/xhs/json/search_contents_2025-12-10.json"),
    Path("MediaCrawler/data/xhs/json/search_comments_2025-12-10.json"),
]

# 输出目录
OUTPUT_DIR = Path("data/clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_TXT = OUTPUT_DIR / "opinions_clean_5000.txt"
OUTPUT_JSON = OUTPUT_DIR / "opinions_clean_5000.json"

# ============================================================================
# 清洁函数
# ============================================================================

def load_data():
    """加载所有JSON数据"""
    all_items = []
    
    for input_file in INPUT_FILES:
        if not input_file.exists():
            print(f"[WARN] 文件不存在: {input_file}")
            continue
        
        print(f"[LOAD] {input_file.name}")
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 处理列表格式
                if isinstance(data, list):
                    all_items.extend(data)
                # 处理dict格式
                elif isinstance(data, dict):
                    if "data" in data:
                        items = data["data"]
                        if isinstance(items, list):
                            all_items.extend(items)
                    
            print(f"       [OK] {len(all_items)} items loaded")
        except Exception as e:
            print(f"       [ERR] {e}")
    
    print(f"\n[OK] Total loaded: {len(all_items)} items\n")
    return all_items

def extract_content(item):
    """从item中提取内容"""
    # 优先级：content > text > desc > title
    content = item.get("content", "")
    if not content:
        content = item.get("text", "")
    if not content:
        content = item.get("desc", "")
    if not content:
        content = item.get("title", "")
    
    return content.strip()

def deduplicate(items):
    """去重"""
    print("[STEP2] Deduplication")
    
    unique_items = []
    seen_hashes = set()
    
    for item in items:
        content = extract_content(item)
        if not content:
            continue
        
        # MD5哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        if content_hash not in seen_hashes:
            unique_items.append(item)
            seen_hashes.add(content_hash)
    
    removed = len(items) - len(unique_items)
    print(f"  Before: {len(items)} items")
    print(f"  After: {len(unique_items)} items")
    print(f"  Removed: {removed} ({100*removed/len(items):.1f}%)\n")
    
    return unique_items

def filter_length(items, min_len=10, max_len=500):
    """按长度过滤"""
    print("[STEP3] Length filter")
    
    filtered = []
    for item in items:
        content = extract_content(item)
        
        # 长度检查
        if len(content) < min_len:
            continue
        
        # 截断
        if len(content) > max_len:
            content = content[:max_len]
        
        item["_cleaned_content"] = content
        filtered.append(item)
    
    removed = len(items) - len(filtered)
    print(f"  Length: {min_len}-{max_len} chars")
    print(f"  After: {len(filtered)} items")
    print(f"  Removed: {removed}\n")
    
    return filtered

def filter_ads(items):
    """过滤广告"""
    print("[STEP4] Ad filter")
    
    ad_keywords = [
        "purchase", "click", "scan", "contact", "wechat",
        "earn", "daily", "monthly", "free", "limited",
        "buy", "promotional", "discount", "agent", "franchise"
    ]
    
    filtered = []
    for item in items:
        content = item.get("_cleaned_content", "")
        
        # 检查广告特征
        is_ad = False
        for kw in ad_keywords:
            if kw in content and (content.count(kw) > 1 or len(content) < 20):
                is_ad = True
                break
        
        if not is_ad:
            filtered.append(item)
    
    removed = len(items) - len(filtered)
    print(f"  Before: {len(items)} items")
    print(f"  After: {len(filtered)} items")
    print(f"  Removed: {removed}\n")
    
    return filtered

def normalize(items):
    """规范化内容"""
    print("[STEP5] Normalize")
    
    normalized = []
    for item in items:
        content = item.get("_cleaned_content", "")
        
        # 移除URL
        content = re.sub(r'http[s]?://\S+', '', content)
        
        # 移除emoji
        content = re.sub(r'[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]', '', content)
        
        # 移除[xxx]标签
        content = re.sub(r'\[.*?\]', '', content)
        
        # 移除多余空格
        content = ' '.join(content.split())
        
        clean_item = {
            "content": content,
            "platform": "xiaohongshu",
            "keywords": item.get("tag_list", "") or item.get("source_keyword", ""),
        }
        
        normalized.append(clean_item)
    
    print(f"[OK] Normalized: {len(normalized)} items\n")
    return normalized

# ============================================================================
# 导出
# ============================================================================

def export_txt(items, output_file):
    """导出TXT"""
    print(f"[EXPORT] {output_file.name}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(item["content"] + "\n")
    
    print(f"[OK] Saved {len(items)} items\n")

def export_json(items, output_file):
    """导出JSON"""
    print(f"[EXPORT] {output_file.name}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(items),
            "data": items
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved {len(items)} items\n")

# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 70)
    print("[START] Cross-border e-commerce opinion analysis - Data cleaning")
    print("=" * 70)
    print()
    
    # 1. 加载
    print("[STEP1] Load raw data")
    items = load_data()
    
    if not items:
        print("[ERR] No data, exit")
        return False
    
    # 2. 去重
    items = deduplicate(items)
    
    # 3. 长度过滤
    items = filter_length(items)
    
    # 4. 广告过滤
    items = filter_ads(items)
    
    # 5. 规范化
    items = normalize(items)
    
    # 6. 导出
    export_txt(items, OUTPUT_TXT)
    export_json(items, OUTPUT_JSON)
    
    # 统计
    print("=" * 70)
    print("[STATS] Final summary")
    print("=" * 70)
    print(f"\n[OK] Cleaning complete!")
    print(f"   Output: {OUTPUT_TXT}")
    print(f"   Total: {len(items)} items")
    if items:
        avg_len = sum(len(item['content']) for item in items) // len(items)
        print(f"   Avg length: {avg_len} chars\n")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
