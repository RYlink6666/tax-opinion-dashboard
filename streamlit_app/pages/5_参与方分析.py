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

def load_data():
    return load_analysis_data()

df = load_data()

# 辅助函数：拆分复合标签
def split_composite_labels(series):
    """将复合标签（如'consumer|government'）拆分为单独的标签"""
    all_labels = []
    for value in series:
        if pd.isna(value):
            continue
        labels = str(value).split('|')
        all_labels.extend([label.strip() for label in labels])
    return all_labels

# 1. 参与方分布概览
st.subheader("1️⃣ 参与方分布")

col1, col2 = st.columns(2)

with col1:
    # 拆分复合标签后统计
    split_actors = split_composite_labels(df['actor'])
    actor_dist = pd.Series(split_actors).value_counts()
    
    st.write(f"**参与方类型**: {len(actor_dist)} 种 [split count={len(split_actors)}]")
    st.write("")
    for actor, count in actor_dist.items():
        pct = count / len(split_actors) * 100
        st.write(f"**{translate_actor(actor)}**: {count} ({pct:.1f}%)")

with col2:
    # 翻译参与方标签
    actor_labels = [translate_actor(actor) for actor in actor_dist.index]
    fig_actor = go.Figure(data=[go.Pie(
        labels=actor_labels,
        values=actor_dist.values,
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set2)
    )])
    fig_actor.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_actor, use_container_width=True)

st.markdown("---")

# 2. 参与方的情感倾向
st.subheader("2️⃣ 参与方的情感倾向")

# 构建拆分后的数据用于交叉表
df_split = []
for idx, row in df.iterrows():
    actors = str(row['actor']).split('|')
    for actor in actors:
        df_split.append({
            'actor': actor.strip(),
            'sentiment': row['sentiment']
        })
df_split = pd.DataFrame(df_split)

actor_sentiment = pd.crosstab(df_split['actor'], df_split['sentiment'])

# 翻译参与方和情感标签
actor_labels_x = [translate_actor(actor) for actor in actor_sentiment.index]
sentiment_labels = [translate_sentiment(sent) for sent in actor_sentiment.columns]

fig_sentiment = go.Figure(data=[
    go.Bar(name=sentiment_labels[i], x=actor_labels_x, y=actor_sentiment[actor_sentiment.columns[i]])
    for i in range(len(actor_sentiment.columns))
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

# 构建拆分后的数据用于风险交叉表
df_risk_split = []
for idx, row in df.iterrows():
    actors = str(row['actor']).split('|')
    for actor in actors:
        df_risk_split.append({
            'actor': actor.strip(),
            'risk_level': row['risk_level']
        })
df_risk_split = pd.DataFrame(df_risk_split)

actor_risk = pd.crosstab(df_risk_split['actor'], df_risk_split['risk_level'])
risk_order = ['critical', 'high', 'medium', 'low']

# 翻译参与方和风险等级标签
actor_labels_x = [translate_actor(actor) for actor in actor_risk.index]
risk_labels = [translate_risk(risk_type) for risk_type in risk_order]

fig_risk = go.Figure(data=[
    go.Bar(name=risk_labels[i], x=actor_labels_x, y=actor_risk[risk_order[i]] if risk_order[i] in actor_risk.columns else [0]*len(actor_risk))
    for i in range(len(risk_order))
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

# 构建拆分后的数据用于话题交叉表
df_topic_split = []
for idx, row in df.iterrows():
    actors = str(row['actor']).split('|')
    for actor in actors:
        df_topic_split.append({
            'actor': actor.strip(),
            'topic': row['topic']
        })
df_topic_split = pd.DataFrame(df_topic_split)

actor_topic = pd.crosstab(df_topic_split['actor'], df_topic_split['topic'])

# 翻译参与方和话题标签
actor_labels_y = [translate_actor(actor) for actor in actor_topic.index]
topic_labels_x = [translate_topic(topic) for topic in actor_topic.columns]

fig_topic_heatmap = go.Figure(data=go.Heatmap(
    z=actor_topic.values,
    x=topic_labels_x,
    y=actor_labels_y,
    colorscale='YlOrRd'
))
fig_topic_heatmap.update_layout(height=400, xaxis_title="话题", yaxis_title="参与方")
st.plotly_chart(fig_topic_heatmap, use_container_width=True)

st.markdown("---")

# 5. 参与方详细分析
st.subheader("5️⃣ 参与方详细分析")

import re

# 使用拆分后的演员列表
actors = actor_dist.index

for actor in actors:
    # 构建该演员对应的所有记录（使用正则匹配拆分）
    pattern = rf'(^|\|){re.escape(actor)}($|\|)'
    actor_df = df[df['actor'].str.contains(pattern, regex=True, na=False)]
    
    with st.expander(f"👤 {translate_actor(actor)}"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("发言数", len(actor_df))
        
        with col2:
            neg_pct = len(actor_df[actor_df['sentiment'] == 'negative']) / len(actor_df) * 100 if len(actor_df) > 0 else 0
            st.metric("负面率", f"{neg_pct:.1f}%")
        
        with col3:
            high_risk = len(actor_df[actor_df['risk_level'].isin(['critical', 'high'])]) / len(actor_df) * 100 if len(actor_df) > 0 else 0
            st.metric("高风险率", f"{high_risk:.1f}%")
        
        with col4:
            avg_conf = actor_df['actor_confidence'].mean() if len(actor_df) > 0 else 0
            st.metric("身份识别置信度", f"{avg_conf:.3f}")
        
        # 情感分布
        st.write("**情感分布**")
        sent_dist = actor_df['sentiment'].value_counts()
        for sent, count in sent_dist.items():
            pct = count / len(actor_df) * 100 if len(actor_df) > 0 else 0
            st.write(f"{translate_sentiment(sent)}: {count} ({pct:.1f}%)")
        
        # 主要话题
        st.write("**关注的话题** (Top 5)")
        topic_dist = actor_df['topic'].value_counts().head(5)
        for topic, count in topic_dist.items():
            pct = count / len(actor_df) * 100 if len(actor_df) > 0 else 0
            st.write(f"{translate_topic(topic)}: {count} ({pct:.1f}%)")
        
        # 主要模式
        st.write("**表达模式** (Top 5)")
        pattern_dist = actor_df['pattern'].value_counts().head(5)
        for pattern, count in pattern_dist.items():
            pct = count / len(actor_df) * 100 if len(actor_df) > 0 else 0
            st.write(f"{pattern}: {count} ({pct:.1f}%)")

st.markdown("---")

# 6. 参与方对比分析
st.subheader("6️⃣ 参与方对比")

# 构建对比表（使用拆分后的演员列表）
comparison_data = []
for actor in actor_dist.index:
    pattern = rf'(^|\|){re.escape(actor)}($|\|)'
    actor_df_compare = df[df['actor'].str.contains(pattern, regex=True, na=False)]
    
    if len(actor_df_compare) > 0:
        comparison_data.append({
            '参与方': translate_actor(actor),
            '发言数': len(actor_df_compare),
            '平均置信度': actor_df_compare['actor_confidence'].mean(),
            '负面占比(%)': len(actor_df_compare[actor_df_compare['sentiment'] == 'negative']) / len(actor_df_compare) * 100,
            '高风险率(%)': len(actor_df_compare[actor_df_compare['risk_level'].isin(['critical', 'high'])]) / len(actor_df_compare) * 100,
        })

comparison_metrics = pd.DataFrame(comparison_data)

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

# 获取top 3演员（按拆分后的统计）
actors_top = actor_dist.head(3).index

for actor in actors_top:
    with st.expander(f"💬 {translate_actor(actor)}的高风险发言示例"):
        # 使用正则匹配找出包含该演员的高风险发言
        pattern = rf'(^|\|){re.escape(actor)}($|\|)'
        actor_risk_df = df[(df['actor'].str.contains(pattern, regex=True, na=False)) & 
                           (df['risk_level'].isin(['critical', 'high']))]
        
        if len(actor_risk_df) > 0:
            samples = actor_risk_df.head(3)
            for idx, (_, row) in enumerate(samples.iterrows(), 1):
                st.write(f"**{idx}.** [风险等级: {row['risk_level'].upper()}]")
                st.write(f"📝 {row['source_text']}")
                st.caption(f"情感: {translate_sentiment(row['sentiment'])} | 话题: {translate_topic(row['topic'])} | 模式: {row['pattern']}")
                st.divider()
        else:
            st.info(f"暂无 {translate_actor(actor)} 的高风险发言")
