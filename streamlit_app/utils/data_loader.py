"""
数据加载和处理工具
"""

import json
import pandas as pd
from pathlib import Path
import streamlit as st
import os


@st.cache_data
def load_analysis_data(filepath=None):
    """加载分析结果JSON文件"""
    if filepath is None:
        # 自动定位data文件夹（相对于项目根目录）
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        filepath = os.path.join(current_dir, 'data', 'analysis', 'analysis_results.json')
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    
    results = data.get('data', [])
    return pd.DataFrame(results)


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
