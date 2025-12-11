"""
参与方分析页面
"""

import streamlit as st
import pandas as pd
import re
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor,
    get_actors_split_statistics,
    get_cross_analysis
)
from utils.chart_builder import (
    create_distribution_pie,
    create_grouped_bar,
    create_stacked_bar,
    create_crosstab_heatmap
)
from utils.components import display_opinion_expander

st.set_page_config(page_title="参与方分析", page_icon="👥", layout="wide")

st.title("👥 参与方分析")
st.write("分析不同参与方在舆论中的表现和行为")

def load_data():
    return load_analysis_data()

df = load_data()

# 1. 参与方分布概览
st.subheader("1️⃣ 参与方分布")

# 获取拆分后的参与方统计
actor_dist = get_actors_split_statistics(df)

col1, col2 = st.columns(2)

with col1:
    st.write(f"**参与方类型**: {len(actor_dist)} 种")
    st.write("")
    for actor, count in actor_dist.items():
        pct = count / actor_dist.sum() * 100
        st.write(f"**{translate_actor(actor)}**: {count} ({pct:.1f}%)")

with col2:
    # 翻译参与方标签
    actor_labels = [translate_actor(actor) for actor in actor_dist.index]
    fig_actor = create_distribution_pie(
        actor_dist.values,
        actor_labels,
        title="参与方分布"
    )
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

# 翻译行标签（参与方）
actor_labels_x = [translate_actor(actor) for actor in actor_sentiment.index]
actor_sentiment_display = actor_sentiment.copy()
actor_sentiment_display.index = actor_labels_x

# 翻译列标签（情感）
sentiment_cols_display = [translate_sentiment(sent) for sent in actor_sentiment.columns]
actor_sentiment_display.columns = sentiment_cols_display

fig_sentiment = create_grouped_bar(
    actor_sentiment_display,
    title="参与方的情感倾向"
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

# 确保所有风险等级都存在（缺失的用0填充）
for risk in risk_order:
    if risk not in actor_risk.columns:
        actor_risk[risk] = 0
actor_risk = actor_risk[risk_order]

# 翻译标签
actor_labels_x = [translate_actor(actor) for actor in actor_risk.index]
actor_risk_display = actor_risk.copy()
actor_risk_display.index = actor_labels_x
risk_labels = [translate_risk(risk_type) for risk_type in risk_order]
actor_risk_display.columns = risk_labels

fig_risk = create_stacked_bar(
    actor_risk_display,
    title="参与方的风险分布"
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

# 翻译标签
actor_labels_y = [translate_actor(actor) for actor in actor_topic.index]
topic_labels_x = [translate_topic(topic) for topic in actor_topic.columns]
actor_topic_display = actor_topic.copy()
actor_topic_display.index = actor_labels_y
actor_topic_display.columns = topic_labels_x

fig_topic_heatmap = create_crosstab_heatmap(
    actor_topic_display,
    title="参与方的话题关注分布"
)
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
                display_opinion_expander(row, index=idx)
        else:
            st.info(f"暂无 {translate_actor(actor)} 的高风险发言")
