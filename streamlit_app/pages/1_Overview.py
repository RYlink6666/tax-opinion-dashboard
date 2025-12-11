"""
详细总览页面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_analysis_data, get_confidence_stats

st.set_page_config(page_title="详细总览", page_icon="📊", layout="wide")

st.title("📊 舆论详细总览")
st.write("全面统计所有1399条意见的分布情况")

@st.cache_data
def load_data():
    return load_analysis_data()

df = load_data()

# 1. 情感分析详解
st.subheader("1️⃣ 情感分析详解")

col1, col2 = st.columns(2)

with col1:
    sentiment_dist = df['sentiment'].value_counts()
    st.metric("总计", len(df))
    
    for sentiment, count in sentiment_dist.items():
        pct = count / len(df) * 100
        st.write(f"**{sentiment}**: {count} 条 ({pct:.1f}%)")
    
    avg_conf = df['sentiment_confidence'].mean()
    st.write(f"**平均置信度**: {avg_conf:.2f}")

with col2:
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_dist.index,
        values=sentiment_dist.values,
        marker=dict(colors=['#ef553b', '#636efa', '#00cc96'])
    )])
    st.plotly_chart(fig, use_container_width=True)

# 2. 话题分析
st.subheader("2️⃣ 话题分析")

col1, col2 = st.columns([2, 1])

with col1:
    topic_dist = df['topic'].value_counts().head(10)
    fig = go.Figure(data=[go.Bar(
        y=topic_dist.index,
        x=topic_dist.values,
        orientation='h',
        marker=dict(color=topic_dist.values, colorscale='Blues')
    )])
    fig.update_layout(height=400, title="话题分布排行")
    st.plotly_chart(fig, use_container_width=True)

with col1:
    st.write("**话题统计**")
    for topic, count in topic_dist.items():
        pct = count / len(df) * 100
        st.write(f"- {topic}: {count} ({pct:.1f}%)")

# 3. 风险分析
st.subheader("3️⃣ 风险等级分析")

risk_dist = df['risk_level'].value_counts()
risk_order = ['critical', 'high', 'medium', 'low']
risk_ordered = {k: risk_dist.get(k, 0) for k in risk_order}

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure(data=[go.Bar(
        x=list(risk_ordered.keys()),
        y=list(risk_ordered.values()),
        marker=dict(color=['#8b0000', '#ff6b6b', '#ffa500', '#00cc96'])
    )])
    fig.update_layout(height=400, title="风险分布")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("**风险统计**")
    for risk, count in risk_ordered.items():
        pct = count / len(df) * 100
        st.write(f"- {risk}: {count} ({pct:.1f}%)")

# 4. 参与方分析
st.subheader("4️⃣ 参与方分析")

actor_dist = df['actor'].value_counts().head(10)

fig = go.Figure(data=[go.Bar(
    x=actor_dist.index,
    y=actor_dist.values,
    marker=dict(color=actor_dist.values, colorscale='Viridis')
)])
fig.update_layout(height=400, title="参与方分布", xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# 5. 置信度分析
st.subheader("5️⃣ 分析质量评估")

conf_stats = get_confidence_stats(df)

fig = go.Figure(data=[go.Bar(
    x=['情感', '话题', '模式', '风险', '参与方'],
    y=[conf_stats['sentiment'], conf_stats['topic'], conf_stats['pattern'], conf_stats['risk'], conf_stats['actor']],
    marker=dict(color=['#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a'])
)])
fig.update_layout(height=400, title="各维度平均置信度", yaxis_range=[0, 1])
st.plotly_chart(fig, use_container_width=True)

st.info("💡 **更多分析** - 使用左侧菜单查看特定维度的深度分析")
