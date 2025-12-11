"""
数据搜索和详览页面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import (
    load_analysis_data, 
    search_by_keyword, 
    filter_by_sentiment, 
    filter_by_risk,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)

st.set_page_config(page_title="数据搜索", page_icon="🔍", layout="wide")

st.title("🔍 数据搜索和详览")

def load_data():
    return load_analysis_data()

df = load_data()

# 侧边栏过滤
st.sidebar.subheader("🔗 筛选条件")

# 情感筛选
sentiment_options = ['全部'] + df['sentiment'].unique().tolist()
selected_sentiment = st.sidebar.selectbox("情感倾向", sentiment_options)

# 风险筛选
risk_options = ['全部'] + df['risk_level'].unique().tolist()
selected_risk = st.sidebar.selectbox("风险等级", risk_options)

# 话题筛选
topic_options = ['全部'] + sorted(df['topic'].unique().tolist())
selected_topic = st.sidebar.selectbox("话题分类", topic_options)

# 关键词搜索
keyword = st.sidebar.text_input("关键词搜索", placeholder="输入关键词...")

# 应用筛选
result_df = df.copy()

if selected_sentiment != '全部':
    result_df = result_df[result_df['sentiment'] == selected_sentiment]

if selected_risk != '全部':
    result_df = result_df[result_df['risk_level'] == selected_risk]

if selected_topic != '全部':
    result_df = result_df[result_df['topic'] == selected_topic]

if keyword:
    result_df = search_by_keyword(result_df, keyword)

# Tab结构：搜索结果 + 快速分析
tab1, tab2 = st.tabs(["🔍 搜索结果", "📊 快速分析"])

with tab1:
    st.subheader(f"📊 搜索结果 (共 {len(result_df)} 条)")
    
    # 简要统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("匹配数", len(result_df))
    with col2:
        if len(result_df) > 0:
            neg_pct = len(result_df[result_df['sentiment'] == 'negative']) / len(result_df) * 100
            st.metric("负面占比", f"{neg_pct:.1f}%")
    with col3:
        if len(result_df) > 0:
            avg_conf = result_df['sentiment_confidence'].mean()
            st.metric("平均置信度", f"{avg_conf:.2f}")
    with col4:
        if len(result_df) > 0:
            high_risk = len(result_df[result_df['risk_level'].isin(['critical', 'high'])])
            st.metric("高风险数", high_risk)
    
    st.markdown("---")
    
    # 显示详细数据
    if len(result_df) > 0:
        st.subheader("📝 详细数据")
        
        # 选择显示的列
        display_cols = ['sentiment', 'topic', 'risk_level', 'actor', 'pattern', 'source_text']
        
        # 分页显示
        rows_per_page = st.selectbox("每页显示", [10, 20, 50])
        total_pages = (len(result_df) - 1) // rows_per_page + 1
        page = st.selectbox("页码", range(1, total_pages + 1))
        
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        display_df = result_df[display_cols].iloc[start_idx:end_idx].reset_index(drop=True)
        
        # 简化表格显示
        for idx, row in display_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**#{start_idx + idx + 1}**")
                    st.write(f"📝 {row['source_text'][:120]}...")
                    
                    cols = st.columns(4)
                    with cols[0]:
                        st.write(f"🎯 **情感**: {translate_sentiment(row['sentiment'])}")
                    with cols[1]:
                        st.write(f"📌 **话题**: {translate_topic(row['topic'])}")
                    with cols[2]:
                        st.write(f"⚠️ **风险**: {translate_risk(row['risk_level'])}")
                    with cols[3]:
                        st.write(f"👥 **参与方**: {translate_actor(row['actor'])}")
                
                with col2:
                    st.write(f"**模式**: {row['pattern']}")
                
                st.divider()
        
        st.write(f"第 {page} / {total_pages} 页")
            
    else:
        st.warning("❌ 未找到匹配的结果，请调整筛选条件")
    
    # 导出功能
    st.markdown("---")
    st.subheader("💾 导出数据")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 下载为CSV"):
            csv = result_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="点击下载 CSV",
                data=csv,
                file_name="opinion_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 下载为Excel"):
            import io
            buffer = io.BytesIO()
            result_df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button(
                label="点击下载 Excel",
                data=buffer,
                file_name="opinion_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

with tab2:
    st.subheader("📊 对搜索结果的实时分析")
    
    if len(result_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**情感分布（仅搜索结果）**")
            sentiment_dist = result_df['sentiment'].value_counts()
            sentiment_labels = [translate_sentiment(s) for s in sentiment_dist.index]
            
            fig_sentiment = go.Figure(data=[go.Pie(
                labels=sentiment_labels,
                values=sentiment_dist.values,
                marker=dict(colors=['#FF6B6B', '#FFD93D', '#6BCB77'])
            )])
            fig_sentiment.update_layout(height=400)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            st.write("**话题分布（Top 10）**")
            topic_dist = result_df['topic'].value_counts().head(10)
            topic_labels = [translate_topic(t) for t in topic_dist.index]
            
            fig_topic = go.Figure(data=[go.Bar(
                y=topic_labels,
                x=topic_dist.values,
                orientation='h',
                marker=dict(color=topic_dist.values, colorscale='Viridis')
            )])
            fig_topic.update_layout(height=400, xaxis_title="数量")
            st.plotly_chart(fig_topic, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**风险分布**")
            risk_dist = result_df['risk_level'].value_counts()
            risk_labels = [translate_risk(r) for r in risk_dist.index]
            
            fig_risk = go.Figure(data=[go.Bar(
                y=risk_labels,
                x=risk_dist.values,
                orientation='h',
                marker=dict(color=['#FF6B6B', '#FFA500', '#FFD93D', '#6BCB77'])
            )])
            fig_risk.update_layout(height=400, xaxis_title="数量")
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            st.write("**参与方分布（Top 10）**")
            actor_dist = result_df['actor'].value_counts().head(10)
            actor_labels = [translate_actor(a) for a in actor_dist.index]
            
            fig_actor = go.Figure(data=[go.Bar(
                y=actor_labels,
                x=actor_dist.values,
                orientation='h',
                marker=dict(color=actor_dist.values, colorscale='Plasma')
            )])
            fig_actor.update_layout(height=400, xaxis_title="数量")
            st.plotly_chart(fig_actor, use_container_width=True)
        
        st.markdown("---")
        
        # 统计摘要
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            neg_count = len(result_df[result_df['sentiment'] == 'negative'])
            neg_pct = neg_count / len(result_df) * 100
            st.metric("负面数量", f"{neg_count}", f"{neg_pct:.1f}%")
        
        with col2:
            high_risk_count = len(result_df[result_df['risk_level'].isin(['critical', 'high'])])
            high_risk_pct = high_risk_count / len(result_df) * 100
            st.metric("高风险数量", f"{high_risk_count}", f"{high_risk_pct:.1f}%")
        
        with col3:
            avg_conf = result_df['sentiment_confidence'].mean()
            st.metric("平均置信度", f"{avg_conf:.2f}", "(0-1)")
        
        with col4:
            st.metric("总数量", len(result_df))
    
    else:
        st.info("🔍 调整搜索条件查看结果的分析统计")
