"""
Phase 10A: 优先级2 - 图表组件库

消除Plotly图表代码重复。提供标准化的图表生成函数，
在多个页面（P1, P3, P4, P5, P7, P9）复用。

核心思想：将重复的 go.Figure(...) 代码提取为函数，
只需传入数据和标签即可。
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# ============================================================================
# 1. 分布图表
# ============================================================================

def create_distribution_pie(values, labels, title="", hole=0.3):
    """创建分布饼/圆环图（标准用法）
    
    用于展示：
    - 情感分布（正面/中立/负面）
    - 风险分布（严重/高/中/低）
    - 参与方分布（各演员占比）
    
    参数：
        values: 数值列表或Series.values
        labels: 标签列表（中文）
        title: 图表标题
        hole: 圆环大小（0表示饼图，0.3表示圆环）
    
    用法：
        sentiment_dist = df['sentiment'].value_counts()
        sentiment_labels = [translate_sentiment(k) for k in sentiment_dist.index]
        
        # 从这样：
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_labels,
            values=sentiment_dist.values,
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set2)
        )])
        fig.update_layout(height=400, showlegend=True)
        
        # 改成这样：
        fig = create_distribution_pie(
            sentiment_dist.values,
            sentiment_labels,
            title="情感分布"
        )
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker=dict(colors=px.colors.qualitative.Set2)
    )])
    fig.update_layout(
        height=350,
        showlegend=True,
        title=title if title else ""
    )
    return fig


def create_horizontal_bar(labels, values, title="", colorscale='Blues'):
    """创建横向柱状图
    
    用于展示：
    - 话题热度排行
    - 风险分布
    - Top N统计
    
    参数：
        labels: 标签列表（中文）
        values: 数值列表或Series.values
        title: 图表标题
        colorscale: 颜色方案（本参数已弃用，自动使用渐进蓝色）
    
    用法：
        topic_dist = df['topic'].value_counts().head(6)
        topic_labels = [translate_topic(k) for k in topic_dist.index]
        
        fig = create_horizontal_bar(
            topic_labels,
            topic_dist.values,
            title="话题热度排行"
        )
    """
    # 确保values是数值类型的列表
    values_list = [float(v) for v in values] if hasattr(values, '__iter__') else [float(values)]
    
    # 生成颜色列表（从浅蓝到深蓝）
    n = len(values_list)
    colors = [f'rgba(31, 119, 180, {0.4 + 0.4 * i / max(1, n-1)})' for i in range(n)]
    
    fig = go.Figure(data=[go.Bar(
        y=labels,
        x=values_list,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        text=[str(int(v)) for v in values_list],
        textposition='outside'
    )])
    fig.update_layout(
        height=max(350, 30 * len(labels)),
        title=title if title else "",
        xaxis_title="讨论数",
        yaxis_title="",
        margin=dict(l=100, r=50, t=50, b=50)
    )
    return fig


def create_vertical_bar(labels, values, title="", colorscale='Viridis'):
    """创建纵向柱状图
    
    用于展示：
    - 参与方分布
    - 模式分布
    
    参数：
        labels: 标签列表（中文）
        values: 数值列表或Series.values
        title: 图表标题
        colorscale: 颜色方案
    
    用法：
        actor_dist = df['actor'].value_counts().head(6)
        actor_labels = [translate_actor(k) for k in actor_dist.index]
        
        fig = create_vertical_bar(
            actor_labels,
            actor_dist.values,
            title="主要参与方"
        )
    """
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=values,
            colorscale=colorscale
        )
    )])
    fig.update_layout(
        height=350,
        title=title if title else "",
        xaxis_title="",
        yaxis_title="讨论数",
        xaxis_tickangle=-45
    )
    return fig


# ============================================================================
# 2. 交叉分析图表
# ============================================================================

def create_crosstab_heatmap(crosstab_df, title="", colorscale='Blues'):
    """创建交叉表热力图
    
    用于展示维度间的关系：
    - 风险×情感
    - 模式×情感
    - 参与方×话题
    - 话题×风险
    
    参数：
        crosstab_df: pd.crosstab()的结果（行为维度A，列为维度B）
        title: 图表标题
        colorscale: 颜色方案
    
    用法：
        # P3 风险分析：风险×情感
        risk_sentiment = pd.crosstab(df['risk_level'], df['sentiment'])
        
        # 从这样：
        fig = go.Figure(data=go.Heatmap(
            z=risk_sentiment.values,
            x=risk_sentiment.columns,
            y=risk_sentiment.index
        ))
        
        # 改成这样：
        fig = create_crosstab_heatmap(
            risk_sentiment,
            title="风险等级 × 情感倾向",
            colorscale='RdYlGn_r'
        )
    """
    fig = go.Figure(data=go.Heatmap(
        z=crosstab_df.values,
        x=[str(col) for col in crosstab_df.columns],
        y=[str(idx) for idx in crosstab_df.index],
        colorscale=colorscale,
        colorbar=dict(title="数量")
    ))
    fig.update_layout(
        height=400,
        title=title if title else "",
        xaxis_title="",
        yaxis_title=""
    )
    return fig


def create_grouped_bar(crosstab_df, title=""):
    """创建分组柱状图
    
    用于展示：
    - 不同参与方的情感分布
    - 不同话题的风险分布
    
    参数：
        crosstab_df: pd.crosstab()的结果
        title: 图表标题
    
    用法：
        # P5 参与方分析：参与方×情感
        actor_sentiment = pd.crosstab(df['actor'], df['sentiment'])
        
        fig = create_grouped_bar(
            actor_sentiment,
            title="参与方的情感倾向"
        )
    """
    fig = go.Figure(data=[
        go.Bar(
            name=str(col),
            x=[str(idx) for idx in crosstab_df.index],
            y=crosstab_df[col]
        )
        for col in crosstab_df.columns
    ])
    fig.update_layout(
        barmode='group',
        height=400,
        title=title if title else "",
        xaxis_title="",
        yaxis_title="记录数",
        xaxis_tickangle=-45
    )
    return fig


def create_stacked_bar(crosstab_df, title=""):
    """创建堆叠柱状图
    
    用于展示：
    - 各参与方的风险分布（堆叠）
    
    参数：
        crosstab_df: pd.crosstab()的结果
        title: 图表标题
    
    用法：
        actor_risk = pd.crosstab(df['actor'], df['risk_level'])
        
        fig = create_stacked_bar(
            actor_risk,
            title="参与方的风险分布"
        )
    """
    fig = go.Figure(data=[
        go.Bar(
            name=str(col),
            x=[str(idx) for idx in crosstab_df.index],
            y=crosstab_df[col]
        )
        for col in crosstab_df.columns
    ])
    fig.update_layout(
        barmode='stack',
        height=400,
        title=title if title else "",
        xaxis_title="",
        yaxis_title="记录数",
        xaxis_tickangle=-45
    )
    return fig


# ============================================================================
# 3. 特殊图表
# ============================================================================

def create_scatter_2d(x, y, labels, title="", size=None, color=None):
    """创建2D散点图
    
    用于BERTopic话题可视化
    
    参数：
        x, y: 坐标数组
        labels: 点标签
        title: 图表标题
        size: 点大小（可选）
        color: 点颜色（可选）
    """
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        text=labels,
        textposition='top center',
        marker=dict(
            size=size if size is not None else 10,
            color=color if color is not None else 'blue',
            showscale=True if color is not None else False
        )
    ))
    fig.update_layout(
        height=500,
        title=title if title else "",
        hovermode='closest'
    )
    return fig


# ============================================================================
# 4. 快速创建指标卡片
# ============================================================================

def display_metric_cards(metrics_dict, cols=4):
    """快速创建指标卡片组
    
    用法：
        import streamlit as st
        
        metrics = {
            '总意见数': len(df),
            '负面占比': f"{neg_pct:.1f}%",
            '高风险比例': f"{high_risk_pct:.1f}%",
            '平均置信度': f"{avg_conf:.2f}"
        }
        
        display_metric_cards(metrics, cols=4)
    
    注意：这是一个Streamlit组件，需要在Streamlit上下文中调用
    """
    import streamlit as st
    
    col_list = st.columns(cols)
    for i, (label, value) in enumerate(metrics_dict.items()):
        with col_list[i % cols]:
            st.metric(label, value)


# ============================================================================
# 5. 颜色方案配置
# ============================================================================

RISK_COLORS = {
    'critical': '#8b0000',  # 深红
    '严重': '#8b0000',
    'high': '#ff6b6b',      # 红
    '高': '#ff6b6b',
    'medium': '#ffa500',    # 橙色
    '中': '#ffa500',
    'low': '#00cc96',       # 绿
    '低': '#00cc96'
}

SENTIMENT_COLORS = {
    'positive': '#00cc96',  # 绿
    '正面': '#00cc96',
    'negative': '#ef553b',  # 红
    '负面': '#ef553b',
    'neutral': '#636efa',   # 蓝
    '中立': '#636efa'
}


def get_color_by_risk(risk_level):
    """根据风险等级获取颜色"""
    return RISK_COLORS.get(risk_level, '#999999')


def get_color_by_sentiment(sentiment):
    """根据情感获取颜色"""
    return SENTIMENT_COLORS.get(sentiment, '#999999')
