"""
互动分析工具 - Phase 9 优化版
使用LLM标注的现有话题数据，无需BERTopic训练
秒开加载，Cloud友好
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor,
    get_topic_comparison_data,
    get_actor_statistics_summary
)
from utils.chart_builder import (
    create_horizontal_bar,
    create_stacked_bar
)
from utils.components import (
    display_search_results,
    display_opinion_batch
)
import json

st.set_page_config(page_title="互动分析工具", page_icon="🔮", layout="wide")

st.title("🔮 互动分析工具")
st.write("基于LLM标注的智能分析 - 秒开，无需等待模型训练")

# 加载数据（不缓存，确保数据最新）
def load_data():
    return load_analysis_data()

df = load_data()

st.success(f"✅ 数据已加载：{len(df)}条意见 | {df['topic'].nunique()}个话题")

st.markdown("---")

# 8个Tab
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📄 单条意见分析",
    "📊 话题分布",
    "🔍 关键词搜索",
    "🏷️ 话题管理",
    "⚡ 话题对比",
    "👥 参与方分析",
    "⭐ 代表意见",
    "💾 导出报告"
])

# ============================================================================
# Tab 1: 单条意见详细分析
# ============================================================================
with tab1:
    st.subheader("📄 单条意见分析")
    st.write("查看完整的意见内容和LLM标注")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        doc_idx = st.slider(
            "选择意见",
            0, len(df) - 1, 0,
            help="滑动选择要查看的意见"
        )
    with col2:
        st.metric("当前编号", f"#{doc_idx}")
    
    st.markdown("---")
    
    # 显示完整意见
    row = df.iloc[doc_idx]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📝 意见内容:**")
        st.info(row['source_text'])
    
    with col2:
        st.write("**🏷️ LLM标注结果:**")
        
        label_data = f"""
**情感**: {translate_sentiment(row['sentiment'])}
**置信度**: {row['sentiment_confidence']:.2%}

**话题**: {translate_topic(row['topic'])}
**置信度**: {row['topic_confidence']:.2%}

**风险等级**: {translate_risk(row['risk_level'])}
**置信度**: {row['risk_confidence']:.2%}

**参与方**: {translate_actor(row['actor'])}
**置信度**: {row['actor_confidence']:.2%}

**模式**: {row['pattern']}
**置信度**: {row['pattern_confidence']:.2%}
"""
        st.code(label_data, language="text")
    
    # 显示相同话题的其他意见
    st.markdown("---")
    st.write(f"**同话题的其他意见** ({translate_topic(row['topic'])})")
    
    same_topic = df[df['topic'] == row['topic']].head(5)
    for i, (idx, item) in enumerate(same_topic.iterrows(), 1):
        with st.expander(f"意见 {i} - 风险等级: {translate_risk(item['risk_level'])}"):
            st.write(item['source_text'][:200] + "...")

# ============================================================================
# Tab 2: 话题分布统计
# ============================================================================
with tab2:
    st.subheader("📊 话题分布统计")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**话题热度排行**")
        topic_dist = df['topic'].value_counts()
        topic_labels = [translate_topic(t) for t in topic_dist.index]
        
        fig = create_horizontal_bar(
            topic_labels,
            topic_dist.values,
            title="话题热度排行"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**话题-情感交叉分布**")
        
        cross_tab = pd.crosstab(
            df['topic'].apply(translate_topic),
            df['sentiment'].apply(translate_sentiment)
        )
        
        fig = create_stacked_bar(
            cross_tab,
            title="话题-情感交叉分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 话题详情表格
    st.write("**各话题统计详情**")
    
    topic_summary = df.groupby('topic').agg({
        'sentiment': lambda x: (x == 'negative').sum(),  # 负面数
        'risk_level': lambda x: ((x == 'critical') | (x == 'high')).sum(),  # 高风险数
        'source_text': 'count'  # 总数
    }).rename(columns={
        'sentiment': '负面意见数',
        'risk_level': '高风险数',
        'source_text': '总数'
    })
    
    topic_summary['负面占比'] = (topic_summary['负面意见数'] / topic_summary['总数'] * 100).round(1).astype(str) + '%'
    topic_summary['风险占比'] = (topic_summary['高风险数'] / topic_summary['总数'] * 100).round(1).astype(str) + '%'
    topic_summary.index = topic_summary.index.map(translate_topic)
    
    st.dataframe(topic_summary, use_container_width=True)

# ============================================================================
# Tab 3: 关键词搜索
# ============================================================================
with tab3:
    st.subheader("🔍 关键词搜索")
    st.write("输入关键词，找到相关意见")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        keyword = st.text_input(
            "输入搜索关键词",
            placeholder="如：政策、税收、风险...",
            help="支持中文关键词"
        )
    
    with col2:
        match_type = st.selectbox(
            "匹配方式",
            ["包含", "精确"]
        )
    
    with col3:
        max_results = st.number_input("最多显示", min_value=5, max_value=50, value=10)
    
    if keyword:
        if match_type == "包含":
            results = df[df['source_text'].str.contains(keyword, case=False, na=False)]
        else:
            results = df[df['source_text'] == keyword]
        
        # 使用通用搜索结果展示函数（消除手动循环）
        display_search_results(results, keyword=keyword, max_items=max_results)

# ============================================================================
# Tab 4: 话题管理和标签编辑
# ============================================================================
with tab4:
    st.subheader("🏷️ 话题标签编辑")
    st.write("查看或修改话题标签的显示名称")
    
    # 当前的话题标签映射
    st.write("**当前话题标签**")
    
    current_topics = df['topic'].unique()
    
    topic_mapping = {}
    
    cols = st.columns(2)
    col_idx = 0
    
    for topic in sorted(current_topics):
        with cols[col_idx % 2]:
            translated = translate_topic(topic)
            count = len(df[df['topic'] == topic])
            
            st.write(f"**{translated}** ({count}条)")
            
            new_label = st.text_input(
                f"编辑标签: {topic}",
                value=translated,
                key=f"label_{topic}",
                label_visibility="collapsed"
            )
            
            topic_mapping[topic] = new_label
            col_idx += 1
    
    st.markdown("---")
    
    # 导出/导入标签配置
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 导出标签配置"):
            st.json(topic_mapping)
    
    with col2:
        st.write("**批量导入标签（JSON格式）**")
        custom_json = st.text_area(
            "粘贴JSON",
            placeholder='{"topic1": "显示名称1", ...}',
            height=150,
            label_visibility="collapsed"
        )

# ============================================================================
# Tab 5: 话题对比分析
# ============================================================================
with tab5:
    st.subheader("⚡ 话题对比分析")
    st.write("比较不同话题的特征")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_topics = st.multiselect(
            "选择要对比的话题",
            options=df['topic'].unique(),
            default=df['topic'].unique()[:2] if len(df['topic'].unique()) >= 2 else df['topic'].unique(),
            format_func=translate_topic
        )
    
    if selected_topics:
        st.markdown("---")
        
        # 对比数据（使用缓存函数）
        comparison_df = get_topic_comparison_data(df, selected_topics)
        st.dataframe(comparison_df, use_container_width=True)
        
        # 可视化对比
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**话题样本量对比**")
            fig = px.bar(
                comparison_df,
                x='话题',
                y='总数',
                color='话题'
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Tab 6: 参与方分析
# ============================================================================
with tab6:
    st.subheader("👥 参与方分析")
    st.write("查看不同参与方的舆论特征（自动拆分复合标签）")
    
    # 拆分复合参与方标签（如 "consumer|government" → ["consumer", "government"]）
    all_actors = []
    for actors_str in df['actor']:
        if pd.notna(actors_str):
            actors = [a.strip() for a in str(actors_str).split('|')]
            all_actors.extend(actors)
    
    actor_series = pd.Series(all_actors)
    actor_dist = actor_series.value_counts()
    
    # 调试信息
    st.info(f"[调试] 拆分后参与方数: {len(actor_dist)} | 总记录数: {len(df)} | 拆分后总数: {len(all_actors)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**参与方分布**")
        fig = px.pie(
            values=actor_dist.values,
            names=[translate_actor(a) for a in actor_dist.index],
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**参与方-风险分布**")
        
        # 为每个拆分后的参与方创建对应的风险分布
        actor_risk_data = []
        
        for actor in actor_dist.index:
            # 找出包含这个参与方的所有记录（支持复合标签）
            pattern = rf'(^|\|){actor}($|\|)'
            mask = df['actor'].str.contains(pattern, na=False, regex=True)
            actor_risks = df[mask]['risk_level'].apply(translate_risk).value_counts()
            
            for risk_type in ['严重', '高', '中', '低']:
                actor_risk_data.append({
                    'actor': translate_actor(actor),
                    'risk': risk_type,
                    'count': actor_risks.get(risk_type, 0)
                })
        
        actor_risk_df = pd.DataFrame(actor_risk_data)
        
        fig = px.bar(
            actor_risk_df,
            x='actor',
            y='count',
            color='risk',
            barmode='stack',
            color_discrete_map={
                '严重': '#8b0000',
                '高': '#ff6b6b',
                '中': '#ffa500',
                '低': '#00cc96'
            }
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 参与方统计表（使用缓存函数）
    st.write("**参与方统计详情**")
    actor_summary_df = get_actor_statistics_summary(df)
    st.dataframe(actor_summary_df, use_container_width=True)

# ============================================================================
# Tab 7: 代表意见提取
# ============================================================================
with tab7:
    st.subheader("⭐ 代表意见提取")
    st.write("每个话题最具代表性的意见")
    
    topics = sorted(df['topic'].unique())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_topic = st.selectbox(
            "选择话题",
            options=topics,
            format_func=translate_topic
        )
    
    with col2:
        top_n = st.number_input("显示Top-N", min_value=1, max_value=10, value=3)
    
    # 获取该话题的代表意见（按置信度排序，使用通用函数）
    topic_data = df[df['topic'] == selected_topic].sort_values(
        'sentiment_confidence',
        ascending=False
    ).head(top_n)
    
    # 使用通用批量展示函数（消除手动意见循环）
    display_opinion_batch(
        topic_data,
        title=f"{translate_topic(selected_topic)} 的代表意见（Top {top_n}）",
        show_fields=['sentiment', 'topic']
    )

# ============================================================================
# Tab 8: 导出报告
# ============================================================================
with tab8:
    st.subheader("💾 导出分析报告")
    st.write("生成话题分析总结报告")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**报告类型**")
        
        report_type = st.selectbox(
            "选择报告类型",
            ["话题总体统计", "话题详细分析", "风险预警"],
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("**导出格式**")
        export_format = st.selectbox(
            "选择格式",
            ["Markdown", "JSON", "CSV"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # 生成报告
    if st.button("📄 生成报告"):
        if report_type == "话题总体统计":
            
            report_md = f"""# 话题分析报告

**数据时间**: 2025年12月
**总意见数**: {len(df)}
**话题总数**: {df['topic'].nunique()}

## 话题分布

"""
            
            for topic in sorted(df['topic'].unique()):
                topic_data = df[df['topic'] == topic]
                report_md += f"""
### {translate_topic(topic)}

- 意见数: {len(topic_data)}
- 占比: {len(topic_data) / len(df) * 100:.1f}%
- 负面占比: {(topic_data['sentiment'] == 'negative').sum() / len(topic_data) * 100:.1f}%
- 高风险占比: {((topic_data['risk_level'] == 'critical') | (topic_data['risk_level'] == 'high')).sum() / len(topic_data) * 100:.1f}%
"""
            
            st.markdown(report_md)
            st.download_button(
                "⬇️ 下载 Markdown",
                report_md,
                "report.md",
                "text/markdown"
            )
        
        elif report_type == "话题详细分析":
            
            export_data = df.to_dict(orient='records')
            report_json = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            st.code(report_json[:500] + "...", language="json")
            st.download_button(
                "⬇️ 下载 JSON",
                report_json,
                "report.json",
                "application/json"
            )

st.markdown("---")
st.info("""
**本页面特点**:
- ⚡ 秒开加载（无需BERTopic训练）
- 🔮 基于LLM智能标注
- 📊 8个交互分析工具
- 💾 导出多种格式报告
""")
