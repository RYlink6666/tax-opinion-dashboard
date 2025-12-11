"""
风险深度分析页面
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

st.set_page_config(page_title="风险分析", page_icon="⚠️", layout="wide")

st.title("⚠️ 风险深度分析")
st.write("全面分析高风险舆论的特征和分布")

@st.cache_data
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
    fig_risk = go.Figure(data=[go.Pie(
        labels=[risk_labels[k] for k in risk_order if k in risk_dist.index],
        values=[risk_dist[k] for k in risk_order if k in risk_dist.index],
        hole=0.3,
        marker=dict(colors=[risk_colors[k] for k in risk_order if k in risk_dist.index])
    )])
    fig_risk.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# 2. 高风险舆论分析
st.subheader("2️⃣ 高风险舆论特征分析")

high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("高风险总数", len(high_risk_df))
    st.write("**按情感分布**")
    sent_dist = high_risk_df['sentiment'].value_counts()
    for sent, count in sent_dist.items():
        pct = count / len(high_risk_df) * 100
        st.write(f"{translate_sentiment(sent)}: {count} ({pct:.1f}%)")

with col2:
    st.write("**高风险话题Top 5**")
    topic_dist = high_risk_df['topic'].value_counts().head(5)
    for topic, count in topic_dist.items():
        pct = count / len(high_risk_df) * 100
        st.write(f"{translate_topic(topic)}: {count} ({pct:.1f}%)")

with col3:
    st.write("**高风险参与方Top 5**")
    actor_dist = high_risk_df['actor'].value_counts().head(5)
    for actor, count in actor_dist.items():
        pct = count / len(high_risk_df) * 100
        st.write(f"{translate_actor(actor)}: {count} ({pct:.1f}%)")

# 3. 高风险舆论按话题分布
st.write("**高风险舆论话题分布**")
topic_risk = high_risk_df['topic'].value_counts()
fig_topic_risk = go.Figure(data=[go.Bar(
    y=topic_risk.index,
    x=topic_risk.values,
    orientation='h',
    marker=dict(color=topic_risk.values, colorscale='Reds')
)])
fig_topic_risk.update_layout(height=400, title="")
st.plotly_chart(fig_topic_risk, use_container_width=True)

st.markdown("---")

# 4. 风险等级与情感的关系
st.subheader("3️⃣ 风险等级与情感的交叉分析")

risk_sentiment = pd.crosstab(
    df['risk_level'].map({'critical': '严重', 'high': '高', 'medium': '中', 'low': '低'}),
    df['sentiment']
)

fig_cross = go.Figure(data=[
    go.Bar(name=col, x=risk_sentiment.index, y=risk_sentiment[col])
    for col in risk_sentiment.columns
])
fig_cross.update_layout(barmode='stack', height=400, xaxis_title="风险等级", yaxis_title="记录数")
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
        with st.container():
            st.write(f"**##{idx} [{row['risk_level'].upper()}风险]**")
            st.write(f"📝 {row['source_text']}")
            
            cols = st.columns(4)
            with cols[0]:
                st.write(f"情感: **{row['sentiment']}**")
            with cols[1]:
                st.write(f"话题: **{row['topic']}**")
            with cols[2]:
                st.write(f"参与方: **{row['actor']}**")
            with cols[3]:
                st.write(f"置信度: **{row['risk_confidence']:.2f}**")
            
            st.divider()
else:
    st.info("暂无高风险舆论")
