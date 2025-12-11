"""
知乎爬虫 - 基于 MediaCrawler
采集关于跨境电商税收政策的问答内容

使用方法：
    python 2_crawl_zhihu_mediacrawler.py

预期结果：
    data/raw/zhihu/ 目录下的 JSON 文件
    
特点：
- 知乎数据质量高（讨论深度好）
- 采集量相对较少（质量>数量）
- 重点关注实战模式讨论（9610/9810等）
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from media_crawler.zhihu import ZhihuCrawler
import config

# ============================================================================
# 日志设置
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "crawl_zhihu.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# 知乎爬虫适配器
# ============================================================================

class ZhihuOpinionCrawler:
    """
    用 MediaCrawler 爬取知乎舆论
    
    知乎爬虫特点：
    - 需要登录（MediaCrawler 已处理）
    - 反爬虫严格（使用延迟）
    - 数据质量高（讨论深度）
    - 采集速度相对慢
    """
    
    def __init__(self):
        self.crawler = ZhihuCrawler()
        self.all_posts = []
        self.start_date = config.DATE_RANGE["start"]
        self.end_date = config.DATE_RANGE["end"]
        self.target_count = config.TARGET_VOLUMES["zhihu"]
        
        logger.info(f"初始化知乎爬虫")
        logger.info(f"目标：采集 {self.target_count} 条数据")
        logger.info(f"时间范围：{self.start_date} 至 {self.end_date}")
    
    def crawl(self):
        """执行爬取"""
        logger.info(f"开始知乎爬取")
        
        # 知乎：优先选择实战模式相关的关键词
        keywords = self._select_keywords()
        logger.info(f"选中 {len(keywords)} 个关键词")
        
        for idx, keyword in enumerate(keywords, 1):
            if len(self.all_posts) >= self.target_count:
                logger.info(f"✅ 已达到目标数量 {len(self.all_posts)}")
                break
            
            logger.info(f"[{idx}/{len(keywords)}] 爬取关键词：{keyword}")
            
            self._crawl_keyword(keyword)
            
            # 知乎反爬虫严格，延迟更长
            delay = config.CRAWL_CONFIG["zhihu"]["delay_min"]
            logger.debug(f"  延迟 {delay} 秒...")
            time.sleep(delay)
        
        logger.info(f"\n【爬取完成】总共采集 {len(self.all_posts)} 条原始数据")
        return self.all_posts
    
    def _select_keywords(self) -> List[str]:
        """
        选择适合知乎的关键词
        知乎用户更关注实战模式，而不是情感词汇
        """
        keywords = []
        
        # 优先级：实战模式 > 政策讨论
        for category in ["9610", "9810", "1039", "0110", "policies"]:
            keywords.extend(config.KEYWORDS[category])
        
        # 去重并限制数量
        keywords = list(set(keywords))[:20]
        
        return keywords
    
    def _crawl_keyword(self, keyword: str):
        """爬取单个关键词"""
        try:
            # 搜索答案（知乎搜索接口）
            answers = self.crawler.search(
                keywords=keyword,
                max_pages=config.CRAWL_CONFIG["zhihu"]["max_pages"]
            )
            
            # 验证和清洁
            valid_posts = self._validate_posts(answers, keyword)
            
            self.all_posts.extend(valid_posts)
            
            logger.info(f"  ✓ 获得 {len(valid_posts)} 条有效答案 "
                       f"（总计 {len(self.all_posts)}/{self.target_count}）")
            
        except Exception as e:
            logger.warning(f"  ✗ 爬取失败：{e}")
    
    def _validate_posts(self, answers: List[Dict], keyword: str) -> List[Dict]:
        """
        验证知乎答案数据
        知乎的数据结构与微博不同
        """
        valid_posts = []
        
        for answer in answers:
            try:
                # 获取答案内容
                content = answer.get("content", "").strip()
                
                # 长度检查
                if len(content) < config.CLEAN_CONFIG["min_length"]:
                    continue
                
                if len(content) > config.CLEAN_CONFIG["max_length"]:
                    content = content[:config.CLEAN_CONFIG["max_length"]]
                
                # 标准格式
                clean_post = {
                    "platform": "zhihu",
                    "keyword": keyword,
                    "content": content,
                    
                    # 知乎特有字段
                    "question": answer.get("question_title", ""),
                    "answer_author": answer.get("author", "unknown"),
                    "likes": answer.get("likes", 0),
                    "comments": answer.get("comments", 0),
                    "shares": answer.get("shares", 0),
                    "views": answer.get("views", 0),
                    
                    # 其他
                    "publish_time": answer.get("publish_time", ""),
                    "source_url": answer.get("url", ""),
                    "crawl_time": datetime.now().isoformat()
                }
                
                valid_posts.append(clean_post)
                
            except Exception as e:
                logger.debug(f"    ! 验证失败：{e}")
                continue
        
        return valid_posts
    
    def save_results(self):
        """保存爬取结果"""
        output_file = config.ZHIHU_RAW_DIR / f"zhihu_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
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
        
        logger.info("\n【知乎数据统计】")
        logger.info(f"  总条数：{len(self.all_posts)}")
        
        # 问题分布
        questions = set()
        for post in self.all_posts:
            q = post.get("question", "")
            if q:
                questions.add(q)
        logger.info(f"  涉及问题数：{len(questions)}")
        
        # 平均质量指标
        total_likes = sum(p.get("likes", 0) for p in self.all_posts)
        avg_likes = total_likes / len(self.all_posts) if self.all_posts else 0
        logger.info(f"  平均赞数：{avg_likes:.1f}")
        
        total_views = sum(p.get("views", 0) for p in self.all_posts)
        avg_views = total_views / len(self.all_posts) if self.all_posts else 0
        logger.info(f"  平均浏览数：{avg_views:.0f}")
        
        # 内容长度
        lengths = [len(p.get("content", "")) for p in self.all_posts]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        logger.info(f"  平均内容长度：{avg_length:.0f} 字符")


# ============================================================================
# 简化版本（如有问题可用）
# ============================================================================

class ZhihuOpinionCrawlerSimple:
    """
    简化版：使用 Mock 数据进行测试
    """
    
    def __init__(self):
        self.output_dir = config.ZHIHU_RAW_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def crawl(self):
        """使用 Mock 数据测试"""
        logger.info("使用 Mock 数据进行知乎爬虫测试")
        from generate_mock_data import generate_mock_zhihu_data
        mock_data = generate_mock_zhihu_data(count=100)
        return mock_data
    
    def save_results(self, data):
        """保存 Mock 数据"""
        output_file = self.output_dir / "zhihu_raw_mock.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Mock 数据已保存到 {output_file}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    logger.info("=" * 70)
    logger.info("【知乎舆论爬虫】- MediaCrawler 版本")
    logger.info("=" * 70)
    
    # 初始化爬虫
    crawler = ZhihuOpinionCrawler()
    
    try:
        # 执行爬取
        posts = crawler.crawl()
        
        # 保存结果
        crawler.save_results()
        
        logger.info("\n✅ 知乎爬取完成")
        logger.info(f"   输出目录：{config.ZHIHU_RAW_DIR}")
        logger.info(f"   下一步：运行 3_crawl_xiaohongshu_mediacrawler.py（可选）")
        
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
