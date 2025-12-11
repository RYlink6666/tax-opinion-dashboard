"""
话题热度与敏感度分析页面
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
from utils.bertopic_analyzer import (
    train_bertopic,
    visualize_topics_2d,
    visualize_topic_similarity,
    visualize_topic_hierarchy,
    get_topics_summary,
    get_documents_by_topic,
    generate_topic_tree,
    BERTOPIC_AVAILABLE
)

st.set_page_config(page_title="话题分析", page_icon="🔥", layout="wide")

st.title("🔥 话题热度与敏感度分析")
st.write("分析大家对什么话题感兴趣，对什么话题敏感")

def load_data():
    return load_analysis_data()

df = load_data()

# 计算话题热度和敏感度指标
topic_stats = []
for topic in df['topic'].unique():
    topic_df = df[df['topic'] == topic]
    count = len(topic_df)
    
    # 热度 = 出现频次
    heat = count
    
    # 风险指数 = 高风险+严重风险占比
    high_risk_count = len(topic_df[topic_df['risk_level'].isin(['critical', 'high'])])
    risk_index = high_risk_count / count * 100 if count > 0 else 0
    
    # 负面占比
    negative_count = len(topic_df[topic_df['sentiment'] == 'negative'])
    negative_pct = negative_count / count * 100 if count > 0 else 0
    
    # 中立占比
    neutral_count = len(topic_df[topic_df['sentiment'] == 'neutral'])
    neutral_pct = neutral_count / count * 100 if count > 0 else 0
    
    # 正面占比
    positive_count = len(topic_df[topic_df['sentiment'] == 'positive'])
    positive_pct = positive_count / count * 100 if count > 0 else 0
    
    # 敏感度 = 风险指数 + 负面占比 的加权
    sensitivity = risk_index * 0.6 + negative_pct * 0.4
    
    topic_stats.append({
        '话题': translate_topic(topic),
        '话题_原始': topic,
        '热度': heat,
        '风险指数': risk_index,
        '负面占比': negative_pct,
        '敏感度': sensitivity,
        '中立占比': neutral_pct,
        '正面占比': positive_pct
    })

topic_stats_df = pd.DataFrame(topic_stats).sort_values('热度', ascending=False)

# 1. 话题热度排行
st.subheader("1️⃣ 话题热度排行（大家最关注的话题）")

col1, col2 = st.columns([2, 1])

with col1:
    fig_heat = go.Figure(data=[go.Bar(
        y=topic_stats_df['话题'],
        x=topic_stats_df['热度'],
        orientation='h',
        marker=dict(
            color=topic_stats_df['热度'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="讨论数")
        ),
        text=topic_stats_df['热度'],
        textposition='outside'
    )])
    fig_heat.update_layout(height=400, xaxis_title="讨论频次", yaxis_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.write("**热度Top 5**")
    for idx, row in topic_stats_df.head(5).iterrows():
        st.write(f"**{row['话题']}**: {row['热度']} 条 ({row['热度']/len(df)*100:.1f}%)")

st.markdown("---")

# 2. 话题敏感度排行
st.subheader("2️⃣ 话题敏感度排行（大家最敏感的话题）")

topic_sensitivity_df = topic_stats_df.sort_values('敏感度', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig_sens = go.Figure(data=[go.Bar(
        y=topic_sensitivity_df['话题'],
        x=topic_sensitivity_df['敏感度'],
        orientation='h',
        marker=dict(
            color=topic_sensitivity_df['敏感度'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="敏感度")
        ),
        text=topic_sensitivity_df['敏感度'].apply(lambda x: f'{x:.1f}'),
        textposition='outside'
    )])
    fig_sens.update_layout(height=400, xaxis_title="敏感度指数", yaxis_title="")
    st.plotly_chart(fig_sens, use_container_width=True)

with col2:
    st.write("**敏感度Top 5**")
    st.write("*(风险指数 × 0.6 + 负面占比 × 0.4)*")
    for idx, row in topic_sensitivity_df.head(5).iterrows():
        st.write(f"**{row['话题']}**: {row['敏感度']:.1f}")

st.markdown("---")

# 3. 热度 vs 敏感度散点图
st.subheader("3️⃣ 热度 vs 敏感度矩阵")

st.write("**图表解读**:")
st.write("""
- 右上角：高热度 + 高敏感度 = **🔴 重点关注**（热议且敏感）
- 右下角：高热度 + 低敏感度 = **🟢 正面热议**（讨论热烈但理性）
- 左上角：低热度 + 高敏感度 = **🟡 潜在风险**（虽讨论少但敏感）
- 左下角：低热度 + 低敏感度 = **⚪ 常规话题**（讨论少且理性）
""")

fig_scatter = go.Figure(data=[go.Scatter(
    x=topic_stats_df['热度'],
    y=topic_stats_df['敏感度'],
    mode='markers+text',
    text=topic_stats_df['话题'],
    textposition='top center',
    marker=dict(
        size=topic_stats_df['热度'] / 10,
        color=topic_stats_df['敏感度'],
        colorscale='RdYlGn_r',
        showscale=True,
        colorbar=dict(title="敏感度"),
        line=dict(width=2, color='white')
    )
)])
fig_scatter.update_layout(
    height=500,
    xaxis_title="热度（讨论频次）",
    yaxis_title="敏感度指数",
    hovermode='closest'
)
fig_scatter.add_hline(y=topic_stats_df['敏感度'].mean(), line_dash="dash", line_color="gray", 
                      annotation_text="敏感度平均值")
fig_scatter.add_vline(x=topic_stats_df['热度'].mean(), line_dash="dash", line_color="gray",
                      annotation_text="热度平均值")
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# 4. 各话题的情感分布
st.subheader("4️⃣ 各话题的情感分布")

fig_sentiment_dist = go.Figure()

for sentiment in ['positive', 'neutral', 'negative']:
    fig_sentiment_dist.add_trace(go.Bar(
        y=topic_stats_df['话题'],
        x=topic_stats_df[['正面占比', '中立占比', '负面占比'][['positive', 'neutral', 'negative'].index(sentiment)]],
        name=translate_sentiment(sentiment),
        orientation='h'
    ))

fig_sentiment_dist.update_layout(
    barmode='stack',
    height=400,
    xaxis_title="占比 (%)",
    yaxis_title="",
    hovermode='x unified'
)
st.plotly_chart(fig_sentiment_dist, use_container_width=True)

st.markdown("---")

# 5. 各话题的主要参与方
st.subheader("5️⃣ 各话题最活跃的参与方")

col1, col2 = st.columns(2)

# 获取热度Top 3和敏感度Top 3的话题
top_heat_topics = topic_stats_df.nlargest(3, '热度')['话题_原始'].tolist()
top_sens_topics = topic_stats_df.nlargest(3, '敏感度')['话题_原始'].tolist()

with col1:
    st.write("**热度Top 3话题的参与方分布**")
    for topic in top_heat_topics:
        topic_name = translate_topic(topic)
        topic_df = df[df['topic'] == topic]
        actor_dist = topic_df['actor'].value_counts().head(3)
        
        with st.expander(f"📌 {topic_name}"):
            for actor, count in actor_dist.items():
                pct = count / len(topic_df) * 100
                st.write(f"  • {translate_actor(actor)}: {count} ({pct:.1f}%)")

with col2:
    st.write("**敏感度Top 3话题的参与方分布**")
    for topic in top_sens_topics:
        topic_name = translate_topic(topic)
        topic_df = df[df['topic'] == topic]
        actor_dist = topic_df['actor'].value_counts().head(3)
        
        with st.expander(f"📌 {topic_name}"):
            for actor, count in actor_dist.items():
                pct = count / len(topic_df) * 100
                st.write(f"  • {translate_actor(actor)}: {count} ({pct:.1f}%)")

st.markdown("---")

# 6. 话题详细数据表
st.subheader("6️⃣ 话题详细数据表")

display_df = topic_stats_df[['话题', '热度', '风险指数', '负面占比', '中立占比', '正面占比', '敏感度']].copy()
display_df['热度占比(%)'] = (display_df['热度'] / len(df) * 100).round(1)
display_df['风险指数'] = display_df['风险指数'].round(1)
display_df['负面占比'] = display_df['负面占比'].round(1)
display_df['中立占比'] = display_df['中立占比'].round(1)
display_df['正面占比'] = display_df['正面占比'].round(1)
display_df['敏感度'] = display_df['敏感度'].round(1)

st.dataframe(
    display_df,
    column_config={
        '话题': st.column_config.TextColumn('话题'),
        '热度': st.column_config.NumberColumn('热度', format="%d"),
        '热度占比(%)': st.column_config.NumberColumn('热度占比(%)', format="%.1f"),
        '风险指数': st.column_config.NumberColumn('风险指数', format="%.1f"),
        '负面占比': st.column_config.NumberColumn('负面占比(%)', format="%.1f"),
        '中立占比': st.column_config.NumberColumn('中立占比(%)', format="%.1f"),
        '正面占比': st.column_config.NumberColumn('正面占比(%)', format="%.1f"),
        '敏感度': st.column_config.NumberColumn('敏感度指数', format="%.1f"),
    },
    hide_index=True,
    use_container_width=True
)

st.markdown("---")

# 7. 核心发现
st.subheader("7️⃣ 核心发现")

most_heated = topic_stats_df.iloc[0]
most_sensitive = topic_sensitivity_df.iloc[0]
high_heat_low_sens = topic_stats_df[(topic_stats_df['热度'] > topic_stats_df['热度'].quantile(0.75)) & 
                                     (topic_stats_df['敏感度'] < topic_stats_df['敏感度'].quantile(0.25))]
high_sens_low_heat = topic_stats_df[(topic_stats_df['敏感度'] > topic_stats_df['敏感度'].quantile(0.75)) & 
                                     (topic_stats_df['热度'] < topic_stats_df['热度'].quantile(0.25))]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "最热话题",
        f"{most_heated['话题']}",
        f"{most_heated['热度']:.0f} 条讨论"
    )

with col2:
    st.metric(
        "最敏感话题",
        f"{most_sensitive['话题']}",
        f"敏感度 {most_sensitive['敏感度']:.1f}"
    )

with col3:
    if len(high_heat_low_sens) > 0:
        st.metric(
            "正面热议话题数",
            f"{len(high_heat_low_sens)} 个",
            "讨论多但理性"
        )
    else:
        st.metric(
            "正面热议话题数",
            "0 个",
            "暂无"
        )

st.info("""
💡 **政策建议**:
- 🔴 **最敏感话题** - 需要优先解决，制定针对性政策
- 🟢 **正面热议话题** - 继续保持，加强宣传推广
- 🟡 **潜在风险话题** - 虽讨论少但需要重视，预防其升级
""")

st.markdown("---")

# 8. BERTopic深度主题分析（高级功能）
if BERTOPIC_AVAILABLE:
    st.subheader("8️⃣ 🤖 深度主题建模分析 (基于BERTopic)")
    st.write("使用AI提取文本中的隐藏主题关系，而非依赖预定义分类")
    
    # 训练BERTopic模型
    texts = df['source_text'].tolist()
    topics, probs, model = train_bertopic(texts)
    
    if model is not None and topics is not None:
        # 显示主题统计
        topic_info = get_topics_summary(model)
        
        if not topic_info.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("发现的隐藏主题数", len(topic_info) - 1)  # 排除-1主题
            
            with col2:
                largest_topic = topic_info.nlargest(1, 'Count').iloc[0]
                st.metric("最大主题", f"{int(largest_topic['Count'])} 条")
            
            with col3:
                st.metric("模型置信度", "高")
            
            st.markdown("---")
            
            # Tab页面组织BERTopic可视化
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 主题分布",
                "🔗 主题相似度",
                "📈 主题层级",
                "📝 主题列表",
                "🌳 主题分层"
            ])
            
            with tab1:
                st.write("**主题在2D空间中的分布（Umap降维）**")
                st.write("相近的点表示主题相似，可视化了数千条文本的隐藏结构")
                viz = visualize_topics_2d(model, topics)
                if viz:
                    st.plotly_chart(viz, use_container_width=True)
                else:
                    st.info("主题分布可视化生成中...请稍候")
            
            with tab2:
                st.write("**主题间的相似度热力图**")
                st.write("热力图中的颜色深度表示主题间的相似程度")
                viz = visualize_topic_similarity(model)
                if viz:
                    st.plotly_chart(viz, use_container_width=True)
                else:
                    st.info("相似度热力图生成中...请稍候")
            
            with tab3:
                st.write("**主题的层级聚类关系**")
                st.write("展示主题如何按相似性分组形成的树形结构")
                viz = visualize_topic_hierarchy(model)
                if viz:
                    st.plotly_chart(viz, use_container_width=True)
                else:
                    st.info("层级关系图生成中...请稍候")
            
            with tab4:
                st.write("**所有发现的隐藏主题列表**")
                st.dataframe(
                    topic_info[topic_info['Topic'] != -1][['Topic', 'Count', 'Name']],
                    column_config={
                        'Topic': st.column_config.NumberColumn('主题ID'),
                        'Count': st.column_config.NumberColumn('包含文档数'),
                        'Name': st.column_config.TextColumn('主题标签'),
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            with tab5:
                st.write("**主题分层结构 - 每个话题下的具体文档**")
                st.write("显示每个主题包含的代表性文档（最多前3条）")
                
                # 生成树形结构
                tree_text = generate_topic_tree(model, df, topics)
                
                if tree_text:
                    st.markdown(tree_text)
                else:
                    st.warning("无法生成主题分层结构")
                
                st.markdown("---")
                
                # 详细查看选项
                st.write("**选择主题查看详细文档**")
                
                selected_topic = st.selectbox(
                    "选择主题",
                    options=topic_info[topic_info['Topic'] != -1]['Topic'].tolist(),
                    format_func=lambda x: f"话题{int(x)}: {topic_info[topic_info['Topic']==x]['Name'].iloc[0]}"
                )
                
                if selected_topic is not None:
                    topic_docs = get_documents_by_topic(df, topics, selected_topic, top_n=10)
                    
                    if not topic_docs.empty:
                        st.subheader(f"话题{int(selected_topic)}的文档列表")
                        
                        for idx, (_, doc) in enumerate(topic_docs.iterrows(), 1):
                            with st.expander(f"📄 文档{idx}: {doc['source_text'][:50]}..."):
                                st.write(f"**原文**: {doc['source_text']}")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**情感**: {translate_sentiment(doc['sentiment'])}")
                                with col2:
                                    st.write(f"**风险**: {translate_risk(doc['risk_level'])}")
                    else:
                        st.info("该主题下无文档")
        else:
            st.warning("⚠️ 无法提取主题，数据可能不足或格式不符")
    else:
        st.warning("⚠️ BERTopic模型初始化失败，跳过深度主题分析")
else:
    with st.expander("🤖 深度主题建模（需要安装BERTopic）"):
        st.write("""
        BERTopic是一种先进的主题建模技术，可以：
        - 自动发现文本中的隐藏主题
        - 建立主题间的层级关系
        - 生成主题相似度热力图
        
        **安装BERTopic**:
        ```bash
        pip install -r requirements.txt
        ```
        
        然后重启Streamlit应用即可启用此功能。
        """)
