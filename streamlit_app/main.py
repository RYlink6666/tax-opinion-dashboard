"""
🌐 首页 - 跨境电商税收舆论分析平台
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

# 加载数据（不缓存，每次都读新数据）
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
    st.markdown(f"<div class='subtitle'>基于LLM的智能舆论分析系统 | {total_count}条意见实时分析</div>", unsafe_allow_html=True)

st.info("""
💡 **快速开始**：
1. 新用户：展开下方"📖 页面说明"查看详细教程
2. 已有经验：查看下面的核心指标，然后进入相应分析页面
3. 快速搜索：使用 **P2 意见搜索** 页面找特定舆论
4. 做决策：查看 **P6 政策建议** 页面获取分析结论
""")

st.markdown("---")

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
    min_idx = df.index.min() if len(df) > 0 else 0
    max_idx = df.index.max() if len(df) > 0 else 0
    st.metric("数据覆盖", f"{min_idx}-{max_idx}", "意见索引")

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
            st.write(f"**#{i} 风险等级: {translate_risk(sample['risk_level'])}**")
            st.write(f"📝 {sample['source_text'][:100]}...")
            st.write(f"🏷️ 话题: {translate_topic(sample['topic'])} | 参与方: {translate_actor(sample['actor'])}")
            st.divider()

with col2:
    st.write("**正面舆论示例**")
    positive_samples = get_sample_opinions(df, sentiment='positive', limit=3)
    if positive_samples:
        for i, sample in enumerate(positive_samples, 1):
            with st.container():
                st.write(f"**#{i} 风险等级: {translate_risk(sample['risk_level'])}**")
                st.write(f"📝 {sample['source_text'][:100]}...")
                st.write(f"🏷️ 话题: {translate_topic(sample['topic'])} | 参与方: {translate_actor(sample['actor'])}")
                st.divider()
    else:
        st.info("暂无正面舆论")

# 详细说明 - 可折叠
st.markdown("---")
st.subheader("📖 详细页面说明")

with st.expander("👉 展开查看各页面用途和使用建议", expanded=False):
    st.markdown("""
    ### 📊 P1 - 总体概览
    **目标**：30秒内掌握舆论数据概况
    - 关键指标卡片（总数、正面比例、风险占比等）
    - 4个维度分布图（情感、风险、话题、参与方）
    
    ### 🔍 P2 - 意见搜索
    **目标**：用多条件过滤找到需要的舆论
    - 关键词搜索 + 多维度筛选
    - 结果表格展示，支持排序和分页
    
    ### 🚨 P3 - 风险分析
    **目标**：发现最危险的舆论
    - 风险等级分布、高风险舆论特征
    - 风险与话题、参与方的关系分析
    
    ### 📈 P4 - 模式分析
    **目标**：理解不同交易模式下的舆论差异
    - 各模式的舆论数量、情感倾向、风险特征
    
    ### 👥 P5 - 参与方分析
    **目标**：理解消费者、企业、政府等群体的观点
    - 参与方的情感分布、风险特征、代表观点
    
    ### 💡 P6 - 政策建议
    **目标**：将舆论分析转化为决策建议
    - 关键发现、利益相关方观点、具体政策建议
    
    ### 🔥 P7 - 话题热度敏感度分析
    **目标**：找出最热、最敏感、最有争议的话题
    - 话题热度排行、敏感度热力图、情感分布
    
    ### 🔬 P9 - 互动分析工具
    **目标**：深入分析单条舆论
    - 舆论选择 + 详细信息 + 标签管理
    """)

with st.expander("🛣️ 推荐分析路径", expanded=False):
    tab1, tab2, tab3 = st.tabs(["风险管理", "决策支持", "话题深入"])
    
    with tab1:
        st.markdown("""
        **风险管理路径**
        ```
        P1 (发现高风险舆论)
          ↓
        P3 (分析风险分布和特征)
          ↓
        P5 (找出高风险参与方)
          ↓
        P9 (查看具体高风险舆论)
          ↓
        P6 (制定回应措施)
        ```
        """)
    
    with tab2:
        st.markdown("""
        **决策支持路径**
        ```
        P1 (了解整体舆论)
          ↓
        P4 (理解不同模式的舆论差异)
          ↓
        P5 (理解不同参与方的观点)
          ↓
        P6 (获取政策建议)
        ```
        """)
    
    with tab3:
        st.markdown("""
        **话题深入路径**
        ```
        P7 (找出热门/敏感话题)
          ↓
        P2 (搜索该话题相关舆论)
          ↓
        P3 (分析该话题的风险)
          ↓
        P5 (看各参与方的态度)
          ↓
        P9 (查看代表性舆论)
        ```
        """)

with st.expander("❓ 常见问题 FAQ", expanded=False):
    st.markdown("""
    **Q: 各页面数据是同步的吗？**
    
    A: 是的。所有页面使用同一份数据源，经过相同的清洗和标签流程。
    
    ---
    
    **Q: 数据多久更新一次？**
    
    A: 目前是静态数据（2,297条舆论）。未来计划每月自动更新。
    
    ---
    
    **Q: 可以导出数据或报告吗？**
    
    A: P2的表格可直接复制。P6的内容可截图或复制用于报告。
    
    ---
    
    **Q: 如果发现数据标签错误？**
    
    A: 使用P9页面标记，或直接反馈具体位置。
    """)

with st.expander("🚀 快速上手步骤", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **第一次使用（5分钟）**
        1. 查看本页核心指标
        2. 进入P1看4维度分布
        3. 进入P2搜索关键词
        4. 查看搜索结果表格
        """)
    
    with col2:
        st.markdown("""
        **日常使用（10分钟）**
        1. 打开P1或P7查看热点
        2. 异常时进入P3或P6
        3. 需要找舆论时用P2
        """)
    
    with col3:
        st.markdown("""
        **深入分析（30-60分钟）**
        1. 从P1明确目标
        2. 选择分析路径
        3. 逐步深入
        4. P6汇总为建议
        """)

st.success("""
💡 **核心建议**：新用户先看P1获得全局认知，然后根据需要选择分析路径。
""")

# 页脚
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #999; font-size: 12px;'>
    <p>跨境电商税收舆论分析平台 © 2025 | 基于LLM的舆论分析系统</p>
    <p>数据来源：小红书 | 分析时间：2025年12月 | 样本量：{total_count}条</p>
</div>
""", unsafe_allow_html=True)
