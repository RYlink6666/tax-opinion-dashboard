"""
跨境电商税收舆论分析 - 主应用
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import (
    load_analysis_data, 
    get_sentiment_distribution,
    get_topic_distribution,
    get_risk_distribution,
    get_actor_distribution,
    get_confidence_stats,
    get_sample_opinions,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)

# 页面配置
st.set_page_config(
    page_title="跨境电商舆论分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据
@st.cache_data
def load_data():
    return load_analysis_data()

df = load_data()
total_count = len(df)

# 自定义CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .title-main {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.1em;
        color: #666;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 页面标题
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<div class='title-main'>🌐 跨境电商税收舆论分析平台</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>基于LLM的智能舆论分析系统 | 1399条意见实时分析</div>", unsafe_allow_html=True)

# 关键指标
st.markdown("---")
st.subheader("📈 核心指标")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("总意见数", f"{total_count:,}", "条")

with col2:
    sentiment_dist = get_sentiment_distribution(df)
    negative_pct = sentiment_dist.get('negative', 0) / total_count * 100
    st.metric("负面舆论", f"{negative_pct:.1f}%", f"{sentiment_dist.get('negative', 0)} 条")

with col3:
    avg_conf = df['sentiment_confidence'].mean()
    st.metric("平均置信度", f"{avg_conf:.2f}", "↑ 很高")

with col4:
    risk_high = len(df[df['risk_level'].isin(['critical', 'high'])])
    risk_pct = risk_high / total_count * 100
    st.metric("高风险占比", f"{risk_pct:.1f}%", f"{risk_high} 条")

with col5:
    st.metric("数据覆盖", "900-2299", "意见索引")

st.markdown("---")

# 主要图表区域
st.subheader("📊 舆论分析概览")

# 1. 情感分布
col1, col2 = st.columns(2)

with col1:
    st.write("**情感分布**")
    sentiment_dist = get_sentiment_distribution(df)
    
    # 翻译标签
    sentiment_labels = [translate_sentiment(k) for k in sentiment_dist.keys()]
    
    fig_sentiment = go.Figure(data=[go.Pie(
        labels=sentiment_labels,
        values=list(sentiment_dist.values()),
        hole=.3,
        marker=dict(colors=['#ef553b', '#636efa', '#00cc96'])
    )])
    fig_sentiment.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    st.write("**风险分布**")
    risk_dist = get_risk_distribution(df)
    
    risk_order = ['critical', 'high', 'medium', 'low']
    ordered_risk = {k: risk_dist.get(k, 0) for k in risk_order}
    
    # 翻译标签
    risk_labels = [translate_risk(k) for k in ordered_risk.keys()]
    
    fig_risk = go.Figure(data=[go.Bar(
        x=risk_labels,
        y=list(ordered_risk.values()),
        marker=dict(color=['#8b0000', '#ff6b6b', '#ffa500', '#00cc96'])
    )])
    fig_risk.update_layout(height=400, title="")
    st.plotly_chart(fig_risk, use_container_width=True)

# 2. 话题分布
st.write("**话题热度排行**")
topic_dist = get_topic_distribution(df)

# 翻译标签
topic_labels = [translate_topic(k) for k in topic_dist.keys()]

fig_topic = go.Figure(data=[go.Bar(
    y=topic_labels,
    x=list(topic_dist.values()),
    orientation='h',
    marker=dict(color=list(topic_dist.values()), colorscale='Blues')
)])
fig_topic.update_layout(height=400, title="")
st.plotly_chart(fig_topic, use_container_width=True)

# 3. 参与方分布
st.write("**主要参与方**")
actor_dist = get_actor_distribution(df)

# 翻译标签
actor_labels = [translate_actor(k) for k in actor_dist.keys()]

fig_actor = go.Figure(data=[go.Bar(
    x=actor_labels,
    y=list(actor_dist.values()),
    marker=dict(color=list(actor_dist.values()), colorscale='Viridis')
)])
fig_actor.update_layout(height=350, title="", xaxis_tickangle=-45)
st.plotly_chart(fig_actor, use_container_width=True)

# 置信度统计
st.markdown("---")
st.subheader("🎯 分析质量评估")

conf_stats = get_confidence_stats(df)
col1, col2, col3, col4, col5 = st.columns(5)

confidence_labels = ['情感', '话题', '模式', '风险', '参与方']
confidence_values = [conf_stats[k] for k in ['sentiment', 'topic', 'pattern', 'risk', 'actor']]

with col1:
    st.metric("情感", f"{conf_stats['sentiment']:.2f}")
with col2:
    st.metric("话题", f"{conf_stats['topic']:.2f}")
with col3:
    st.metric("模式", f"{conf_stats['pattern']:.2f}")
with col4:
    st.metric("风险", f"{conf_stats['risk']:.2f}")
with col5:
    st.metric("参与方", f"{conf_stats['actor']:.2f}")

# 样本意见展示
st.markdown("---")
st.subheader("💬 典型意见示例")

col1, col2 = st.columns(2)

with col1:
    st.write("**负面舆论示例**")
    negative_samples = get_sample_opinions(df, sentiment='negative', limit=3)
    for i, sample in enumerate(negative_samples, 1):
        with st.container():
            st.write(f"**#{i} 风险等级: {sample['risk_level'].upper()}**")
            st.write(f"📝 {sample['source_text'][:100]}...")
            st.write(f"🏷️ 话题: {sample['topic']} | 参与方: {sample['actor']}")
            st.divider()

with col2:
    st.write("**正面舆论示例**")
    positive_samples = get_sample_opinions(df, sentiment='positive', limit=3)
    if positive_samples:
        for i, sample in enumerate(positive_samples, 1):
            with st.container():
                st.write(f"**#{i} 风险等级: {sample['risk_level'].upper()}**")
                st.write(f"📝 {sample['source_text'][:100]}...")
                st.write(f"🏷️ 话题: {sample['topic']} | 参与方: {sample['actor']}")
                st.divider()
    else:
        st.info("暂无正面舆论")

# 页面导航提示
st.markdown("---")
st.info("""
📌 **如何使用本平台**

使用左侧菜单导航到不同的分析页面：
- 📊 **详细总览** - 完整的数据统计
- 🔄 **六大模式** - 跨境电商模式分析
- ⚠️ **风险分析** - 高风险舆论识别
- 📈 **行为响应** - 参与方反应分析
- 🏷️ **关键词** - 热词和主题分析
- 📋 **数据详览** - 原始数据查询
- ℹ️ **关于项目** - 项目背景和方法
""")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 12px;'>
    <p>跨境电商税收舆论分析平台 © 2025 | 基于LLM的舆论分析系统</p>
    <p>数据来源：小红书 | 分析时间：2025年12月 | 样本量：1,399条</p>
</div>
""", unsafe_allow_html=True)
