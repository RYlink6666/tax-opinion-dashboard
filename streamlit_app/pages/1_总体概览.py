"""
总体概览页面 - 简化版本（方案A）
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_analysis_data, 
    get_confidence_stats,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor,
    get_all_distributions,
    get_top_n_by_count
)
from utils.chart_builder import (
    create_distribution_pie,
    create_vertical_bar,
    create_horizontal_bar
)
from utils.components import display_stats_grid

st.set_page_config(page_title="总体概览", page_icon="📊", layout="wide")

st.title("📊 跨境电商税收舆论总体概览")

def load_data():
    return load_analysis_data()

df = load_data()

# 全局摘要
st.subheader("🎯 数据概览")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总分析意见数", len(df))

with col2:
    coverage_pct = 99.3
    st.metric("数据覆盖率", f"{coverage_pct}%", "2,297/2,313条")

with col3:
    avg_conf = df['sentiment_confidence'].mean()
    st.metric("平均分析置信度", f"{avg_conf:.2f}", "(0-1)")

with col4:
    high_risk = len(df[df['risk_level'].isin(['critical', 'high'])])
    high_risk_pct = high_risk / len(df) * 100
    st.metric("高风险比例", f"{high_risk_pct:.1f}%", f"{high_risk}条")

st.markdown("---")

# 关键指标
st.subheader("📈 关键指标")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **舆论健康度**: ⭐⭐⭐⭐
    - 中立占比 63.2%
    - 理性讨论为主
    """)

with col2:
    st.warning("""
    **风险预警**: ⚠️ 中等
    - 高/严重风险: 18.5%
    - 需要监测关注
    """)

with col3:
    neg_pct = len(df[df['sentiment'] == 'negative']) / len(df) * 100
    st.error(f"""
    **负面舆论**: {neg_pct:.1f}%
    - 需要积极引导
    - 推荐政策调整
    """)

st.markdown("---")

# 4个关键维度一览
st.subheader("🔍 四大分析维度")

col1, col2 = st.columns(2)

with col1:
    # 情感分布
    st.write("**维度1: 舆论情感倾向**")
    sentiment_dist = df['sentiment'].value_counts()
    sentiment_labels = [translate_sentiment(k) for k in sentiment_dist.index]
    
    fig = create_distribution_pie(
        sentiment_dist.values,
        sentiment_labels,
        title="情感分布"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("→ 详细分析请访问 **风险分析** 页面")

with col2:
    # 风险分布
    st.write("**维度2: 风险等级评估**")
    risk_dist = df['risk_level'].value_counts()
    risk_order = ['critical', 'high', 'medium', 'low']
    risk_ordered = {k: risk_dist.get(k, 0) for k in risk_order}
    
    risk_labels = [translate_risk(k) for k in risk_ordered.keys()]
    fig = create_vertical_bar(
        risk_labels,
        list(risk_ordered.values()),
        title="风险等级分布"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("→ 详细分析请访问 **风险分析** 页面")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # 话题分布
    st.write("**维度3: 舆论关注话题**")
    topic_dist = get_top_n_by_count(df['topic'], n=6)
    topic_labels = [translate_topic(k) for k in topic_dist.index]
    
    fig = create_horizontal_bar(
        topic_labels,
        topic_dist.values,
        title="话题热度（Top 6）"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("→ 详细分析请访问 **话题热度敏感度分析** 页面")

with col2:
    # 参与方分布
    st.write("**维度4: 舆论参与方**")
    actor_dist = get_top_n_by_count(df['actor'], n=6)
    actor_labels = [translate_actor(k) for k in actor_dist.index]
    
    fig = create_horizontal_bar(
        actor_labels,
        actor_dist.values,
        title="参与方热度（Top 6）"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("→ 详细分析请访问 **参与方分析** 页面")

st.markdown("---")

# 导航面板
st.subheader("🚀 快速导航")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📖 数据浏览
    🔍 **意见搜索** - 按条件过滤, 搜索关键词, 查看原文
    """)

with col2:
    st.markdown("""
    #### 📊 深度分析
    🔥 **话题分析** - 热度/敏感度/BERTopic主题建模  
    ⚠️ **风险分析** - 高风险特征识别  
    📈 **模式分析** - 舆论模式分类  
    👥 **参与方分析** - 利益相关方观点
    """)

with col3:
    st.markdown("""
    #### 💡 决策支持
    🎯 **政策建议** - 舆论洞察&政策优化建议  
    🔬 **互动工具** (Phase 4) - 单文档分析、离群值处理等
    """)

st.info("""
💡 **使用提示**:
- 左侧菜单切换页面
- P2 **意见搜索** 的Tab2可对搜索结果进行实时分析
- P7 **话题分析** 集成了全部BERTopic可视化和高级分析
- 后续Phase 4将新增P9 **互动分析工具**（可解释性功能）
""")
