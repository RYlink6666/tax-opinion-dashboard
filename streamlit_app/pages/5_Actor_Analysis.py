"""
参与方分析页面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)

st.set_page_config(page_title="参与方分析", page_icon="👥", layout="wide")

st.title("👥 参与方分析")
st.write("分析不同参与方在舆论中的表现和行为")

@st.cache_data
def load_data():
    return load_analysis_data()

df = load_data()

# 1. 参与方分布概览
st.subheader("1️⃣ 参与方分布")

col1, col2 = st.columns(2)

with col1:
    actor_dist = df['actor'].value_counts()
    
    st.write(f"**参与方类型**: {df['actor'].nunique()} 种")
    st.write("")
    for actor, count in actor_dist.items():
        pct = count / len(df) * 100
        st.write(f"**{translate_actor(actor)}**: {count} ({pct:.1f}%)")

with col2:
    fig_actor = go.Figure(data=[go.Pie(
        labels=actor_dist.index,
        values=actor_dist.values,
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set2)
    )])
    fig_actor.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_actor, use_container_width=True)

st.markdown("---")

# 2. 参与方的情感倾向
st.subheader("2️⃣ 参与方的情感倾向")

actor_sentiment = pd.crosstab(df['actor'], df['sentiment'])

fig_sentiment = go.Figure(data=[
    go.Bar(name=sent, x=actor_sentiment.index, y=actor_sentiment[sent])
    for sent in actor_sentiment.columns
])
fig_sentiment.update_layout(
    barmode='group',
    height=400,
    xaxis_title="参与方",
    yaxis_title="记录数",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_sentiment, use_container_width=True)

st.markdown("---")

# 3. 参与方的风险特征
st.subheader("3️⃣ 参与方的风险分布")

actor_risk = pd.crosstab(df['actor'], df['risk_level'])
risk_order = ['critical', 'high', 'medium', 'low']

fig_risk = go.Figure(data=[
    go.Bar(name=risk_type, x=actor_risk.index, y=actor_risk[risk_type] if risk_type in actor_risk.columns else [0]*len(actor_risk))
    for risk_type in risk_order
])
fig_risk.update_layout(
    barmode='stack',
    height=400,
    xaxis_title="参与方",
    yaxis_title="记录数",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# 4. 参与方的话题偏好
st.subheader("4️⃣ 参与方的主要话题")

actor_topic = pd.crosstab(df['actor'], df['topic'])

fig_topic_heatmap = go.Figure(data=go.Heatmap(
    z=actor_topic.values,
    x=actor_topic.columns,
    y=actor_topic.index,
    colorscale='YlOrRd'
))
fig_topic_heatmap.update_layout(height=400, xaxis_title="话题", yaxis_title="参与方")
st.plotly_chart(fig_topic_heatmap, use_container_width=True)

st.markdown("---")

# 5. 参与方详细分析
st.subheader("5️⃣ 参与方详细分析")

actors = df['actor'].value_counts().index

for actor in actors:
    with st.expander(f"👤 {actor}"):
        actor_df = df[df['actor'] == actor]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("发言数", len(actor_df))
        
        with col2:
            neg_pct = len(actor_df[actor_df['sentiment'] == 'negative']) / len(actor_df) * 100
            st.metric("负面率", f"{neg_pct:.1f}%")
        
        with col3:
            high_risk = len(actor_df[actor_df['risk_level'].isin(['critical', 'high'])]) / len(actor_df) * 100
            st.metric("高风险率", f"{high_risk:.1f}%")
        
        with col4:
            avg_conf = actor_df['actor_confidence'].mean()
            st.metric("身份识别置信度", f"{avg_conf:.3f}")
        
        # 情感分布
         st.write("**情感分布**")
         sent_dist = actor_df['sentiment'].value_counts()
         for sent, count in sent_dist.items():
             pct = count / len(actor_df) * 100
             st.write(f"{translate_sentiment(sent)}: {count} ({pct:.1f}%)")
         
         # 主要话题
         st.write("**关注的话题** (Top 5)")
         topic_dist = actor_df['topic'].value_counts().head(5)
         for topic, count in topic_dist.items():
             pct = count / len(actor_df) * 100
             st.write(f"{translate_topic(topic)}: {count} ({pct:.1f}%)")
        
        # 主要模式
        st.write("**表达模式** (Top 5)")
        pattern_dist = actor_df['pattern'].value_counts().head(5)
        for pattern, count in pattern_dist.items():
            pct = count / len(actor_df) * 100
            st.write(f"{pattern}: {count} ({pct:.1f}%)")

st.markdown("---")

# 6. 参与方对比分析
st.subheader("6️⃣ 参与方对比")

comparison_metrics = pd.DataFrame({
    '参与方': df['actor'].value_counts().index,
    '发言数': [len(df[df['actor'] == a]) for a in df['actor'].value_counts().index],
    '平均置信度': [df[df['actor'] == a]['actor_confidence'].mean() for a in df['actor'].value_counts().index],
    '负面占比(%)': [len(df[(df['actor'] == a) & (df['sentiment'] == 'negative')]) / len(df[df['actor'] == a]) * 100 for a in df['actor'].value_counts().index],
    '高风险率(%)': [len(df[(df['actor'] == a) & (df['risk_level'].isin(['critical', 'high']))]) / len(df[df['actor'] == a]) * 100 for a in df['actor'].value_counts().index],
})

st.dataframe(
    comparison_metrics,
    column_config={
        '参与方': st.column_config.TextColumn('参与方'),
        '发言数': st.column_config.NumberColumn('发言数'),
        '平均置信度': st.column_config.NumberColumn('平均置信度', format="%.3f"),
        '负面占比(%)': st.column_config.NumberColumn('负面占比(%)', format="%.1f"),
        '高风险率(%)': st.column_config.NumberColumn('高风险率(%)', format="%.1f"),
    },
    hide_index=True,
    use_container_width=True
)

st.markdown("---")

# 7. 参与方关键发言
st.subheader("7️⃣ 各参与方的典型发言")

actors_top = df['actor'].value_counts().head(3).index

for actor in actors_top:
    with st.expander(f"💬 {actor}的高风险发言示例"):
        actor_risk_df = df[(df['actor'] == actor) & (df['risk_level'].isin(['critical', 'high']))]
        
        if len(actor_risk_df) > 0:
            samples = actor_risk_df.head(3)
            for idx, (_, row) in enumerate(samples.iterrows(), 1):
                st.write(f"**{idx}.** [风险等级: {row['risk_level'].upper()}]")
                st.write(f"📝 {row['source_text']}")
                st.caption(f"情感: {row['sentiment']} | 话题: {row['topic']} | 模式: {row['pattern']}")
                st.divider()
        else:
            st.info(f"暂无 {actor} 的高风险发言")
