"""
小红书爬虫 - 基于 MediaCrawler（可选）
采集关于跨境电商税收政策的用户讨论

使用方法：
    python 3_crawl_xiaohongshu_mediacrawler.py

预期结果：
    data/raw/xiaohongshu/ 目录下的 JSON 文件

说明：
- 小红书主要反映消费者视角（vs 卖家视角）
- 采集量目标较小（500-800条）
- 数据为补充性质，可选
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from media_crawler.xhs import XhsCrawler
import config

# ============================================================================
# 日志设置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "crawl_xiaohongshu.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 小红书爬虫适配器
# ============================================================================

class XiaohongshuOpinionCrawler:
    """
    用 MediaCrawler 爬取小红书舆论
    
    小红书特点：
    - 主要反映年轻用户、消费者视角
    - 数据较为零散（不像微博有话题集中）
    - 反爬虫非常严格（需要代理和延迟）
    - 采集数量有限（目标500-800条）
    """
    
    def __init__(self):
        self.crawler = XhsCrawler()
        self.all_posts = []
        self.start_date = config.DATE_RANGE["start"]
        self.end_date = config.DATE_RANGE["end"]
        self.target_count = config.TARGET_VOLUMES["xiaohongshu"]
        
        logger.info(f"初始化小红书爬虫")
        logger.info(f"目标：采集 {self.target_count} 条数据（补充性）")
    
    def crawl(self):
        """执行爬取"""
        logger.info(f"开始小红书爬取")
        
        # 小红书：关键词相对简化，易接受的关键词
        keywords = self._select_keywords()
        logger.info(f"选中 {len(keywords)} 个关键词")
        
        for idx, keyword in enumerate(keywords, 1):
            if len(self.all_posts) >= self.target_count:
                logger.info(f"✅ 已达到目标数量 {len(self.all_posts)}")
                break
            
            logger.info(f"[{idx}/{len(keywords)}] 爬取：{keyword}")
            
            self._crawl_keyword(keyword)
            
            # 小红书反爬虫最严格，延迟最长
            delay = config.CRAWL_CONFIG["xiaohongshu"]["delay_min"]
            logger.debug(f"  延迟 {delay} 秒...")
            time.sleep(delay)
        
        logger.info(f"\n【爬取完成】总共采集 {len(self.all_posts)} 条原始数据")
        return self.all_posts
    
    def _select_keywords(self) -> List[str]:
        """
        选择适合小红书的关键词
        小红书用户多为消费者，关注品牌/价格/方便性
        """
        keywords = [
            "Temu",
            "跨境电商",
            "增值税",
            "税收",
            "跨境购物",
            "原产地证",
            "电商税收",
            "9610",
            "海外购"
        ]
        
        return keywords[:10]  # 限制10个关键词
    
    def _crawl_keyword(self, keyword: str):
        """爬取单个关键词"""
        try:
            # 搜索内容
            notes = self.crawler.search(
                keywords=keyword,
                max_pages=config.CRAWL_CONFIG["xiaohongshu"]["max_pages"]
            )
            
            # 验证和清洁
            valid_posts = self._validate_posts(notes, keyword)
            
            self.all_posts.extend(valid_posts)
            
            logger.info(f"  ✓ 获得 {len(valid_posts)} 条有效内容 "
                       f"（总计 {len(self.all_posts)}/{self.target_count}）")
            
        except Exception as e:
            logger.warning(f"  ✗ 爬取失败：{e}")
    
    def _validate_posts(self, notes: List[Dict], keyword: str) -> List[Dict]:
        """
        验证小红书笔记数据
        """
        valid_posts = []
        
        for note in notes:
            try:
                # 获取笔记内容
                content = note.get("content", "").strip()
                if not content:
                    content = note.get("description", "").strip()
                
                # 长度检查
                if len(content) < config.CLEAN_CONFIG["min_length"]:
                    continue
                
                if len(content) > config.CLEAN_CONFIG["max_length"]:
                    content = content[:config.CLEAN_CONFIG["max_length"]]
                
                # 标准格式
                clean_post = {
                    "platform": "xiaohongshu",
                    "keyword": keyword,
                    "content": content,
                    
                    # 小红书特有字段
                    "note_id": note.get("note_id", ""),
                    "author": note.get("author", "unknown"),
                    "likes": note.get("likes", 0),
                    "comments": note.get("comments", 0),
                    "shares": note.get("shares", 0),
                    "tags": note.get("tags", []),
                    
                    # 其他
                    "publish_time": note.get("publish_time", ""),
                    "source_url": note.get("url", ""),
                    "crawl_time": datetime.now().isoformat()
                }
                
                valid_posts.append(clean_post)
                
            except Exception as e:
                logger.debug(f"    ! 验证失败：{e}")
                continue
        
        return valid_posts
    
    def save_results(self):
        """保存爬取结果"""
        output_file = config.XIAOHONGSHU_RAW_DIR / f"xiaohongshu_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_posts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 数据已保存到 {output_file}")
            logger.info(f"   总条数：{len(self.all_posts)}")
            
            # 统计
            self._print_statistics()
            
        except Exception as e:
            logger.error(f"❌ 保存失败：{e}")
    
    def _print_statistics(self):
        """打印统计信息"""
        if not self.all_posts:
            return
        
        logger.info("\n【小红书数据统计】")
        logger.info(f"  总条数：{len(self.all_posts)}")
        
        # 关键词分布
        keyword_counts = {}
        for post in self.all_posts:
            kw = post.get("keyword", "unknown")
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        logger.info(f"  关键词分布：")
        for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"    - {kw}: {count}")
        
        # 平均互动
        avg_likes = sum(p.get("likes", 0) for p in self.all_posts) / len(self.all_posts)
        logger.info(f"  平均点赞数：{avg_likes:.1f}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("【小红书舆论爬虫】- MediaCrawler 版本")
    logger.info("=" * 70)
    
    # 初始化爬虫
    crawler = XiaohongshuOpinionCrawler()
    
    try:
        # 执行爬取
        posts = crawler.crawl()
        
        # 保存结果
        crawler.save_results()
        
        logger.info("\n✅ 小红书爬取完成（可选）")
        logger.info(f"   输出目录：{config.XIAOHONGSHU_RAW_DIR}")
        logger.info(f"   下一步：运行 4_merge_and_clean.py")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断了爬取")
        crawler.save_results()
        return False
        
    except Exception as e:
        logger.error(f"\n❌ 爬取失败：{e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
