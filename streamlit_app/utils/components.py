"""
Phase 10A: 优先级3 - UI组件库

消除展开器、卡片等UI代码重复。提供标准化的Streamlit组件，
在P3, P4, P5, P9多个页面复用。
"""

import streamlit as st
import pandas as pd
from .data_loader import (
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)


# ============================================================================
# 1. 舆论展开器组件
# ============================================================================

def display_opinion_expander(row, show_fields=None, index=None):
    """显示单条舆论的展开器组件（标准用法）
    
    用于展示：
    - 原始文本
    - 情感、风险、话题、参与方等分析结果
    - 置信度信息
    
    参数：
        row: DataFrame的一行（包含source_text, sentiment, risk_level等字段）
        show_fields: 要显示的字段列表（默认显示基本4个）
        index: 序号（用于标题）
    
    用法：
        # P3 高风险舆论示例
        samples = high_risk_df.head(5)
        for idx, (_, row) in enumerate(samples.iterrows(), 1):
            display_opinion_expander(row, index=idx)
        
        # P5 参与方发言示例
        for _, row in samples.iterrows():
            display_opinion_expander(
                row,
                show_fields=['sentiment', 'risk_level', 'topic', 'actor']
            )
    """
    if show_fields is None:
        show_fields = ['sentiment', 'risk_level', 'topic', 'actor']
    
    # 生成标题
    text_preview = row['source_text'][:40] + '...' if len(row['source_text']) > 40 else row['source_text']
    if index:
        title = f"#{index} 📝 {text_preview}"
    else:
        title = f"📝 {text_preview}"
    
    with st.expander(title):
        # 显示完整原文
        st.write(f"**原文**: {row['source_text']}")
        st.markdown("---")
        
        # 显示各字段
        cols = st.columns(len(show_fields))
        for col, field in zip(cols, show_fields):
            with col:
                if field == 'sentiment':
                    display_value = translate_sentiment(row.get('sentiment', 'N/A'))
                    st.write(f"**情感**: {display_value}")
                    if 'sentiment_confidence' in row:
                        st.caption(f"置信度: {row['sentiment_confidence']:.2f}")
                
                elif field == 'risk_level':
                    display_value = translate_risk(row.get('risk_level', 'N/A'))
                    st.write(f"**风险**: {display_value}")
                    if 'risk_confidence' in row:
                        st.caption(f"置信度: {row['risk_confidence']:.2f}")
                
                elif field == 'topic':
                    display_value = translate_topic(row.get('topic', 'N/A'))
                    st.write(f"**话题**: {display_value}")
                    if 'topic_confidence' in row:
                        st.caption(f"置信度: {row['topic_confidence']:.2f}")
                
                elif field == 'actor':
                    display_value = translate_actor(row.get('actor', 'N/A'))
                    st.write(f"**参与方**: {display_value}")
                    if 'actor_confidence' in row:
                        st.caption(f"置信度: {row['actor_confidence']:.2f}")
                
                elif field == 'pattern':
                    st.write(f"**模式**: {row.get('pattern', 'N/A')}")
                    if 'pattern_confidence' in row:
                        st.caption(f"置信度: {row['pattern_confidence']:.2f}")
                
                else:
                    # 通用字段显示
                    st.write(f"**{field}**: {row.get(field, 'N/A')}")


# ============================================================================
# 2. 统计展示卡片
# ============================================================================

def display_stat_card(label, value, subtext="", color="normal"):
    """显示单个统计卡片（改进版st.metric）
    
    用法：
        display_stat_card("总意见数", len(df), "(已分析)")
        display_stat_card("负面占比", f"{neg_pct:.1f}%", "需要关注", color="warning")
    """
    with st.container():
        cols = st.columns([3, 1])
        with cols[0]:
            st.metric(label, value, subtext)
        with cols[1]:
            if color == "warning":
                st.warning("⚠️")
            elif color == "error":
                st.error("❌")
            elif color == "success":
                st.success("✅")


def display_stats_grid(metrics_dict, cols=4):
    """快速显示多个统计指标（网格排列）
    
    用法：
        metrics = {
            '总意见数': len(df),
            '高风险占比': f"{high_risk_pct:.1f}%",
            '负面舆论': f"{neg_pct:.1f}%",
            '平均置信度': f"{avg_conf:.2f}"
        }
        display_stats_grid(metrics, cols=4)
    """
    col_list = st.columns(cols)
    for i, (label, value) in enumerate(metrics_dict.items()):
        with col_list[i % cols]:
            st.metric(label, value)


# ============================================================================
# 3. 筛选面板
# ============================================================================

def create_sidebar_filters(df, with_search=True):
    """创建侧边栏筛选面板
    
    返回dict包含所有筛选条件：
    {
        'sentiment': selected_sentiment,
        'risk_level': selected_risk,
        'topic': selected_topic,
        'keyword': search_keyword
    }
    
    用法：
        # P2 意见搜索页面
        filters = create_sidebar_filters(df)
        
        # 应用筛选
        filtered_df = df.copy()
        if filters['sentiment'] != '全部':
            filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]
        if filters['risk_level'] != '全部':
            filtered_df = filtered_df[filtered_df['risk_level'] == filters['risk_level']]
        ...
    """
    st.sidebar.subheader("🔍 筛选条件")
    
    filters = {}
    
    # 情感筛选
    sentiment_options = ['全部'] + sorted(df['sentiment'].unique().tolist())
    filters['sentiment'] = st.sidebar.selectbox("情感倾向", sentiment_options)
    
    # 风险筛选
    risk_options = ['全部'] + sorted(df['risk_level'].unique().tolist())
    filters['risk_level'] = st.sidebar.selectbox("风险等级", risk_options)
    
    # 话题筛选
    topic_options = ['全部'] + sorted(df['topic'].unique().tolist())
    filters['topic'] = st.sidebar.selectbox("话题分类", topic_options)
    
    # 关键词搜索
    if with_search:
        filters['keyword'] = st.sidebar.text_input("🔎 关键词搜索", placeholder="输入关键词...")
    
    return filters


def apply_filters(df, filters):
    """应用筛选条件到DataFrame
    
    用法：
        filters = create_sidebar_filters(df)
        filtered_df = apply_filters(df, filters)
        st.info(f"找到 {len(filtered_df)} 条舆论")
    """
    result_df = df.copy()
    
    # 应用各筛选条件
    if filters.get('sentiment') and filters['sentiment'] != '全部':
        result_df = result_df[result_df['sentiment'] == filters['sentiment']]
    
    if filters.get('risk_level') and filters['risk_level'] != '全部':
        result_df = result_df[result_df['risk_level'] == filters['risk_level']]
    
    if filters.get('topic') and filters['topic'] != '全部':
        result_df = result_df[result_df['topic'] == filters['topic']]
    
    if filters.get('keyword') and filters['keyword'].strip():
        result_df = result_df[
            result_df['source_text'].str.contains(filters['keyword'], na=False, case=False)
        ]
    
    return result_df


# ============================================================================
# 4. 摘要信息框
# ============================================================================

def display_summary_box(title, stats_dict, box_type="info"):
    """显示摘要信息框
    
    用法：
        summary = {
            '总记录': len(df),
            '高风险': len(high_risk_df),
            '负面占比': f"{neg_pct:.1f}%"
        }
        display_summary_box("数据摘要", summary, box_type="info")
    """
    content = f"**{title}**\n\n"
    for key, value in stats_dict.items():
        content += f"- {key}: {value}\n"
    
    if box_type == "info":
        st.info(content)
    elif box_type == "warning":
        st.warning(content)
    elif box_type == "error":
        st.error(content)
    elif box_type == "success":
        st.success(content)
    else:
        st.write(content)


# ============================================================================
# 5. 分页显示
# ============================================================================

def paginate_dataframe(df, page_size=20):
    """为DataFrame实现分页显示
    
    返回 (start_idx, end_idx) 用于切片
    
    用法：
        start_idx, end_idx = paginate_dataframe(df, page_size=20)
        
        for _, row in df.iloc[start_idx:end_idx].iterrows():
            display_opinion_expander(row)
    """
    total_pages = (len(df) - 1) // page_size + 1
    if total_pages <= 1:
        return 0, len(df)
    
    current_page = st.slider("页码", 1, total_pages, 1)
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    
    st.caption(f"显示 {start_idx + 1}-{end_idx} / {len(df)} 条")
    
    return start_idx, end_idx


# ============================================================================
# 6. 指标对比面板
# ============================================================================

def display_comparison_panel(title, comparison_data):
    """显示对比分析面板
    
    用法：
        comparison_data = {
            '消费者': {'发言数': 100, '负面率': '25%', '高风险率': '15%'},
            '企业': {'发言数': 80, '负面率': '35%', '高风险率': '25%'},
        }
        display_comparison_panel("参与方对比", comparison_data)
    """
    st.subheader(title)
    
    # 转换为DataFrame展示
    comparison_df = pd.DataFrame(comparison_data).T
    st.dataframe(comparison_df, use_container_width=True)


# ============================================================================
# 7. 快速洞察框
# ============================================================================

def display_insight(number, text, icon="💡"):
    """显示单条洞察
    
    用法：
        display_insight(1, "负面舆论占比25.8%，主要来自中小企业")
        display_insight(2, "最敏感话题是'税收合规性'，风险指数达70%", icon="⚠️")
    """
    st.write(f"{icon} **#{number}** {text}")


def display_insights_list(insights_list):
    """显示多条洞察列表
    
    用法：
        insights = [
            "负面舆论占比25.8%，需要政策沟通",
            "商家风险担忧15%，需要扶持措施",
            "信息不对称是首要问题"
        ]
        display_insights_list(insights)
    """
    st.subheader("💡 关键发现")
    for i, insight in enumerate(insights_list, 1):
        display_insight(i, insight)
