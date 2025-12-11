"""
风险深度分析页面
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor,
    get_high_risk_subset,
    get_high_risk_analysis
)
from utils.chart_builder import (
    create_distribution_pie,
    create_horizontal_bar,
    create_stacked_bar
)
from utils.components import display_opinion_expander

st.set_page_config(page_title="风险分析", page_icon="⚠️", layout="wide")

st.title("⚠️ 风险深度分析")
st.write("全面分析高风险舆论的特征和分布")

def load_data():
    return load_analysis_data()

df = load_data()

# 1. 风险等级分布详解
st.subheader("1️⃣ 风险等级分布")

col1, col2 = st.columns(2)

with col1:
    risk_dist = df['risk_level'].value_counts().sort_index()
    
    # 定义风险等级的顺序和颜色
    risk_order = ['critical', 'high', 'medium', 'low']
    risk_labels = {'critical': '严重', 'high': '高', 'medium': '中', 'low': '低'}
    risk_colors = {'critical': '#8b0000', 'high': '#ff6b6b', 'medium': '#ffa500', 'low': '#00cc96'}
    
    ordered_data = {risk_labels[k]: risk_dist.get(k, 0) for k in risk_order if k in risk_dist.index}
    
    st.metric("总记录数", len(df))
    st.metric("高风险+严重", len(df[df['risk_level'].isin(['critical', 'high'])]))
    st.metric("中低风险", len(df[df['risk_level'].isin(['medium', 'low'])]))
    
    for risk_type in risk_order:
        if risk_type in risk_dist.index:
            count = risk_dist[risk_type]
            pct = count / len(df) * 100
            st.write(f"**{risk_labels[risk_type]}风险**: {count} 条 ({pct:.1f}%)")

with col2:
    # 圆环图
    labels = [risk_labels[k] for k in risk_order if k in risk_dist.index]
    values = [risk_dist[k] for k in risk_order if k in risk_dist.index]
    fig_risk = create_distribution_pie(values, labels, title="风险等级分布")
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# 2. 高风险與论分析
st.subheader("2️⃣ 高风险舆论特征分析")

# 使用缓存函数获取高风险统计
high_risk_stats = get_high_risk_analysis(df)
high_risk_df = get_high_risk_subset(df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("高风险总数", high_risk_stats['count'])
    st.write("**按情感分布**")
    for sent, count in high_risk_stats['sentiment'].items():
        pct = count / high_risk_stats['count'] * 100
        st.write(f"{translate_sentiment(sent)}: {count} ({pct:.1f}%)")

with col2:
    st.write("**高风险话题Top 5**")
    for topic, count in high_risk_stats['topic'].items():
        pct = count / high_risk_stats['count'] * 100
        st.write(f"{translate_topic(topic)}: {count} ({pct:.1f}%)")

with col3:
    st.write("**高风险参与方Top 5**")
    for actor, count in high_risk_stats['actor'].items():
        pct = count / high_risk_stats['count'] * 100
        st.write(f"{translate_actor(actor)}: {count} ({pct:.1f}%)")

# 3. 高风险舆论按话题分布
st.write("**高风险舆论话题分布**")
topic_risk = high_risk_df['topic'].value_counts()
topic_labels = [translate_topic(k) for k in topic_risk.index]
fig_topic_risk = create_horizontal_bar(
    topic_labels,
    topic_risk.values,
    title="高风险舆论话题分布"
)
st.plotly_chart(fig_topic_risk, use_container_width=True)

st.markdown("---")

# 4. 风险等级与情感的关系
st.subheader("3️⃣ 风险等级与情感的交叉分析")

risk_sentiment = pd.crosstab(
    df['risk_level'].map({'critical': '严重', 'high': '高', 'medium': '中', 'low': '低'}),
    df['sentiment']
)

fig_cross = create_stacked_bar(
    risk_sentiment,
    title="风险等级与情感倾向分布"
)
st.plotly_chart(fig_cross, use_container_width=True)

st.markdown("---")

# 5. 置信度分析
st.subheader("4️⃣ 风险评估质量")

conf_by_risk = df.groupby('risk_level')['risk_confidence'].mean()
risk_order = ['critical', 'high', 'medium', 'low']
conf_ordered = {risk_labels[k]: conf_by_risk.get(k, 0) for k in risk_order if k in conf_by_risk.index}

col1, col2, col3, col4 = st.columns(4)
cols_list = [col1, col2, col3, col4]

for i, (risk_type, conf) in enumerate(conf_ordered.items()):
    with cols_list[i]:
        st.metric(f"{risk_type}", f"{conf:.3f}")

st.markdown("---")

# 6. 高风险舆论示例
st.subheader("5️⃣ 高风险舆论示例")

if len(high_risk_df) > 0:
    sample_count = min(5, len(high_risk_df))
    samples = high_risk_df.head(sample_count)
    
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        display_opinion_expander(row, index=idx)
else:
    st.info("暂无高风险舆论")
