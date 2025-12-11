"""
深度话题分析页面 - BERTopic高级可视化
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
)
from utils.bertopic_analyzer import (
    train_bertopic,
    visualize_term_score_decline,
    visualize_hierarchical_documents,
    get_topic_keywords_detailed,
    get_hierarchical_topics,
    visualize_topic_per_class,
    get_topics_summary,
    get_documents_by_topic,
    BERTOPIC_AVAILABLE
)

st.set_page_config(page_title="深度分析", page_icon="🔬", layout="wide")

st.title("🔬 深度话题分析 (Advanced BERTopic)")
st.write("使用BERTopic的高级功能进行深层主题发现和分析")

def load_data():
    return load_analysis_data()

df = load_data()

if not BERTOPIC_AVAILABLE:
    st.error("⚠️ BERTopic未安装，无法使用深度分析功能")
    st.stop()

# 训练模型
st.info("🤖 正在初始化BERTopic模型...")

texts = df['source_text'].tolist()
topics, probs, model = train_bertopic(texts)

if model is None or topics is None:
    st.error("❌ 模型训练失败，请检查数据")
    st.stop()

topic_info = get_topics_summary(model)

if topic_info.empty:
    st.error("❌ 无法获取主题信息")
    st.stop()

st.success(f"✅ 模型训练完成！发现{len(topic_info)-1}个隐藏主题")

st.markdown("---")

# 1. c-TF-IDF 分数衰减分析
st.subheader("1️⃣ c-TF-IDF 分数衰减分析")
st.write("展示每个主题的关键词权重递减规律 - 用于优化主题词汇数量")

col1, col2 = st.columns([3, 1])

with col2:
    n_topics_decline = st.slider("选择分析主题数", 1, min(10, len(topic_info)-1), 5, key="decline")

with col1:
    viz = visualize_term_score_decline(model, top_n_topics=n_topics_decline)
    if viz:
        st.plotly_chart(viz, use_container_width=True)
    else:
        st.info("💡 生成中或不可用...")

st.markdown("""
**如何解读**:
- X轴：词汇的排名（1=最代表该主题的词）
- Y轴：c-TF-IDF分数（越高越代表该主题）
- 通常，曲线的"肘部"（elbow）处表示最优的词汇数量
""")

st.markdown("---")

# 2. 主题关键词详细分析
st.subheader("2️⃣ 主题关键词详细分析")
st.write("逐个查看每个主题的代表性关键词及其权重分数")

col1, col2 = st.columns([1, 3])

with col1:
    # 获取有效的主题ID
    valid_topics = topic_info[topic_info['Topic'] != -1]['Topic'].tolist()
    selected_topic = st.selectbox(
        "选择主题",
        options=valid_topics,
        format_func=lambda x: f"话题{int(x)}: {topic_info[topic_info['Topic']==x]['Name'].iloc[0]}"
    )

with col2:
    # 获取词汇数量
    n_keywords = st.slider("显示关键词数", 5, 20, 10, key="keywords")

# 显示关键词表格
keywords_df = get_topic_keywords_detailed(model, selected_topic, top_n=n_keywords)

if not keywords_df.empty:
    st.dataframe(
        keywords_df,
        column_config={
            '排名': st.column_config.NumberColumn('排名', width=60),
            '关键词': st.column_config.TextColumn('关键词', width=150),
            'c-TF-IDF分数': st.column_config.NumberColumn('权重分数', format="%.4f", width=120),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # 显示分数柱状图
    fig = go.Figure(data=[
        go.Bar(
            y=keywords_df['关键词'],
            x=keywords_df['c-TF-IDF分数'],
            orientation='h',
            marker=dict(
                color=keywords_df['c-TF-IDF分数'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="权重")
            ),
            text=keywords_df['c-TF-IDF分数'].apply(lambda x: f'{x:.4f}'),
            textposition='outside'
        )
    ])
    fig.update_layout(
        height=400,
        xaxis_title="c-TF-IDF分数",
        yaxis_title="",
        title=f"话题{int(selected_topic)}的关键词权重"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"⚠️ 无法获取话题{selected_topic}的关键词")

st.markdown("---")

# 3. 按情感分类的主题分布
st.subheader("3️⃣ 按情感分类的主题分布")
st.write("对比不同情感类型（正面/中立/负面）下的主题分布差异")

fig = visualize_topic_per_class(model, df, class_column='sentiment')
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 可视化生成中...")

st.markdown("""
**分析意义**:
- 不同情感下主题分布的差异可以反映用户对不同话题的态度
- 某些话题更容易激发负面情感
- 这可以指导内容管理和舆论引导
""")

st.markdown("---")

# 4. 按风险等级分类的主题分布
st.subheader("4️⃣ 按风险等级分类的主题分布")
st.write("对比不同风险等级下的主题分布特征")

fig = visualize_topic_per_class(model, df, class_column='risk_level')
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 可视化生成中...")

st.markdown("""
**分析意义**:
- 高风险话题往往集中在特定主题
- 帮助识别需要重点监控的话题
- 支持风险预警和应急处理
""")

st.markdown("---")

# 5. 主题层级结构
st.subheader("5️⃣ 主题层级结构")
st.write("展示主题间的层级聚类关系（哪些话题可以合并）")

# 尝试获取分层结构
hierarchical_topics = get_hierarchical_topics(model)

if hierarchical_topics is not None:
    st.success(f"✅ 检测到{len(hierarchical_topics)}层主题结构")
    
    # 显示层级关系的文本表示
    st.markdown("**层级关系说明**:")
    st.markdown("""
    - 下表展示了主题在不同聚类级别下的组织方式
    - Topic_Parent表示该主题属于哪个父主题
    - 这可以帮助我们理解主题间的逻辑关系
    """)
    
    # 简化显示（只显示前30行）
    display_cols = ['Topic', 'Parent_ID', 'Parent_Name'] if 'Parent_ID' in hierarchical_topics.columns else ['Topic']
    st.dataframe(
        hierarchical_topics.head(30),
        use_container_width=True
    )
else:
    st.info("💡 主题数量不足以生成层级结构（需要至少3个主题）")

st.markdown("---")

# 6. 主题文档详细浏览
st.subheader("6️⃣ 主题文档详细浏览")
st.write("按主题浏览包含的具体文档")

col1, col2 = st.columns([1, 1])

with col1:
    browse_topic = st.selectbox(
        "选择要浏览的主题",
        options=valid_topics,
        format_func=lambda x: f"话题{int(x)}: {topic_info[topic_info['Topic']==x]['Name'].iloc[0]}",
        key="browse"
    )

with col2:
    n_docs = st.slider("显示文档数", 1, 20, 5, key="docs")

# 获取该主题的文档
topic_docs = get_documents_by_topic(df, topics, browse_topic, top_n=n_docs)

if not topic_docs.empty:
    st.info(f"📄 该主题共包含 {len(df[topics == browse_topic])} 条文档，显示前 {len(topic_docs)} 条")
    
    for idx, (_, doc) in enumerate(topic_docs.iterrows(), 1):
        with st.expander(f"📄 文档 {idx} - {doc['source_text'][:50]}..."):
            st.write(f"**完整文本**: {doc['source_text']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                sentiment_badge = "😊" if doc['sentiment'] == 'positive' else ("😐" if doc['sentiment'] == 'neutral' else "😞")
                st.write(f"**情感** {sentiment_badge}: {translate_sentiment(doc['sentiment'])}")
            
            with col2:
                risk_color = "🔴" if doc['risk_level'] in ['critical', 'high'] else ("🟡" if doc['risk_level'] == 'medium' else "🟢")
                st.write(f"**风险** {risk_color}: {translate_risk(doc['risk_level'])}")
            
            with col3:
                st.write(f"**来源**: {doc.get('source', 'Unknown')}")
else:
    st.warning(f"⚠️ 该主题下没有文档")

st.markdown("---")

# 7. 统计摘要
st.subheader("7️⃣ 统计摘要")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总主题数", len(topic_info) - 1)

with col2:
    largest = topic_info[topic_info['Topic'] != -1].nlargest(1, 'Count')
    if not largest.empty:
        st.metric("最大主题文档数", int(largest.iloc[0]['Count']))

with col3:
    st.metric("总文档数", len(df))

with col4:
    noise_count = len(df[topics == -1])
    noise_pct = noise_count / len(df) * 100
    st.metric("噪声文档比例", f"{noise_pct:.1f}%", delta=f"{noise_count} 条")

st.markdown("---")

st.info("""
💡 **高级功能说明**:
- **c-TF-IDF分数衰减**: 识别最优词汇数，避免噪声词汇
- **关键词权重分析**: 理解每个主题的核心特征
- **情感/风险分布**: 发现特定主题与情感/风险的关联
- **层级结构**: 优化主题数量和组织
""")
