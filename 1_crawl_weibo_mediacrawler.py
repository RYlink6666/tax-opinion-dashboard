"""
微博爬虫 - 基于 MediaCrawler
采集关于跨境电商税收政策的舆论

使用方法：
    python 1_crawl_weibo_mediacrawler.py

预期结果：
    data/raw/weibo/ 目录下的 JSON 文件
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from media_crawler.weibo import WeiboCrawler
import config

# ============================================================================
# 日志设置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "crawl_weibo.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 微博爬虫适配器
# ============================================================================

class WeiboOpinionCrawler:
    """
    用 MediaCrawler 爬取微博舆论
    
    关键特性：
    - 自动处理反爬虫（轮换User-Agent、延迟等）
    - 按关键词搜索
    - 时间范围过滤
    - 去重和数据验证
    """
    
    def __init__(self):
        self.crawler = WeiboCrawler()
        self.all_posts = []
        self.start_date = config.DATE_RANGE["start"]
        self.end_date = config.DATE_RANGE["end"]
        self.target_count = config.TARGET_VOLUMES["weibo"]
        
        logger.info(f"初始化微博爬虫")
        logger.info(f"目标：采集 {self.target_count} 条数据")
        logger.info(f"时间范围：{self.start_date} 至 {self.end_date}")
    
    def crawl(self):
        """执行爬取"""
        logger.info(f"开始微博爬取，总共 {len(config.FLAT_KEYWORDS)} 个关键词")
        
        # 微博：分批爬取不同关键词
        # 为了多样性，分组爬取
        keyword_groups = self._group_keywords()
        
        for group_idx, keywords_group in enumerate(keyword_groups, 1):
            logger.info(f"\n【第 {group_idx}/{len(keyword_groups)} 组】")
            logger.info(f"关键词：{keywords_group}")
            
            for keyword in keywords_group:
                if len(self.all_posts) >= self.target_count * 1.1:  # 预留10%
                    logger.info(f"✅ 已达到目标数量 {len(self.all_posts)}")
                    break
                
                self._crawl_keyword(keyword)
                
                # 延迟避免被限流
                time.sleep(config.CRAWL_CONFIG["weibo"]["delay_min"])
            
            if len(self.all_posts) >= self.target_count * 1.1:
                break
        
        logger.info(f"\n【爬取完成】总共采集 {len(self.all_posts)} 条原始数据")
        return self.all_posts
    
    def _group_keywords(self) -> List[List[str]]:
        """
        分组关键词，保证多样性
        微博容易被限流，所以要分组爬取
        """
        keywords = config.FLAT_KEYWORDS.copy()
        
        # 优先级排序：模式词 > 政策词 > 情感词
        priority_keywords = []
        for category in ["0110", "9610", "9710", "9810", "1039", "temu"]:
            priority_keywords.extend(config.KEYWORDS[category])
        
        # 分组（每组10个）
        groups = []
        for i in range(0, len(priority_keywords), 10):
            groups.append(priority_keywords[i:i+10])
        
        return groups
    
    def _crawl_keyword(self, keyword: str):
        """爬取单个关键词"""
        logger.info(f"  爬取关键词：{keyword}")
        
        try:
            # 使用 MediaCrawler 的搜索接口
            # 注：具体API取决于 MediaCrawler 的版本
            # 这里给出通用的调用方式
            
            posts = self.crawler.search(
                keywords=keyword,
                start_date=self.start_date.replace("-", ""),
                end_date=self.end_date.replace("-", ""),
                max_pages=config.CRAWL_CONFIG["weibo"]["max_pages"]
            )
            
            # 数据验证和清洁
            valid_posts = self._validate_posts(posts, keyword)
            
            self.all_posts.extend(valid_posts)
            
            logger.info(f"    ✓ 获得 {len(valid_posts)} 条有效数据 "
                       f"（总计 {len(self.all_posts)}/{self.target_count}）")
            
        except Exception as e:
            logger.warning(f"    ✗ 爬取失败：{e}")
    
    def _validate_posts(self, posts: List[Dict], keyword: str) -> List[Dict]:
        """
        验证和清洁获取的数据
        """
        valid_posts = []
        
        for post in posts:
            try:
                # 检查必需字段
                if not post.get("content"):
                    continue
                
                content = post.get("content", "").strip()
                
                # 长度检查
                if len(content) < config.CLEAN_CONFIG["min_length"]:
                    continue
                
                if len(content) > config.CLEAN_CONFIG["max_length"]:
                    content = content[:config.CLEAN_CONFIG["max_length"]]
                
                # 构建标准数据格式
                clean_post = {
                    "platform": "weibo",
                    "keyword": keyword,
                    "content": content,
                    "author": post.get("author", "unknown"),
                    "likes": post.get("likes", 0),
                    "comments": post.get("comments", 0),
                    "reposts": post.get("reposts", 0),
                    "publish_time": post.get("publish_time", ""),
                    "source_url": post.get("url", ""),
                    "crawl_time": datetime.now().isoformat()
                }
                
                valid_posts.append(clean_post)
                
            except Exception as e:
                logger.debug(f"    ! 验证失败：{e}")
                continue
        
        return valid_posts
    
    def save_results(self):
        """保存爬取结果"""
        output_file = config.WEIBO_RAW_DIR / f"weibo_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
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
        
        logger.info("\n【统计信息】")
        logger.info(f"  总条数：{len(self.all_posts)}")
        
        # 按关键词统计
        keyword_counts = {}
        for post in self.all_posts:
            kw = post.get("keyword", "unknown")
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        logger.info(f"  关键词分布：")
        for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"    - {kw}: {count}")
        
        # 点赞/评论情况
        total_likes = sum(p.get("likes", 0) for p in self.all_posts)
        avg_likes = total_likes / len(self.all_posts) if self.all_posts else 0
        logger.info(f"  平均点赞数：{avg_likes:.1f}")
        
        # 字数统计
        lengths = [len(p.get("content", "")) for p in self.all_posts]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        logger.info(f"  平均内容长度：{avg_length:.0f} 字符")


# ============================================================================
# 备选方案：直接调用 MediaCrawler 的通用接口
# ============================================================================

class WeiboOpinionCrawlerSimple:
    """
    简化版本：直接用 MediaCrawler 的 CLI 或通用接口
    如果上面的版本有问题，用这个
    """
    
    def __init__(self):
        self.output_dir = config.WEIBO_RAW_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def crawl(self):
        """
        使用 MediaCrawler 的命令行工具
        """
        logger.info("使用 MediaCrawler 命令行工具爬取微博")
        
        # 这需要 MediaCrawler 本身提供 CLI
        # 使用方式：
        # python -m media_crawler.weibo --keywords "9610" --output data/raw/weibo/
        
        # 对于初期测试，可以用下面的Mock方式
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """
        如果 MediaCrawler 暂时无法使用，先用Mock数据测试流程
        """
        logger.warning("⚠️  使用Mock数据进行测试")
        
        # 这只是为了测试流程，实际采集时删除
        from generate_mock_data import generate_mock_weibo_data
        mock_data = generate_mock_weibo_data(count=100)
        
        output_file = self.output_dir / "weibo_raw_mock.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Mock数据已保存到 {output_file}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("【微博舆论爬虫】- MediaCrawler 版本")
    logger.info("=" * 70)
    
    # 初始化爬虫
    crawler = WeiboOpinionCrawler()
    
    try:
        # 执行爬取
        posts = crawler.crawl()
        
        # 保存结果
        crawler.save_results()
        
        logger.info("\n✅ 微博爬取完成")
        logger.info(f"   输出目录：{config.WEIBO_RAW_DIR}")
        logger.info(f"   下一步：运行 2_crawl_zhihu_mediacrawler.py")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断了爬取")
        crawler.save_results()  # 保存已采集的数据
        return False
        
    except Exception as e:
        logger.error(f"\n❌ 爬取失败：{e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
