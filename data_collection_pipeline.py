# -*- coding: utf-8 -*-
"""
跨境电商税收舆论数据采集管道 (Pipeline)
一个脚本完成所有采集工作：爬虫 → 清洁 → 输出

使用方式：
    python data_collection_pipeline.py

预期产出：
    ✅ opinions_clean_5000.txt (最终格式，用于LLM分析)
    ✅ opinions_clean_5000.json
    ✅ opinions_clean_5000.csv
"""

import sys
import os
import json
import time
import requests
import random
from datetime import datetime
from pathlib import Path
import csv

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 尝试导入pandas，如果没有则后续安装
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from bs4 import BeautifulSoup


class PipelineConfig:
    """配置参数"""
    
    # 微博配置
    WEIBO_KEYWORDS = [
        '0110香港公司',
        '9610备案',
        '9710B2B',
        '9810海外仓',
        '1039市场采购',
        'Temu全托管',
        '跨境电商增值税',
        '跨境电商税收',
        '跨境电商补税',
    ]
    WEIBO_PAGES = 2  # 每个关键词采集页数
    
    # 知乎配置
    ZHIHU_KEYWORDS = [
        '跨境电商增值税',
        '跨境电商税收政策',
        '9610海关编码',
        '1039市场采购',
        'Temu税务',
        '香港公司税收居民',
        '海外仓报关',
        '电商补税',
    ]
    ZHIHU_PAGES = 2
    
    # 输出配置
    WEIBO_RAW_FILE = 'weibo_raw_data.json'
    ZHIHU_RAW_FILE = 'zhihu_raw_data.json'
    FINAL_TXT_FILE = 'opinions_clean_5000.txt'
    FINAL_JSON_FILE = 'opinions_clean_5000.json'
    FINAL_CSV_FILE = 'opinions_clean_5000.csv'


class Logger:
    """日志记录"""
    
    @staticmethod
    def info(msg):
        """普通信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️  {msg}")
    
    @staticmethod
    def success(msg):
        """成功"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✅ {msg}")
    
    @staticmethod
    def warning(msg):
        """警告"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⚠️  {msg}")
    
    @staticmethod
    def error(msg):
        """错误"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ {msg}")
    
    @staticmethod
    def section(title):
        """章节标题"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")


class WeiboCollector:
    """微博数据采集器"""
    
    def __init__(self):
        self.posts = []
        self.session = self._create_session()
    
    def _create_session(self):
        """创建请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._random_user_agent()
        })
        return session
    
    @staticmethod
    def _random_user_agent():
        """随机User-Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(agents)
    
    def collect(self, keyword, num_pages=2):
        """采集单个关键词的微博"""
        Logger.info(f"采集微博：{keyword}")
        
        for page in range(1, num_pages + 1):
            try:
                url = f"https://s.weibo.com/weibo?q={keyword}&typeall=1&suball=1&page={page}"
                
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    Logger.warning(f"  页面 {page} 请求失败 (状态码: {response.status_code})")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = soup.find_all('div', class_='mbrank')
                
                count = 0
                for post in posts:
                    try:
                        text_elem = post.find('p', class_='txt')
                        if not text_elem:
                            continue
                        
                        text = text_elem.get_text(strip=True)
                        
                        if len(text) < 20:
                            continue
                        
                        # 过滤垃圾
                        if any(kw in text for kw in ['推广', '广告', '链接']):
                            continue
                        
                        self.posts.append({
                            'platform': 'weibo',
                            'keyword': keyword,
                            'text': text[:500],
                            'collected_at': datetime.now().isoformat()
                        })
                        count += 1
                    except:
                        continue
                
                Logger.info(f"  页面 {page}：采集 {count} 条")
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                Logger.warning(f"  页面 {page} 出错：{str(e)}")
                time.sleep(random.uniform(3, 5))
        
        return len(self.posts)
    
    def run(self):
        """执行微博采集"""
        Logger.section("📱 第1步：采集微博数据")
        
        total_before = len(self.posts)
        
        for keyword in PipelineConfig.WEIBO_KEYWORDS:
            self.collect(keyword, num_pages=PipelineConfig.WEIBO_PAGES)
        
        total_after = len(self.posts)
        new_count = total_after - total_before
        
        Logger.success(f"微博采集完成：共 {new_count} 条")
        
        return self.posts
    
    def save(self, filename=None):
        """保存数据"""
        if not filename:
            filename = PipelineConfig.WEIBO_RAW_FILE
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        Logger.success(f"已保存到 {filename}")
        return filename


class ZhihuCollector:
    """知乎数据采集器"""
    
    def __init__(self):
        self.posts = []
        self.session = self._create_session()
    
    def _create_session(self):
        """创建请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self._random_user_agent()
        })
        return session
    
    @staticmethod
    def _random_user_agent():
        """随机User-Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ]
        return random.choice(agents)
    
    def collect(self, keyword, num_pages=2):
        """采集知乎"""
        Logger.info(f"采集知乎：{keyword}")
        
        for page in range(1, num_pages + 1):
            try:
                url = f"https://www.zhihu.com/search?type=content&q={keyword}&page={page}"
                
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    Logger.warning(f"  页面 {page} 请求失败")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找内容元素
                items = soup.find_all('div', attrs={'class': lambda x: x and 'SearchResult' in (x or '')})
                
                count = 0
                for item in items:
                    try:
                        title_elem = item.find('h2')
                        content_elem = item.find('p')
                        
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        content = content_elem.get_text(strip=True) if content_elem else ""
                        
                        text = f"{title} {content}".strip()
                        
                        if len(text) < 20:
                            continue
                        
                        if any(kw in text for kw in ['推广', '广告']):
                            continue
                        
                        self.posts.append({
                            'platform': 'zhihu',
                            'keyword': keyword,
                            'text': text[:500],
                            'collected_at': datetime.now().isoformat()
                        })
                        count += 1
                    except:
                        continue
                
                Logger.info(f"  页面 {page}：采集 {count} 条")
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                Logger.warning(f"  页面 {page} 出错：{str(e)}")
                time.sleep(random.uniform(3, 5))
        
        return len(self.posts)
    
    def run(self):
        """执行知乎采集"""
        Logger.section("💡 第2步：采集知乎数据")
        
        total_before = len(self.posts)
        
        for keyword in PipelineConfig.ZHIHU_KEYWORDS:
            self.collect(keyword, num_pages=PipelineConfig.ZHIHU_PAGES)
        
        total_after = len(self.posts)
        new_count = total_after - total_before
        
        Logger.success(f"知乎采集完成：共 {new_count} 条")
        
        return self.posts
    
    def save(self, filename=None):
        """保存数据"""
        if not filename:
            filename = PipelineConfig.ZHIHU_RAW_FILE
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        Logger.success(f"已保存到 {filename}")
        return filename


class DataCleaner:
    """数据清洁器"""
    
    @staticmethod
    def clean_text(text):
        """清洁文本"""
        if not isinstance(text, str):
            return ""
        
        text = ' '.join(text.split())
        text = ''.join(c for c in text if c.isprintable())
        text = text[:500].strip()
        
        return text
    
    @staticmethod
    def is_valid(text):
        """判断是否有效"""
        if not text or len(text) < 10 or len(text) > 500:
            return False
        
        # 检查中文比例
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_count < len(text) * 0.3:
            return False
        
        return True
    
    def clean_and_deduplicate(self, all_posts):
        """清洁和去重"""
        Logger.section("🧹 第3步：数据清洁和去重")
        
        seen = set()
        cleaned = []
        duplicates = 0
        invalid = 0
        
        Logger.info(f"开始处理 {len(all_posts)} 条原始数据...")
        
        for post in all_posts:
            text = post.get('text', '') if isinstance(post, dict) else str(post)
            text = self.clean_text(text)
            
            if not self.is_valid(text):
                invalid += 1
                continue
            
            if text in seen:
                duplicates += 1
                continue
            
            seen.add(text)
            cleaned.append(text)
        
        Logger.info(f"原始条数：{len(all_posts)}")
        Logger.info(f"已清洁：{len(cleaned)}")
        Logger.info(f"重复移除：{duplicates}")
        Logger.info(f"无效移除：{invalid}")
        Logger.success(f"最终条数：{len(cleaned)}")
        
        return cleaned
    
    @staticmethod
    def save_txt(texts, filename):
        """保存为TXT"""
        with open(filename, 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n')
        Logger.success(f"TXT 已保存到 {filename}")
    
    @staticmethod
    def save_json(texts, filename):
        """保存为JSON"""
        data = {
            'metadata': {
                'total': len(texts),
                'created_at': datetime.now().isoformat()
            },
            'data': texts
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        Logger.success(f"JSON 已保存到 {filename}")
    
    @staticmethod
    def save_csv(texts, filename):
        """保存为CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text'])
            for i, text in enumerate(texts, 1):
                writer.writerow([i, text])
        Logger.success(f"CSV 已保存到 {filename}")
    
    def save_all_formats(self, texts):
        """保存为所有格式"""
        self.save_txt(texts, PipelineConfig.FINAL_TXT_FILE)
        self.save_json(texts, PipelineConfig.FINAL_JSON_FILE)
        self.save_csv(texts, PipelineConfig.FINAL_CSV_FILE)
    
    @staticmethod
    def quality_report(texts):
        """质量报告"""
        Logger.section("📊 数据质量报告")
        
        if not texts:
            Logger.error("无数据")
            return
        
        lengths = [len(t) for t in texts]
        
        print(f"总条数：          {len(texts):,}")
        print(f"平均长度：        {sum(lengths) / len(lengths):.0f} 字符")
        print(f"最短：            {min(lengths)} 字符")
        print(f"最长：            {max(lengths)} 字符")
        print(f"中位数：          {sorted(lengths)[len(lengths)//2]} 字符")
        
        print("\n📌 随机抽样（前5条）：")
        for i, text in enumerate(texts[:5], 1):
            preview = text[:70] + "..." if len(text) > 70 else text
            print(f"  {i}. {preview}")
        
        print("\n✅ 数据质量：合格（已准备好用于LLM分析）")


class DataCollectionPipeline:
    """数据采集主管道"""
    
    def __init__(self):
        self.weibo_collector = WeiboCollector()
        self.zhihu_collector = ZhihuCollector()
        self.cleaner = DataCleaner()
    
    def run(self):
        """执行完整管道"""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 12 + "🚀 跨境电商税收舆论数据采集管道" + " " * 22 + "║")
        print("║" + " " * 20 + "一键完成：爬虫 → 清洁 → 输出" + " " * 20 + "║")
        print("╚" + "=" * 68 + "╝\n")
        
        try:
            # 第1步：采集微博
            weibo_posts = self.weibo_collector.run()
            self.weibo_collector.save()
            
            # 第2步：采集知乎
            zhihu_posts = self.zhihu_collector.run()
            self.zhihu_collector.save()
            
            # 合并
            all_posts = weibo_posts + zhihu_posts
            Logger.section("📦 数据合并")
            Logger.success(f"合并完成：微博 {len(weibo_posts)} + 知乎 {len(zhihu_posts)} = {len(all_posts)} 条")
            
            # 第3步：清洁
            cleaned_texts = self.cleaner.clean_and_deduplicate(all_posts)
            
            # 第4步：保存
            Logger.section("💾 保存数据")
            self.cleaner.save_all_formats(cleaned_texts)
            
            # 第5步：报告
            self.cleaner.quality_report(cleaned_texts)
            
            # 最终总结
            self._final_summary(cleaned_texts)
            
        except KeyboardInterrupt:
            Logger.warning("用户中断了采集")
        except Exception as e:
            Logger.error(f"采集失败：{str(e)}")
            raise
    
    @staticmethod
    def _final_summary(texts):
        """最终总结"""
        Logger.section("✨ 采集完成总结")
        
        if len(texts) >= 4800:
            status = "✅ 优秀"
        elif len(texts) >= 3000:
            status = "⚠️  警告"
        else:
            status = "❌ 失败"
        
        print(f"状态：              {status}")
        print(f"最终数据量：        {len(texts):,} 条")
        print(f"目标：              5000 条")
        print(f"完成度：            {len(texts) / 5000 * 100:.1f}%")
        
        print(f"\n📁 输出文件：")
        print(f"  • {PipelineConfig.FINAL_TXT_FILE} (用于LLM分析)")
        print(f"  • {PipelineConfig.FINAL_JSON_FILE}")
        print(f"  • {PipelineConfig.FINAL_CSV_FILE}")
        
        print(f"\n🎯 下一步：")
        if len(texts) >= 4800:
            print(f"  ✅ 数据充足，可开始 LLM 分析")
            print(f"     见：STEP_2_LangExtract完整分析计划.md")
        else:
            print(f"  ⚠️  数据不足，需要补充采集")
            print(f"     方案：众包或增加爬虫页数")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """主函数"""
    # 检查依赖
    try:
        from bs4 import BeautifulSoup
        import requests
    except ImportError:
        print("❌ 缺少依赖，请运行：")
        print("   pip install requests beautifulsoup4 pandas")
        sys.exit(1)
    
    # 运行管道
    pipeline = DataCollectionPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
