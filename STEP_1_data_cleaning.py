# -*- coding: utf-8 -*-
"""
数据清洁和合并脚本
1. 去重
2. 过滤低质量数据
3. 统一格式
4. 生成最终的 opinions_clean_5000.txt
"""

import json
import pandas as pd
import glob
import os
from pathlib import Path

class DataCleaner:
    """数据清洁类"""
    
    def __init__(self):
        self.all_texts = set()  # 用set做去重
        self.all_posts = []
    
    def load_json_files(self, pattern='*_raw_data.json'):
        """加载所有JSON文件"""
        print("📂 正在加载JSON文件...")
        
        files = glob.glob(pattern)
        if not files:
            print(f"   ❌ 未找到匹配 '{pattern}' 的文件")
            return
        
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.all_posts.extend(data)
                        print(f"   ✓ {file}: {len(data)} 条")
                    else:
                        print(f"   ⚠️  {file} 格式非列表，跳过")
            except Exception as e:
                print(f"   ❌ {file}: {str(e)}")
    
    def load_csv_files(self, pattern='*_raw_data.csv'):
        """加载所有CSV文件"""
        print("📂 正在加载CSV文件...")
        
        files = glob.glob(pattern)
        if not files:
            print(f"   ℹ️  未找到匹配 '{pattern}' 的文件")
            return
        
        for file in files:
            try:
                df = pd.read_csv(file, encoding='utf-8')
                # 转为字典列表
                posts = df.to_dict('records')
                self.all_posts.extend(posts)
                print(f"   ✓ {file}: {len(df)} 条")
            except Exception as e:
                print(f"   ❌ {file}: {str(e)}")
    
    def clean_text(self, text):
        """清洁单条文本"""
        if not isinstance(text, str):
            return ""
        
        # 去除多余空格
        text = ' '.join(text.split())
        
        # 去除特殊字符和控制符
        text = ''.join(c for c in text if c.isprintable())
        
        # 截断到500字（舆论通常不太长）
        text = text[:500].strip()
        
        return text
    
    def is_valid_post(self, text):
        """判断是否为有效的舆论"""
        if not text:
            return False
        
        # 长度检查
        if len(text) < 10 or len(text) > 500:
            return False
        
        # 中文内容检查（至少50%中文）
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_count < len(text) * 0.4:
            return False
        
        # 垃圾内容过滤
        spam_keywords = [
            '推广', '广告', '点击', '关注', '转发', '分享',
            '购买', '链接', '扫码', '下载', '安装',
            'http', 'www', '.com', '.cn',  # URL
            '🌟', '💎', '🔥', '💰',  # 过多emoji
        ]
        if any(kw in text for kw in spam_keywords):
            return False
        
        return True
    
    def clean_and_deduplicate(self):
        """清洁和去重"""
        print("\n🧹 正在清洁数据...")
        
        cleaned_texts = []
        duplicates = 0
        invalid = 0
        
        for post in self.all_posts:
            # 提取文本
            if isinstance(post, dict):
                text = post.get('text', '')
            else:
                text = str(post)
            
            # 清洁
            text = self.clean_text(text)
            
            # 有效性检查
            if not self.is_valid_post(text):
                invalid += 1
                continue
            
            # 去重
            if text in self.all_texts:
                duplicates += 1
                continue
            
            self.all_texts.add(text)
            cleaned_texts.append(text)
        
        print(f"   ✓ 原始条数：{len(self.all_posts)}")
        print(f"   ✓ 已清洁：{len(cleaned_texts)}")
        print(f"   ✓ 重复移除：{duplicates}")
        print(f"   ✓ 无效移除：{invalid}")
        print(f"   ✓ 最终条数：{len(cleaned_texts)}")
        
        return cleaned_texts
    
    def save_txt(self, texts, filename='opinions_clean_5000.txt'):
        """保存为TXT（每行一条）"""
        with open(filename, 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n')
        print(f"\n✅ 已保存到 {filename}")
        return filename
    
    def save_json(self, texts, filename='opinions_clean_5000.json'):
        """保存为JSON"""
        data = {
            'metadata': {
                'total': len(texts),
                'format': 'list of strings'
            },
            'data': texts
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存到 {filename}")
        return filename
    
    def save_csv(self, texts, filename='opinions_clean_5000.csv'):
        """保存为CSV"""
        df = pd.DataFrame({
            'id': range(1, len(texts) + 1),
            'text': texts
        })
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ 已保存到 {filename}")
        return filename
    
    def quality_report(self, texts):
        """生成质量报告"""
        print("\n" + "=" * 60)
        print("📊 数据质量报告")
        print("=" * 60)
        
        if not texts:
            print("❌ 无数据")
            return
        
        lengths = [len(t) for t in texts]
        
        print(f"总条数：{len(texts)}")
        print(f"平均长度：{sum(lengths) / len(lengths):.0f} 字符")
        print(f"最短：{min(lengths)} 字符")
        print(f"最长：{max(lengths)} 字符")
        print(f"中位数：{sorted(lengths)[len(lengths)//2]} 字符")
        
        # 随机抽样
        print("\n📌 随机抽样（前10条）：")
        for i, text in enumerate(texts[:10], 1):
            preview = text[:60] + "..." if len(text) > 60 else text
            print(f"{i:2d}. {preview}")
        
        print("=" * 60)
    
    def run(self):
        """执行完整的清洁流程"""
        print("=" * 60)
        print("🚀 开始数据清洁流程")
        print("=" * 60)
        
        # 加载数据
        self.load_json_files()
        self.load_csv_files()
        
        if not self.all_posts:
            print("\n❌ 未加载到任何数据！")
            print("   请确保已运行 STEP_1_weibo_spider.py 和 STEP_1_zhihu_spider.py")
            return
        
        # 清洁
        cleaned_texts = self.clean_and_deduplicate()
        
        if len(cleaned_texts) < 100:
            print(f"\n⚠️  警告：清洁后仅 {len(cleaned_texts)} 条数据，可能不足")
            print("   建议重新运行爬虫或检查数据质量")
        
        # 保存
        self.save_txt(cleaned_texts)
        self.save_json(cleaned_texts)
        self.save_csv(cleaned_texts)
        
        # 报告
        self.quality_report(cleaned_texts)
        
        return cleaned_texts


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaned = cleaner.run()
