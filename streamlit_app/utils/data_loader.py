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


@st.cache_data
def get_actors_sentiment_cross(df):
    """获取参与方×情感交叉表（拆分后的演员）
    
    用法：
    >>> actor_sent = get_actors_sentiment_cross(df)
    >>> fig = create_grouped_bar(actor_sent)
    """
    df_split = []
    for idx, row in df.iterrows():
        actors = str(row['actor']).split('|')
        for actor in actors:
            df_split.append({
                'actor': actor.strip(),
                'sentiment': row['sentiment']
            })
    df_split_df = pd.DataFrame(df_split)
    return pd.crosstab(df_split_df['actor'], df_split_df['sentiment'])


@st.cache_data
def get_actors_risk_cross(df):
    """获取参与方×风险交叉表（拆分后的演员）
    
    用法：
    >>> actor_risk = get_actors_risk_cross(df)
    >>> fig = create_stacked_bar(actor_risk)
    """
    df_split = []
    for idx, row in df.iterrows():
        actors = str(row['actor']).split('|')
        for actor in actors:
            df_split.append({
                'actor': actor.strip(),
                'risk_level': row['risk_level']
            })
    df_split_df = pd.DataFrame(df_split)
    return pd.crosstab(df_split_df['actor'], df_split_df['risk_level'])


@st.cache_data
def get_actors_topic_cross(df):
    """获取参与方×话题交叉表（拆分后的演员）
    
    用法：
    >>> actor_topic = get_actors_topic_cross(df)
    >>> fig = create_crosstab_heatmap(actor_topic)
    """
    df_split = []
    for idx, row in df.iterrows():
        actors = str(row['actor']).split('|')
        for actor in actors:
            df_split.append({
                'actor': actor.strip(),
                'topic': row['topic']
            })
    df_split_df = pd.DataFrame(df_split)
    return pd.crosstab(df_split_df['actor'], df_split_df['topic'])


@st.cache_data
def get_high_risk_analysis(df):
    """获取高风险舆论的多维统计分析
    
    返回高风险舆论的数量及其情感/话题/参与方分布
    用于 P3 风险分析页面
    
    返回dict包含：
    - count: 高风险舆论总数
    - sentiment: 高风险舆论的情感分布
    - topic: 高风险舆论的话题分布 (Top 5)
    - actor: 高风险舆论的参与方分布 (Top 5)
    
    用法：
    >>> high_risk_stats = get_high_risk_analysis(df)
    >>> sent_dist = high_risk_stats['sentiment']
    """
    high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]
    return {
        'count': len(high_risk_df),
        'sentiment': high_risk_df['sentiment'].value_counts(),
        'topic': high_risk_df['topic'].value_counts().head(5),
        'actor': high_risk_df['actor'].value_counts().head(5)
    }


@st.cache_data
def get_topic_statistics(df):
    """计算所有话题的热度、敏感度和情感分布统计
    
    对每个话题计算：
    - heat: 出现频次（讨论热度）
    - risk_index: 高/严重风险占比（%）
    - negative_pct, neutral_pct, positive_pct: 各情感占比（%）
    - sensitivity: 敏感度指数 = risk_index×0.6 + negative_pct×0.4
    
    返回按热度排序的DataFrame
    
    用法：
    >>> topic_stats_df = get_topic_statistics(df)
    >>> most_heated = topic_stats_df.iloc[0]
    >>> most_sensitive = topic_stats_df.sort_values('sensitivity', ascending=False).iloc[0]
    
    此函数替换P7中原有的 L49-87 的大块循环计算
    """
    topic_stats = []
    
    for topic in df['topic'].unique():
        topic_df = df[df['topic'] == topic]
        count = len(topic_df)
        
        # 热度 = 出现频次
        heat = count
        
        # 风险指数 = 高风险+严重风险占比
        high_risk_count = len(topic_df[topic_df['risk_level'].isin(['critical', 'high'])])
        risk_index = high_risk_count / count * 100 if count > 0 else 0
        
        # 负面占比
        negative_count = len(topic_df[topic_df['sentiment'] == 'negative'])
        negative_pct = negative_count / count * 100 if count > 0 else 0
        
        # 中立占比
        neutral_count = len(topic_df[topic_df['sentiment'] == 'neutral'])
        neutral_pct = neutral_count / count * 100 if count > 0 else 0
        
        # 正面占比
        positive_count = len(topic_df[topic_df['sentiment'] == 'positive'])
        positive_pct = positive_count / count * 100 if count > 0 else 0
        
        # 敏感度 = 风险指数 + 负面占比 的加权
        sensitivity = risk_index * 0.6 + negative_pct * 0.4
        
        topic_stats.append({
            'topic': topic,
            'heat': heat,
            'risk_index': risk_index,
            'negative_pct': negative_pct,
            'neutral_pct': neutral_pct,
            'positive_pct': positive_pct,
            'sensitivity': sensitivity,
        })
    
    return pd.DataFrame(topic_stats).sort_values('heat', ascending=False)


@st.cache_data
def get_quick_stats(df):
    """一次性计算常用的快速统计指标（缓存）
    
    返回dict包含：
    - negative_count: 负面数
    - negative_pct: 负面占比
    - high_risk_count: 高风险数
    - high_risk_pct: 高风险占比
    - avg_confidence: 平均置信度
    - total_count: 总数
    
    用法：
    >>> stats = get_quick_stats(result_df)
    >>> st.metric("负面占比", f"{stats['negative_pct']:.1f}%")
    
    消除P2中L76-77, L84-85, L228-235的重复计算
    """
    neg_count = len(df[df['sentiment'] == 'negative'])
    neg_pct = neg_count / len(df) * 100 if len(df) > 0 else 0
    
    high_risk_count = len(df[df['risk_level'].isin(['critical', 'high'])])
    high_risk_pct = high_risk_count / len(df) * 100 if len(df) > 0 else 0
    
    avg_conf = df['sentiment_confidence'].mean() if len(df) > 0 else 0
    
    return {
        'negative_count': neg_count,
        'negative_pct': neg_pct,
        'high_risk_count': high_risk_count,
        'high_risk_pct': high_risk_pct,
        'avg_confidence': avg_conf,
        'total_count': len(df)
    }


@st.cache_data
def get_topic_comparison_data(df, selected_topics):
    """计算多个话题的对比数据
    
    用法：
    >>> comparison_df = get_topic_comparison_data(df, ['tax_policy', 'business_risk'])
    
    消除P9 Tab5中L289-298的重复手动计算
    """
    comparison_data = []
    
    for topic in selected_topics:
        topic_df = df[df['topic'] == topic]
        
        comparison_data.append({
            '话题': translate_topic(topic),
            '总数': len(topic_df),
            '负面%': f"{(topic_df['sentiment'] == 'negative').sum() / len(topic_df) * 100:.1f}%",
            '高风险%': f"{((topic_df['risk_level'] == 'critical') | (topic_df['risk_level'] == 'high')).sum() / len(topic_df) * 100:.1f}%",
            '平均置信度': f"{topic_df['sentiment_confidence'].mean():.2%}"
        })
    
    return pd.DataFrame(comparison_data)


@st.cache_data
def get_actor_statistics_summary(df):
    """获取所有参与方的统计汇总表（拆分后）
    
    返回DataFrame包含：
    - 参与方名称
    - 意见数
    - 占比
    - 负面%
    - 高风险%
    
    用法：
    >>> actor_summary_df = get_actor_statistics_summary(df)
    
    消除P9 Tab6中L389-402的重复手动计算（汇总表）
    """
    # 拆分复合参与方标签
    all_actors = []
    for actors_str in df['actor']:
        if pd.notna(actors_str):
            actors = [a.strip() for a in str(actors_str).split('|')]
            all_actors.extend(actors)
    
    actor_series = pd.Series(all_actors)
    actor_dist = actor_series.value_counts()
    
    # 构建汇总表
    actor_summary = []
    for actor in actor_dist.index:
        pattern = rf'(^|\|){actor}($|\|)'
        mask = df['actor'].str.contains(pattern, na=False, regex=True)
        actor_df = df[mask]
        
        actor_summary.append({
            '参与方': translate_actor(actor),
            '意见数_numeric': len(actor_df),
            '意见数': str(len(actor_df)),
            '占比': f"{len(actor_df) / len(df) * 100:.1f}%",
            '负面%': f"{(actor_df['sentiment'] == 'negative').sum() / len(actor_df) * 100:.1f}%",
            '高风险%': f"{((actor_df['risk_level'] == 'critical') | (actor_df['risk_level'] == 'high')).sum() / len(actor_df) * 100:.1f}%"
        })
    
    result_df = pd.DataFrame(actor_summary)
    result_df = result_df.sort_values('意见数_numeric', ascending=False)
    return result_df[['参与方', '意见数', '占比', '负面%', '高风险%']]


@st.cache_data
def get_actor_segment_analysis(df, actor_names):
    """获取特定参与方组群的分析数据（支持复合标签）
    
    返回dict包含：
    - sentiment_dist: 情感分布
    - risk_dist: 风险分布  
    - topic_dist: 话题分布（Top 5）
    - count: 总数
    
    用法：
    >>> consumer_analysis = get_actor_segment_analysis(df, ['consumer'])
    >>> business_analysis = get_actor_segment_analysis(df, ['enterprise', 'cross_border_seller'])
    
    消除P6中L61-69, L97-118的重复段落查询和分布计算
    """
    if isinstance(actor_names, str):
        actor_names = [actor_names]
    
    # 构建过滤mask - 支持复合标签
    mask = pd.Series([False] * len(df), index=df.index)
    for actor in actor_names:
        pattern = rf'(^|\|){actor}($|\|)'
        mask = mask | df['actor'].str.contains(pattern, na=False, regex=True)
    
    segment_df = df[mask]
    
    return {
        'count': len(segment_df),
        'sentiment_dist': segment_df['sentiment'].value_counts(),
        'risk_dist': segment_df['risk_level'].value_counts(),
        'topic_dist': segment_df['topic'].value_counts().head(5),
        'actor_dist': segment_df['actor'].value_counts()
    }


@st.cache_data
def get_policy_analysis(df):
    """获取政策相关舆论分析
    
    返回dict包含：
    - total: 政策相关舆论总数
    - pct: 占比
    - sentiment_dist: 情感分布
    
    用法：
    >>> policy_stats = get_policy_analysis(df)
    
    消除P6 L131-140的政策舆论计算
    """
    policy_df = df[df['topic'] == 'tax_policy']
    return {
        'total': len(policy_df),
        'pct': len(policy_df) / len(df) * 100,
        'sentiment_dist': policy_df['sentiment'].value_counts()
    }


@st.cache_data
def get_risk_segment_analysis(df):
    """获取高风险舆论的详细分析
    
    返回dict包含：
    - total: 高风险舆论数
    - pct: 占比
    - topic_dist: 话题分布
    - actor_dist: 参与方分布
    
    用法：
    >>> risk_stats = get_risk_segment_analysis(df)
    
    消除P6 L157-170的高风险舆论计算
    """
    high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]
    return {
        'total': len(high_risk_df),
        'pct': len(high_risk_df) / len(df) * 100,
        'topic_dist': high_risk_df['topic'].value_counts(),
        'actor_dist': high_risk_df['actor'].value_counts()
    }
