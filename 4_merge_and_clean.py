"""
数据合并与清洁脚本
将所有平台的原始数据合并、去重、清洁

使用方法：
    python 4_merge_and_clean.py

输入：
    data/raw/weibo/*.json
    data/raw/zhihu/*.json
    data/raw/xiaohongshu/*.json

输出：
    data/clean/opinions_clean_5000.txt
    data/clean/opinions_clean_5000.json
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

import config

# ============================================================================
# 日志设置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "clean.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 数据清洁器
# ============================================================================

class DataCleaner:
    """数据清洁和去重"""
    
    def __init__(self):
        self.all_data = []
        self.dedup_hashes = set()
        self.stats = {
            "total_raw": 0,
            "after_dedup": 0,
            "after_filter_length": 0,
            "after_filter_ads": 0,
            "final": 0
        }
    
    def load_raw_data(self) -> List[Dict]:
        """从所有平台加载原始数据"""
        logger.info("【第1步】加载原始数据")
        
        all_files = []
        for platform_dir in [config.WEIBO_RAW_DIR, config.ZHIHU_RAW_DIR, config.XIAOHONGSHU_RAW_DIR]:
            json_files = list(platform_dir.glob("*.json"))
            all_files.extend(json_files)
            logger.info(f"  {platform_dir.name}: {len(json_files)} 个文件")
        
        if not all_files:
            logger.error("❌ 未找到任何原始数据文件！")
            logger.error(f"   检查是否运行了爬虫脚本 (1_crawl_weibo...)")
            return []
        
        # 加载所有JSON文件
        for json_file in all_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理不同的JSON格式
                    if isinstance(data, list):
                        self.all_data.extend(data)
                    else:
                        # 字典格式：尝试提取data字段或根字段
                        if isinstance(data, dict):
                            if "data" in data:
                                items = data["data"]
                                if isinstance(items, list):
                                    self.all_data.extend(items)
                                else:
                                    self.all_data.append(items)
                            else:
                                # 直接作为单个item
                                self.all_data.append(data)
                
                logger.info(f"  ✓ 已加载 {json_file.name} ({len(self.all_data)} 条数据)")
            except Exception as e:
                logger.warning(f"  ✗ 加载失败 {json_file.name}: {e}")
        
        self.stats["total_raw"] = len(self.all_data)
        logger.info(f"✅ 总共加载 {len(self.all_data)} 条原始数据\n")
        
        return self.all_data
    
    def deduplicate(self) -> List[Dict]:
        """去重"""
        logger.info("【第2步】去重处理")
        
        unique_data = []
        dedup_hashes = set()
        
        for item in self.all_data:
            # 获取内容文本
            content = item.get("content", "")
            if not content:
                content = item.get("text", "")
            
            # 计算哈希
            content_hash = self._hash_content(content)
            
            # 检查重复
            if content_hash not in dedup_hashes:
                unique_data.append(item)
                dedup_hashes.add(content_hash)
        
        removed = len(self.all_data) - len(unique_data)
        self.stats["after_dedup"] = len(unique_data)
        
        logger.info(f"  去重前：{len(self.all_data)} 条")
        logger.info(f"  去重后：{len(unique_data)} 条")
        logger.info(f"  删除：{removed} 条重复 ({100*removed/len(self.all_data):.1f}%)\n")
        
        return unique_data
    
    def filter_by_length(self, data: List[Dict]) -> List[Dict]:
        """按长度过滤"""
        logger.info("【第3步】长度过滤")
        
        min_len = config.CLEAN_CONFIG["min_length"]
        max_len = config.CLEAN_CONFIG["max_length"]
        
        filtered = []
        
        for item in data:
            content = item.get("content", "")
            if not content:
                content = item.get("text", "")
            
            # 长度检查
            if len(content) < min_len:
                continue
            
            # 截断
            if len(content) > max_len:
                content = content[:max_len]
                item["content"] = content
            
            filtered.append(item)
        
        removed = len(data) - len(filtered)
        self.stats["after_filter_length"] = len(filtered)
        
        logger.info(f"  长度范围：{min_len}-{max_len} 字符")
        logger.info(f"  过滤后：{len(filtered)} 条")
        logger.info(f"  删除：{removed} 条\n")
        
        return filtered
    
    def filter_ads_and_spam(self, data: List[Dict]) -> List[Dict]:
        """过滤广告和垃圾信息"""
        logger.info("【第4步】广告和垃圾过滤")
        
        # 广告特征词
        ad_keywords = [
            "购买", "点击这里", "扫码", "联系我", "微信号",
            "可以赚钱", "日赚", "月入", "包邮", "限时",
            "点一下", "长按识别", "点击链接", "领优惠",
            "代理", "加盟", "投资", "返利"
        ]
        
        filtered = []
        
        for item in data:
            content = item.get("content", "")
            if not content:
                content = item.get("text", "")
            
            # 检查广告特征
            is_ad = False
            for ad_kw in ad_keywords:
                if ad_kw in content:
                    # 过于明显的广告
                    if content.count(ad_kw) > 1 or len(content) < 20:
                        is_ad = True
                        break
            
            if not is_ad:
                filtered.append(item)
        
        removed = len(data) - len(filtered)
        self.stats["after_filter_ads"] = len(filtered)
        
        logger.info(f"  过滤前：{len(data)} 条")
        logger.info(f"  过滤后：{len(filtered)} 条")
        logger.info(f"  删除：{removed} 条广告\n")
        
        return filtered
    
    def normalize_content(self, data: List[Dict]) -> List[Dict]:
        """规范化内容"""
        logger.info("【第5步】内容规范化")
        
        import re
        normalized = []
        
        for item in data:
            # 获取内容（支持多种字段名）
            content = item.get("content", "")
            if not content:
                content = item.get("text", "")
            if not content:
                content = item.get("desc", "")  # 小红书的description字段
            if not content:
                content = item.get("title", "")  # 小红书的title字段
            
            # 跳过空内容
            if not content:
                continue
            
            # 移除URL（如需要）
            if config.CLEAN_CONFIG.get("remove_urls", True):
                content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
            
            # 移除emoji和特殊符号
            if config.CLEAN_CONFIG.get("remove_emojis", True):
                # 移除emoji
                content = re.sub(r'[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]', '', content)
                # 移除[xxx]形式的标签
                content = re.sub(r'\[.*?\]', '', content)
            
            # 移除多余空格
            content = ' '.join(content.split())
            
            # 标准化字段
            clean_item = {
                "platform": item.get("platform", "xiaohongshu"),  # 默认小红书
                "content": content,
                "keywords": item.get("keyword", "") or item.get("tag_list", "") or item.get("source_keyword", ""),
                "source_url": item.get("source_url", "") or item.get("note_url", ""),
                "crawl_time": item.get("crawl_time", "") or item.get("time", "")
            }
            
            normalized.append(clean_item)
        
        logger.info(f"✅ 规范化完成：{len(normalized)} 条\n")
        
        return normalized
    
    def clean(self) -> List[Dict]:
        """执行完整的清洁流程"""
        logger.info("\n" + "=" * 70)
        logger.info("【数据清洁流程】")
        logger.info("=" * 70 + "\n")
        
        # 1. 加载
        self.load_raw_data()
        
        if not self.all_data:
            logger.error("❌ 无原始数据，无法继续")
            return []
        
        # 2. 去重
        data = self.deduplicate()
        
        # 3. 长度过滤
        data = self.filter_by_length(data)
        
        # 4. 广告过滤
        data = self.filter_ads_and_spam(data)
        
        # 5. 规范化
        data = self.normalize_content(data)
        
        self.stats["final"] = len(data)
        
        return data
    
    def _hash_content(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def print_statistics(self):
        """打印统计信息"""
        logger.info("\n" + "=" * 70)
        logger.info("【最终统计】")
        logger.info("=" * 70)
        
        logger.info(f"\n数据量变化：")
        logger.info(f"  原始数据：      {self.stats['total_raw']:6d} 条")
        logger.info(f"  去重后：        {self.stats['after_dedup']:6d} 条 "
                   f"(-{self.stats['total_raw'] - self.stats['after_dedup']})")
        logger.info(f"  长度过滤后：    {self.stats['after_filter_length']:6d} 条 "
                   f"(-{self.stats['after_dedup'] - self.stats['after_filter_length']})")
        logger.info(f"  广告过滤后：    {self.stats['after_filter_ads']:6d} 条 "
                   f"(-{self.stats['after_filter_length'] - self.stats['after_filter_ads']})")
        logger.info(f"  最终清洁数据：  {self.stats['final']:6d} 条")
        
        if self.stats['total_raw'] > 0:
            retention_rate = 100 * self.stats['final'] / self.stats['total_raw']
            logger.info(f"\n  数据保留率：{retention_rate:.1f}%")
        
        logger.info("\n✅ 数据清洁完成")


# ============================================================================
# 输出处理
# ============================================================================

class DataExporter:
    """数据导出"""
    
    @staticmethod
    def export_txt(data: List[Dict], output_file: Path):
        """导出为TXT格式（每行一条）"""
        logger.info(f"\n【导出为TXT】{output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in data:
                    content = item.get("content", "")
                    f.write(content + "\n")
            
            logger.info(f"✅ 已保存 {len(data)} 条到 {output_file.name}")
            
        except Exception as e:
            logger.error(f"❌ 导出失败：{e}")
    
    @staticmethod
    def export_json(data: List[Dict], output_file: Path):
        """导出为JSON格式"""
        logger.info(f"\n【导出为JSON】{output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total": len(data),
                    "data": data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 已保存 {len(data)} 条到 {output_file.name}")
            
        except Exception as e:
            logger.error(f"❌ 导出失败：{e}")
    
    @staticmethod
    def export_excel(data: List[Dict], output_file: Path):
        """导出为Excel格式（用于后续分析）"""
        logger.info(f"\n【导出为Excel】{output_file}")
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            df.to_excel(output_file, index=False)
            
            logger.info(f"✅ 已保存 {len(data)} 条到 {output_file.name}")
            
        except ImportError:
            logger.warning("⚠️  未安装pandas，跳过Excel导出")
        except Exception as e:
            logger.error(f"❌ 导出失败：{e}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    logger.info("\n" + "=" * 70)
    logger.info("【跨境电商税收舆论 - 数据清洁】")
    logger.info("=" * 70)
    
    # 1. 清洁数据
    cleaner = DataCleaner()
    clean_data = cleaner.clean()
    
    if not clean_data:
        logger.error("❌ 清洁失败，无有效数据")
        return False
    
    # 2. 统计
    cleaner.print_statistics()
    
    # 3. 导出
    exporter = DataExporter()
    
    # 导出为TXT（用于LLM分析）
    exporter.export_txt(clean_data, config.OUTPUT_CONFIG["clean_opinions_file"])
    
    # 导出为JSON（备份）
    exporter.export_json(clean_data, config.OUTPUT_CONFIG["clean_json_file"])
    
    # 尝试导出Excel
    try:
        exporter.export_excel(clean_data, config.OUTPUT_CONFIG["clean_excel_file"])
    except:
        pass
    
    logger.info("\n" + "=" * 70)
    logger.info("【清洁完成】")
    logger.info("=" * 70)
    logger.info(f"\n✅ 输出文件：")
    logger.info(f"   {config.OUTPUT_CONFIG['clean_opinions_file']}")
    logger.info(f"\n📌 下一步：运行LLM分析")
    logger.info(f"   见：STEP_2_LangExtract完整分析计划.md")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
