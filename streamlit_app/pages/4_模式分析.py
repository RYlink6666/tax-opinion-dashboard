"""
舆论模式分析页面
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)
from utils.chart_builder import (
    create_horizontal_bar,
    create_grouped_bar
)

st.set_page_config(page_title="模式分析", page_icon="🔍", layout="wide")

st.title("🔍 舆论模式分析")
st.write("识别和分析主要的舆论表达模式")

def load_data():
    return load_analysis_data()

df = load_data()

# 1. 模式分布概览
st.subheader("1️⃣ 模式分布概览")

col1, col2 = st.columns(2)

with col1:
    pattern_dist = df['pattern'].value_counts().head(10)
    
    st.write(f"**识别的模式类型**: {df['pattern'].nunique()} 种")
    st.write(f"**总记录数**: {len(df)}")
    st.write("")
    st.write("**Top 10 模式**")
    for pattern, count in pattern_dist.items():
        pct = count / len(df) * 100
        st.write(f"{pattern}: {count} ({pct:.1f}%)")

with col2:
    # 反向排序以匹配原始输出
    pattern_labels = list(pattern_dist.index[::-1])
    pattern_values = list(pattern_dist.values[::-1])
    fig_pattern = create_horizontal_bar(
        pattern_labels,
        pattern_values,
        title="舆论模式分布"
    )
    st.plotly_chart(fig_pattern, use_container_width=True)

st.markdown("---")

# 2. 模式与情感的关系
st.subheader("2️⃣ 模式与情感的关系")

pattern_sentiment = pd.crosstab(df['pattern'], df['sentiment'])
# 只显示前8个模式
pattern_sentiment = pattern_sentiment.head(8)

# 翻译标签并准备数据
sentiment_labels = [translate_sentiment(col) for col in pattern_sentiment.columns]
pattern_sentiment_display = pattern_sentiment.copy()
pattern_sentiment_display.columns = sentiment_labels

fig_pattern_sent = create_grouped_bar(
    pattern_sentiment_display,
    title="舆论模式与情感关系"
)
st.plotly_chart(fig_pattern_sent, use_container_width=True)

st.markdown("---")

# 3. 模式与话题的关系
st.subheader("3️⃣ 模式与话题的关系")

pattern_topic = pd.crosstab(df['pattern'].head(8), df['topic'])

# 翻译话题标签
topic_labels = [translate_topic(col) for col in pattern_topic.columns]
fig_heatmap = go.Figure(data=go.Heatmap(
    z=pattern_topic.values,
    x=topic_labels,
    y=pattern_topic.index,
    colorscale='Blues'
))
fig_heatmap.update_layout(height=400, xaxis_title="话题", yaxis_title="模式")
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# 4. 模式与风险的关系
st.subheader("4️⃣ 模式与风险等级的关系")

pattern_risk = pd.crosstab(df['pattern'].head(8), df['risk_level'])
risk_order = ['critical', 'high', 'medium', 'low']

# 翻译风险等级标签
risk_labels = [translate_risk(risk_type) for risk_type in risk_order]
fig_pattern_risk = go.Figure(data=[
    go.Bar(name=risk_labels[i], x=pattern_risk.index, y=pattern_risk[risk_order[i]] if risk_order[i] in pattern_risk.columns else [0]*len(pattern_risk))
    for i in range(len(risk_order))
])
fig_pattern_risk.update_layout(
    barmode='stack',
    height=400,
    xaxis_title="舆论模式",
    yaxis_title="记录数",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_pattern_risk, use_container_width=True)

st.markdown("---")

# 5. 模式置信度
st.subheader("5️⃣ 模式识别质量")

pattern_confidence = df.groupby('pattern')['pattern_confidence'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)

fig_conf = go.Figure(data=[go.Bar(
    x=pattern_confidence.index,
    y=pattern_confidence['mean'],
    marker=dict(color=pattern_confidence['mean'], colorscale='RdYlGn'),
    text=pattern_confidence['count'].astype(str),
    textposition='outside'
)])
fig_conf.update_layout(
    height=400,
    xaxis_title="舆论模式",
    yaxis_title="平均置信度",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_conf, use_container_width=True)

st.markdown("---")

# 6. 模式分析 - 按参与方
st.subheader("6️⃣ 不同参与方的主要模式")

actors = df['actor'].value_counts().head(5).index

tabs = st.tabs([f"👥 {actor}" for actor in actors])

for tab, actor in zip(tabs, actors):
    with tab:
        actor_df = df[df['actor'] == actor]
        actor_patterns = actor_df['pattern'].value_counts().head(8)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**参与方**: {actor}")
            st.write(f"**记录数**: {len(actor_df)}")
            st.write("")
            st.write("**主要模式**")
            for pattern, count in actor_patterns.items():
                pct = count / len(actor_df) * 100
                st.write(f"{pattern}: {count} ({pct:.1f}%)")
        
        with col2:
            fig = go.Figure(data=[go.Pie(
                labels=actor_patterns.index,
                values=actor_patterns.values,
                hole=0.3
            )])
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 7. 典型模式示例
st.subheader("7️⃣ 典型模式示例")

top_patterns = df['pattern'].value_counts().head(3).index

for pattern in top_patterns:
    with st.expander(f"📌 模式: {pattern}"):
        pattern_df = df[df['pattern'] == pattern]
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("出现次数", len(pattern_df))
        with col2:
            avg_conf = pattern_df['pattern_confidence'].mean()
            st.metric("平均置信度", f"{avg_conf:.3f}")
        with col3:
            neg_pct = len(pattern_df[pattern_df['sentiment'] == 'negative']) / len(pattern_df) * 100
            st.metric("负面占比", f"{neg_pct:.1f}%")
        with col4:
            high_risk = len(pattern_df[pattern_df['risk_level'].isin(['critical', 'high'])]) / len(pattern_df) * 100
            st.metric("高风险占比", f"{high_risk:.1f}%")
        
        # 示例舆论
        st.write("**示例舆论** (最多显示3条)")
        samples = pattern_df.head(3)
        for idx, (_, row) in enumerate(samples.iterrows(), 1):
            st.write(f"{idx}. {row['source_text'][:150]}...")
            st.caption(f"情感: {row['sentiment']} | 话题: {row['topic']} | 风险: {row['risk_level']}")
