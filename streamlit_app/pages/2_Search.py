"""
数据搜索和详览页面
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_analysis_data, search_by_keyword, filter_by_sentiment, filter_by_risk

st.set_page_config(page_title="数据搜索", page_icon="🔍", layout="wide")

st.title("🔍 数据搜索和详览")

@st.cache_data
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

# 显示统计
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
                    st.write(f"🎯 **情感**: {row['sentiment']}")
                with cols[1]:
                    st.write(f"📌 **话题**: {row['topic']}")
                with cols[2]:
                    st.write(f"⚠️ **风险**: {row['risk_level']}")
                with cols[3]:
                    st.write(f"👥 **参与方**: {row['actor']}")
            
            with col2:
                st.write(f"**模式**: {row['pattern']}")
            
            st.divider()
    
    st.write(f"第 {page} / {total_pages} 页")
    
else:
    st.warning("❌ 未找到匹配的结果，请调整筛选条件")

# 导出功能
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
