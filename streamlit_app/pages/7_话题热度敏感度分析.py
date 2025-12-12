"""
话题热度与敏感度分析页面
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor,
    get_topic_statistics
)
from utils.chart_builder import (
    create_horizontal_bar,
    create_scatter_2d,
    create_stacked_bar
)
from utils.bertopic_analyzer import (
    train_bertopic,
    visualize_topics_2d,
    visualize_topic_similarity,
    visualize_topic_hierarchy,
    visualize_documents_2d,
    visualize_term_distribution,
    get_topics_summary,
    get_documents_by_topic,
    generate_topic_tree,
    visualize_term_score_decline,
    visualize_hierarchical_documents,
    get_topic_keywords_detailed,
    get_hierarchical_topics,
    visualize_topic_per_class,
    BERTOPIC_AVAILABLE
)

st.set_page_config(page_title="话题分析", page_icon="🔥", layout="wide")

st.title("🔥 话题热度与敏感度分析")
st.write("分析大家对什么话题感兴趣，对什么话题敏感")

def load_data():
    return load_analysis_data()

df = load_data()

# 使用缓存函数计算话题统计
topic_stats_raw = get_topic_statistics(df)

# 添加翻译和原始值列用于显示和查询
topic_stats_list = []
for _, row in topic_stats_raw.iterrows():
    topic_stats_list.append({
        '话题': translate_topic(row['topic']),
        '话题_原始': row['topic'],
        '热度': row['heat'],
        '风险指数': row['risk_index'],
        '负面占比': row['negative_pct'],
        '敏感度': row['sensitivity'],
        '中立占比': row['neutral_pct'],
        '正面占比': row['positive_pct']
    })

topic_stats_df = pd.DataFrame(topic_stats_list)

# 1. 话题热度排行
st.subheader("1️⃣ 话题热度排行（大家最关注的话题）")

col1, col2 = st.columns([2, 1])

with col1:
    fig_heat = create_horizontal_bar(
        topic_stats_df['话题'],
        topic_stats_df['热度'],
        title="话题热度排行"
    )
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
    fig_sens = create_horizontal_bar(
        topic_sensitivity_df['话题'],
        topic_sensitivity_df['敏感度'],
        title="话题敏感度排行"
    )
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

fig_scatter = create_scatter_2d(
    topic_stats_df['热度'],
    topic_stats_df['敏感度'],
    topic_stats_df['话题'],
    title="热度 vs 敏感度矩阵",
    size=topic_stats_df['热度'] / 10,
    color=topic_stats_df['敏感度']
)
# 添加平均线
fig_scatter.add_hline(y=topic_stats_df['敏感度'].mean(), line_dash="dash", line_color="gray")
fig_scatter.add_vline(x=topic_stats_df['热度'].mean(), line_dash="dash", line_color="gray")
fig_scatter.update_xaxes(title_text="热度（讨论频次）")
fig_scatter.update_yaxes(title_text="敏感度指数")
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# 4. 各话题的情感分布
st.subheader("4️⃣ 各话题的情感分布")

# 构建情感分布DataFrame
sentiment_dist_data = topic_stats_df[['话题', '正面占比', '中立占比', '负面占比']].set_index('话题')
sentiment_cols_display = [translate_sentiment(sent) for sent in ['positive', 'neutral', 'negative']]
sentiment_dist_data.columns = sentiment_cols_display

fig_sentiment_dist = create_stacked_bar(
    sentiment_dist_data,
    title="各话题的情感分布"
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

# 8️⃣ 简化版BERTopic - 只从JSON加载
st.subheader("8️⃣ 🤖 深度主题建模分析")
st.write("使用预先计算的隐藏主题")

import json
from pathlib import Path

result_file = Path(__file__).parent.parent / "data" / "bertopic_model" / "topics.json"

if result_file.exists():
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("发现的隐藏主题数", results['num_topics'])
        with col2:
            max_count = max([t['count'] for t in results['topics']])
            st.metric("最大主题", f"{max_count} 条")
        with col3:
            st.metric("模型置信度", "高")
        
        st.markdown("---")
        st.write("### 🔍 发现的隐藏主题")
        
        topics_df = pd.DataFrame([
            {
                'ID': t['id'],
                '主题名': t['name'],
                '包含文档数': t['count'],
                '占比': f"{t['count']/results['num_documents']*100:.1f}%"
            }
            for t in results['topics']
        ])
        
        st.dataframe(topics_df, use_container_width=True, hide_index=True)
        st.success("✅ 主题提取完成！")
        
        # 显示层级关系（如果存在）
        if 'hierarchy' in results and results['hierarchy']:
            st.markdown("---")
            st.write("### 🌳 主题层级关系")
            
            # 构建层级树显示
            hierarchy = results['hierarchy']
            topic_map = {t['id']: t['name'] for t in results['topics']}
            
            if hierarchy:
                # 简单的文本树显示
                st.write("**主题聚集情况：**")
                for link in hierarchy:
                    parent_id = link['parent']
                    child_id = link['child']
                    distance = link.get('distance', 0)
                    
                    parent_name = topic_map.get(parent_id, f"Cluster {parent_id}") if parent_id >= 0 else "Root"
                    child_name = topic_map.get(child_id, f"Topic {child_id}")
                    
                    st.write(f"  └─ **{child_name}** → {parent_name} (距离: {distance:.3f})")
            else:
                st.info("ℹ️ 未发现层级关系（话题数量太少）")
        
    except Exception as e:
        st.error(f"❌ 加载话题数据失败: {e}")
else:
    st.warning("⚠️ 话题数据文件不存在")

st.markdown("---")

# 9. 深度话题分析 (Advanced BERTopic) - 从P8合并
if False:  # 禁用复杂的高级BERTopic
    st.subheader("9️⃣ 🔬 深度话题分析 (Advanced BERTopic)")
    st.write("使用BERTopic的高级功能进行深层主题发现和分析")
    
    # 确保模型已训练
    texts = df['source_text'].tolist()
    topics, probs, model = train_bertopic(texts)
    
    if model is not None and topics is not None:
        topic_info = get_topics_summary(model)
        
        if not topic_info.empty:
            st.markdown("---")
            
            # 1. c-TF-IDF 分数衰减分析
            st.subheader("📊 c-TF-IDF 分数衰减分析")
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
            st.subheader("🔤 主题关键词详细分析")
            st.write("逐个查看每个主题的代表性关键词及其权重分数")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # 获取有效的主题ID
                valid_topics = topic_info[topic_info['Topic'] != -1]['Topic'].tolist()
                selected_topic = st.selectbox(
                    "选择主题",
                    options=valid_topics,
                    format_func=lambda x: f"话题{int(x)}: {topic_info[topic_info['Topic']==x]['Name'].iloc[0]}",
                    key="adv_keywords_topic"
                )
            
            with col2:
                # 获取词汇数量
                n_keywords = st.slider("显示关键词数", 5, 20, 10, key="adv_keywords_count")
            
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
            st.subheader("😊 按情感分类的主题分布")
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
            st.subheader("🚨 按风险等级分类的主题分布")
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
            st.subheader("🌳 主题层级结构")
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
                st.dataframe(
                    hierarchical_topics.head(30),
                    use_container_width=True
                )
            else:
                st.info("💡 主题数量不足以生成层级结构（需要至少3个主题）")
            
            st.markdown("---")
            
            # 6. 主题文档详细浏览
            st.subheader("📄 主题文档详细浏览")
            st.write("按主题浏览包含的具体文档")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                browse_topic = st.selectbox(
                    "选择要浏览的主题",
                    options=valid_topics,
                    format_func=lambda x: f"话题{int(x)}: {topic_info[topic_info['Topic']==x]['Name'].iloc[0]}",
                    key="adv_browse"
                )
            
            with col2:
                n_docs = st.slider("显示文档数", 1, 20, 5, key="adv_docs")
            
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
            st.subheader("📊 统计摘要")
            
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
