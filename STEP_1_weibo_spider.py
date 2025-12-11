# -*- coding: utf-8 -*-
"""
跨境电商税收舆论采集 - 微博爬虫
目标：采集2000条微博舆论（关键词：0110, 9610, 9810, 1039, Temu等）
时间：2025年6月-12月
"""

import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
import csv

class WeiboSpider:
    """微博爬虫 - 采集跨境电商税收相关舆论"""
    
    def __init__(self):
        self.posts = []
        self.keywords = [
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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self._random_user_agent()
        })
    
    def _random_user_agent(self):
        """随机User-Agent，避免反爬"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(agents)
    
    def search_weibo(self, keyword, num_pages=3):
        """
        搜索微博（使用网页版爬取）
        注意：微博网页结构经常变化，此方法可能需要调整
        """
        print(f"\n📱 开始采集微博：{keyword}")
        
        for page in range(1, num_pages + 1):
            try:
                # 微博搜索URL
                url = f"https://s.weibo.com/weibo?q={keyword}&typeall=1&suball=1&page={page}"
                
                self.session.headers['Referer'] = 'https://s.weibo.com/'
                response = self.session.get(url, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f"   ❌ 第{page}页请求失败 (状态码: {response.status_code})")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尝试多种选择器（因为微博网页结构经常变）
                posts = soup.find_all('div', class_='mbrank')
                
                if not posts:
                    posts = soup.find_all('div', attrs={'class': lambda x: x and 'feed-item' in x})
                
                if not posts:
                    print(f"   ⚠️  第{page}页未找到帖子，可能需要更新选择器")
                    continue
                
                count_this_page = 0
                for post in posts:
                    try:
                        # 提取文本
                        text_elem = post.find('p', class_='txt')
                        if not text_elem:
                            text_elem = post.find('p')
                        
                        if not text_elem:
                            continue
                        
                        text = text_elem.get_text(strip=True)
                        
                        # 过滤：太短的内容
                        if len(text) < 20:
                            continue
                        
                        # 过滤：广告或无关内容
                        spam_keywords = ['推广', '广告', '购买', '链接', '扫码']
                        if any(kw in text for kw in spam_keywords):
                            continue
                        
                        # 提取点赞数（可选）
                        like_elem = post.find('span', attrs={'class': lambda x: x and 'like' in x})
                        like_count = 0
                        if like_elem:
                            try:
                                like_count = int(like_elem.get_text())
                            except:
                                pass
                        
                        # 保存
                        self.posts.append({
                            'platform': 'weibo',
                            'keyword': keyword,
                            'text': text[:500],  # 截断到500字
                            'likes': like_count,
                            'collected_at': datetime.now().isoformat(),
                            'source_url': url
                        })
                        count_this_page += 1
                        
                    except Exception as e:
                        continue
                
                print(f"   ✓ 第{page}页：采集 {count_this_page} 条")
                
                # 反爬虫延迟
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"   ❌ 出错：{str(e)}")
                time.sleep(random.uniform(3, 7))
                continue
    
    def save_to_json(self, filename='weibo_raw_data.json'):
        """保存为JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已保存 {len(self.posts)} 条数据到 {filename}")
        return filename
    
    def save_to_csv(self, filename='weibo_raw_data.csv'):
        """保存为CSV"""
        if not self.posts:
            print("❌ 没有数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['platform', 'keyword', 'text', 'likes', 'collected_at', 'source_url'])
            writer.writeheader()
            writer.writerows(self.posts)
        print(f"✅ 已保存 {len(self.posts)} 条数据到 {filename}")
        return filename
    
    def run(self):
        """执行采集流程"""
        print("=" * 60)
        print("🚀 开始采集跨境电商税收舆论（微博版）")
        print("=" * 60)
        
        for keyword in self.keywords:
            self.search_weibo(keyword, num_pages=3)
            print(f"   目前已采集：{len(self.posts)} 条")
        
        # 保存结果
        if self.posts:
            self.save_to_json()
            self.save_to_csv()
            print("\n" + "=" * 60)
            print(f"📊 采集完成：共 {len(self.posts)} 条微博")
            print("=" * 60)
        else:
            print("\n❌ 未采集到任何数据")
        
        return self.posts


if __name__ == "__main__":
    spider = WeiboSpider()
    posts = spider.run()
