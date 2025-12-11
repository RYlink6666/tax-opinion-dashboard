"""
数据加载和处理工具
"""

import json
import pandas as pd
from pathlib import Path
import streamlit as st
import os


def load_analysis_data(filepath=None):
    """加载分析结果JSON文件（不缓存，每次都读新数据）
    
    支持多个部署环境：
    - 本地开发（工作目录为项目根）
    - Streamlit Cloud（工作目录为repo根）
    - Docker（工作目录变化）
    """
    if filepath is None:
        # 方案1：从当前脚本位置往上找项目根（最可靠）
        # 脚本位置：streamlit_app/utils/data_loader.py
        # 项目根目录应该包含 data/ 文件夹
        script_dir = os.path.dirname(os.path.abspath(__file__))  # streamlit_app/utils
        project_candidates = [
            os.path.dirname(os.path.dirname(script_dir)),  # streamlit_app的上一级（项目根）
            os.path.dirname(script_dir),  # streamlit_app
            os.getcwd(),  # 当前工作目录
        ]
        
        possible_paths = []
        for base_dir in project_candidates:
            possible_paths.extend([
                os.path.join(base_dir, 'data', 'analysis', 'analysis_results.json'),
                os.path.join(base_dir, 'streamlit_app', 'data', 'analysis', 'analysis_results.json'),
            ])
        
        # 方案2：相对路径（备选）
        possible_paths.extend([
            'data/analysis/analysis_results.json',
            '../data/analysis/analysis_results.json',
            '../../data/analysis/analysis_results.json',
        ])
        
        filepath = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                filepath = abs_path
                break
        
        if filepath is None:
            # 详细的调试信息
            debug_info = f"""
❌ 数据文件未找到

尝试查找的路径：
"""
            for p in possible_paths[:5]:
                abs_p = os.path.abspath(p)
                exists = "✓" if os.path.exists(abs_p) else "✗"
                debug_info += f"  {exists} {abs_p}\n"
            
            debug_info += f"""
当前脚本位置: {script_dir}
当前工作目录: {os.getcwd()}

请确保：
1. 数据文件位置: <项目根>/data/analysis/analysis_results.json
2. 项目根目录包含 streamlit_app/ 文件夹
3. 在项目根目录运行 streamlit 应用
"""
            st.error(debug_info)
            st.stop()
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        results = data.get('data', [])
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}\n\n文件路径: {filepath}")
        st.stop()


def get_sentiment_distribution(df):
    """情感分布统计"""
    return df['sentiment'].value_counts().to_dict()


def get_topic_distribution(df):
    """话题分布统计"""
    return df['topic'].value_counts().head(10).to_dict()


def get_risk_distribution(df):
    """风险分布统计"""
    return df['risk_level'].value_counts().to_dict()


def get_actor_distribution(df):
    """参与方分布统计"""
    return df['actor'].value_counts().head(8).to_dict()


def get_pattern_distribution(df):
    """模式分布统计"""
    return df['pattern'].value_counts().head(8).to_dict()


def get_confidence_stats(df):
    """置信度统计"""
    return {
        'sentiment': df['sentiment_confidence'].mean(),
        'topic': df['topic_confidence'].mean(),
        'pattern': df['pattern_confidence'].mean(),
        'risk': df['risk_confidence'].mean(),
        'actor': df['actor_confidence'].mean(),
    }


def filter_by_sentiment(df, sentiment):
    """按情感筛选"""
    return df[df['sentiment'] == sentiment]


def filter_by_risk(df, risk_level):
    """按风险等级筛选"""
    return df[df['risk_level'] == risk_level]


def search_by_keyword(df, keyword):
    """按关键词搜索"""
    return df[df['source_text'].str.contains(keyword, na=False, case=False)]


def get_sample_opinions(df, sentiment=None, risk=None, limit=10):
    """获取样本意见"""
    result = df
    if sentiment:
        result = result[result['sentiment'] == sentiment]
    if risk:
        result = result[result['risk_level'] == risk]
    return result.head(limit).to_dict('records')


# 翻译字典
SENTIMENT_MAP = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中立',
    'positive|neutral': '正面/中立',
    'negative|positive': '负面/正面'
}

RISK_MAP = {
    'critical': '严重',
    'high': '高',
    'medium': '中',
    'low': '低'
}

TOPIC_MAP = {
    'tax_policy': '税收政策',
    'business_risk': '商业风险',
    'price_impact': '价格影响',
    'compliance': '合规性',
    'other': '其他'
}

ACTOR_MAP = {
    'consumer': '消费者',
    'enterprise': '企业',
    'cross_border_seller': '跨境卖家',
    'general_public': '社会公众',
    'government': '政府',
    'media': '媒体',
    'other': '其他',
    'multiple': '多方',
    'student': '学生',
    'individual': '个人',
    'graduate': '研究生'
}

def translate_risk(value):
    """翻译风险等级"""
    return RISK_MAP.get(value, value)

def translate_topic(value):
    """翻译话题（支持组合标签）"""
    if '|' in str(value):
        parts = str(value).split('|')
        return '/'.join([TOPIC_MAP.get(p.strip(), p.strip()) for p in parts])
    return TOPIC_MAP.get(value, value)

def translate_actor(value):
    """翻译参与方（支持组合标签）"""
    if '|' in str(value):
        parts = str(value).split('|')
        return '/'.join([ACTOR_MAP.get(p.strip(), p.strip()) for p in parts])
    return ACTOR_MAP.get(value, value)

def translate_sentiment(value):
    """翻译情感（支持组合标签）"""
    if '|' in str(value):
        parts = str(value).split('|')
        return '/'.join([SENTIMENT_MAP.get(p.strip(), p.strip()) for p in parts])
    return SENTIMENT_MAP.get(value, value)


# ============================================================================
# Phase 10A: 优先级1 - 预计算函数（消除统计重复）
# ============================================================================

@st.cache_data
def get_all_distributions(df):
    """一次性计算所有主要分布（缓存以提升性能）
    
    返回dict包含所有常用的value_counts：
    - sentiment: 情感分布
    - risk_level: 风险等级分布
    - topic: 话题分布
    - actor: 参与方分布（原始拆分前）
    - pattern: 模式分布
    
    优势：
    1. 避免多页面重复计算相同数据
    2. 缓存机制确保只计算一次
    3. 页面加载速度提升
    """
    return {
        'sentiment': df['sentiment'].value_counts(),
        'risk_level': df['risk_level'].value_counts(),
        'topic': df['topic'].value_counts(),
        'actor': df['actor'].value_counts(),
        'pattern': df['pattern'].value_counts(),
    }


@st.cache_data
def get_cross_analysis(df, dim1, dim2):
    """通用交叉表生成（缓存）
    
    用法：
    >>> cross = get_cross_analysis(df, 'risk_level', 'sentiment')
    
    替代原来的：
    >>> cross = pd.crosstab(df['risk_level'], df['sentiment'])
    
    这样可以在多页面复用，且自动缓存
    """
    return pd.crosstab(df[dim1], df[dim2])


@st.cache_data
def get_high_risk_subset(df):
    """获取高风险舆论子集（缓存）
    
    用法：
    >>> high_risk_df = get_high_risk_subset(df)
    
    替代原来的：
    >>> high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]
    
    在 P3, P5, P7, P9 多个页面使用，缓存避免重复计算
    """
    return df[df['risk_level'].isin(['critical', 'high'])]


@st.cache_data
def get_top_n_by_count(series, n=5):
    """获取Series的Top N（缓存）
    
    用法：
    >>> top_topics = get_top_n_by_count(df['topic'], n=5)
    
    替代原来的：
    >>> top_topics = df['topic'].value_counts().head(5)
    """
    return series.value_counts().head(n)


@st.cache_data
def get_actors_split_statistics(df):
    """获取拆分后的演员统计（用于Page 5）
    
    处理演员标签中的复合标签（如'consumer|government'）
    返回拆分后的统计结果
    
    用法：
    >>> actor_dist = get_actors_split_statistics(df)
    """
    all_actors = []
    for actors_str in df['actor'].dropna():
        actors = str(actors_str).split('|')
        all_actors.extend([a.strip() for a in actors])
    return pd.Series(all_actors).value_counts()
