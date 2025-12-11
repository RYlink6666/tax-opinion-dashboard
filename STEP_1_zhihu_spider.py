# -*- coding: utf-8 -*-
"""
跨境电商税收舆论采集 - 知乎爬虫
目标：采集1500条知乎相关问答
时间：2025年6月-12月
"""

import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
import csv

class ZhihuSpider:
    """知乎爬虫 - 采集跨境电商税收讨论"""
    
    def __init__(self):
        self.posts = []
        # 知乎关键词：问题关键词
        self.keywords = [
            '跨境电商增值税',
            '跨境电商税收政策',
            '9610海关编码',
            '1039市场采购',
            'Temu税务',
            '香港公司税收居民',
            '海外仓报关',
            '电商补税',
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self._random_user_agent()
        })
    
    def _random_user_agent(self):
        """随机User-Agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(agents)
    
    def search_zhihu(self, keyword, num_pages=2):
        """
        搜索知乎问答
        """
        print(f"\n💡 开始采集知乎：{keyword}")
        
        for page in range(1, num_pages + 1):
            try:
                # 知乎搜索URL
                url = f"https://www.zhihu.com/search?type=content&q={keyword}&page={page}"
                
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f"   ❌ 第{page}页请求失败")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 知乎搜索结果选择器（可能需要调整）
                items = soup.find_all('div', attrs={'class': lambda x: x and 'SearchResult' in (x or '')})
                
                if not items:
                    # 尝试其他选择器
                    items = soup.find_all('article', attrs={'class': lambda x: x and 'search' in (x or '').lower()})
                
                count_this_page = 0
                for item in items:
                    try:
                        # 提取标题和内容
                        title_elem = item.find('h2')
                        if not title_elem:
                            title_elem = item.find('a', attrs={'class': lambda x: x and 'title' in (x or '').lower()})
                        
                        content_elem = item.find('p', attrs={'class': lambda x: x and 'content' in (x or '').lower()})
                        if not content_elem:
                            content_elem = item.find('p')
                        
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        content = content_elem.get_text(strip=True) if content_elem else ""
                        
                        # 组合文本
                        text = f"{title} {content}".strip()
                        
                        if len(text) < 20:
                            continue
                        
                        # 过滤广告
                        spam_keywords = ['推广', '广告', '购买', '链接']
                        if any(kw in text for kw in spam_keywords):
                            continue
                        
                        # 提取点赞数
                        vote_elem = item.find('button', attrs={'class': lambda x: x and 'vote' in (x or '').lower()})
                        votes = 0
                        if vote_elem:
                            try:
                                votes = int(vote_elem.get_text())
                            except:
                                pass
                        
                        self.posts.append({
                            'platform': 'zhihu',
                            'keyword': keyword,
                            'text': text[:500],
                            'votes': votes,
                            'collected_at': datetime.now().isoformat(),
                            'source_url': url
                        })
                        count_this_page += 1
                        
                    except Exception as e:
                        continue
                
                print(f"   ✓ 第{page}页：采集 {count_this_page} 条")
                
                # 延迟
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"   ❌ 出错：{str(e)}")
                time.sleep(random.uniform(3, 7))
    
    def save_to_json(self, filename='zhihu_raw_data.json'):
        """保存为JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存 {len(self.posts)} 条数据到 {filename}")
        return filename
    
    def save_to_csv(self, filename='zhihu_raw_data.csv'):
        """保存为CSV"""
        if not self.posts:
            print("❌ 没有数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['platform', 'keyword', 'text', 'votes', 'collected_at', 'source_url'])
            writer.writeheader()
            writer.writerows(self.posts)
        print(f"✅ 已保存 {len(self.posts)} 条数据到 {filename}")
        return filename
    
    def run(self):
        """执行采集流程"""
        print("=" * 60)
        print("🚀 开始采集跨境电商税收舆论（知乎版）")
        print("=" * 60)
        
        for keyword in self.keywords:
            self.search_zhihu(keyword, num_pages=2)
            print(f"   目前已采集：{len(self.posts)} 条")
        
        if self.posts:
            self.save_to_json()
            self.save_to_csv()
            print("\n" + "=" * 60)
            print(f"📊 采集完成：共 {len(self.posts)} 条知乎内容")
            print("=" * 60)
        else:
            print("\n❌ 未采集到任何数据")
        
        return self.posts


if __name__ == "__main__":
    spider = ZhihuSpider()
    posts = spider.run()
