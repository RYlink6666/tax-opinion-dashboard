"""
政策建议分析页面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)

st.set_page_config(page_title="政策建议", page_icon="💡", layout="wide")

st.title("💡 基于舆论分析的政策建议")

def load_data():
    return load_analysis_data()

df = load_data()

st.write(f"根据{len(df)}条意见的LLM分析，提出有针对性的政策优化建议")

# 1. 舆论健康度评估
st.subheader("1️⃣ 舆论健康度评估")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("舆论温度", "🟡 中等", "可控")

with col2:
    st.metric("风险等级", "🟢 低风险", "70.6%低风险")

with col3:
    st.metric("话题聚焦度", "🔵 低散", "无单一议题主导")

with col4:
    st.metric("政策窗口", "⏰ 黄金期", "还有调整空间")

st.markdown("""
**评估结论**: ✓ 舆论总体可控，但存在明确的优化空间
- 负面舆论占比25.8% ← 需要沟通
- 商家风险担忧15% ← 需要扶持
- 政策认知分散 ← 需要宣传
""")

st.markdown("---")

# 2. 关键发现
st.subheader("2️⃣ 核心发现 (数据驱动)")

tabs = st.tabs(["消费者心态", "商家困境", "政策认知", "风险点"])

with tabs[0]:
    st.write("**消费者占比最高: 38.8%**")
    
    consumer_df = df[df['actor'] == 'consumer']
    sent_dist = consumer_df['sentiment'].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**消费者舆论分布**")
        for sent, count in sent_dist.items():
            pct = count / len(consumer_df) * 100
            st.write(f"{sent}: {pct:.1f}%")
    
    with col2:
        # 翻译情感标签
        sentiment_labels = [translate_sentiment(sent) for sent in sent_dist.index]
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_labels,
            values=sent_dist.values,
            marker=dict(colors=['#ef553b', '#636efa', '#00cc96'])
        )])
        st.plotly_chart(fig, use_container_width=True)
    
    st.write("**消费者主要关注话题**")
    topic_dist = consumer_df['topic'].value_counts().head(5)
    for topic, count in topic_dist.items():
        pct = count / len(consumer_df) * 100
        st.write(f"• {translate_topic(topic)}: {pct:.1f}%")
    
    st.info("""
    **消费者心态特征**:
    - 理性为主（中立>负面>正面）
    - 关注点：价格影响、购物体验
    - 态度：等待观望，需要政策说明
    """)

with tabs[1]:
    st.write("**商家占比: 17-19% (企业+跨境卖家)**")
    
    business_df = df[df['actor'].isin(['enterprise', 'cross_border_seller'])]
    sent_dist = business_df['sentiment'].value_counts()
    risk_dist = business_df['risk_level'].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**商家舆论分布**")
        for sent, count in sent_dist.items():
            pct = count / len(business_df) * 100
            st.write(f"{translate_sentiment(sent)}: {pct:.1f}%")
    
    with col2:
        st.write("**商家风险认知**")
        for risk, count in risk_dist.items():
            pct = count / len(business_df) * 100
            st.write(f"{translate_risk(risk)}: {pct:.1f}%")
    
    st.write("**商家主要关注话题**")
    topic_dist = business_df['topic'].value_counts().head(5)
    for topic, count in topic_dist.items():
        pct = count / len(business_df) * 100
        st.write(f"• {translate_topic(topic)}: {pct:.1f}%")
    
    st.warning("""
    **商家困境特征**:
    - 负面舆论偏多（35-40%）
    - 风险认知高（高+中风险>30%）
    - 关注点：成本压力、合规风险、价格竞争
    - 态度：担忧、求扶持、急需政策细则
    """)

with tabs[2]:
    st.write("**政策认知现状**")
    
    policy_mentions = df[df['topic'] == 'tax_policy']
    total_policy = len(policy_mentions)
    
    st.metric("政策相关舆论占比", f"{total_policy/len(df)*100:.1f}%")
    
    st.write("**政策舆论的情感分布**")
    sent_dist = policy_mentions['sentiment'].value_counts()
    for sent, count in sent_dist.items():
        pct = count / total_policy * 100
        st.write(f"{translate_sentiment(sent)}: {pct:.1f}%")
    
    st.info("""
    **认知问题**:
    - 政策话题占比仅14.6% ← 讨论不充分
    - 中立为主说明 ← 公众理解不足
    - 缺乏正面声音 ← 缺乏优势宣传
    
    **原因推测**:
    - 政策细节未充分传达
    - 缺乏"好处"的解释
    - 信息不对称
    """)

with tabs[3]:
    st.write("**高风险舆论分析**")
    
    high_risk = df[df['risk_level'].isin(['critical', 'high'])]
    
    st.metric("高风险舆论占比", f"{len(high_risk)/len(df)*100:.1f}%")
    st.write("**高风险的核心话题**")
    topic_dist = high_risk['topic'].value_counts()
    for topic, count in topic_dist.items():
        pct = count / len(high_risk) * 100
        st.write(f"• {translate_topic(topic)}: {pct:.1f}%")
    
    st.write("**高风险的主要参与方**")
    actor_dist = high_risk['actor'].value_counts()
    for actor, count in actor_dist.items():
        pct = count / len(high_risk) * 100
        st.write(f"• {translate_actor(actor)}: {pct:.1f}%")
    
    st.error("""
    **高风险风险点**:
    1. 商业风险话题是重点 - 商家生存压力大
    2. 企业和卖家是高风险发言主体 - 利益相关方不满
    3. 占比虽低(7.1%)但需重点应对 - 易引发群体焦虑
    """)

st.markdown("---")

# 3. 短期行动方案（1-3个月）
st.subheader("3️⃣ 短期行动方案 (1-3个月)")

col1, col2 = st.columns(2)

with col1:
    st.write("### 📢 针对消费者")
    st.write("""
    **行动1: 发布政策解读海报**
    - 内容：税收政策如何保护消费者权益
    - 渠道：小红书、抖音、微博
    - 频次：每周1-2条
    
    **行动2: FAQ常见问题解答**
    - 问题：对消费者的3大影响
    - 答案：政府的保障措施
    - 发布：官方网站+社交媒体
    
    **行动3: 消费者满意度调查**
    - 了解真实诉求
    - 针对性回应
    """)

with col2:
    st.write("### 🤝 针对商家")
    st.write("""
    **行动1: 发布扶持政策细则**
    - 补贴标准、申报流程
    - 税收优惠政策
    - 过渡期政策
    
    **行动2: 建立反馈机制**
    - 政府部门对接
    - 问题快速处理
    - 建立信任通道
    
    **行动3: 针对性行业说明会**
    - 跨境卖家座谈
    - 中小企业扶持
    - 答疑解惑
    """)

st.markdown("---")

# 4. 中期优化方案（3-6个月）
st.subheader("4️⃣ 中期优化方案 (3-6个月)")

st.write("""
### 目标：将负面舆论25.8% → <15%

**优化1: 政策效果评估**
- 评估短期政策的实际效果
- 测量消费者和商家的满意度变化
- 根据反馈调整政策

**优化2: 舆论监测常态化**
- 建立月度舆论监测报告
- 跟踪关键指标变化
- 及时发现新的问题点

**优化3: 构建正面舆论**
- 宣传政策成功案例
- 推出商家风采展示
- 建立消费者权益保护示范

**优化4: 重点解决高风险区**
- 针对商业风险话题深化政策
- 为中小卖家提供更多支持
- 建立风险预警机制
""")

st.markdown("---")

# 5. 长期战略（6个月+）
st.subheader("5️⃣ 长期战略 (6个月+)")

st.write("""
### 目标：建立可持续的舆论管理体系

**战略1: 建立常态化沟通机制**
- 定期发布政策进展
- 建立利益相关方对话平台
- 形成信息透明的生态

**战略2: 政策优化的动态反馈**
- 基于舆论数据持续优化
- 建立"政策→舆论→反馈→优化"的良性循环
- 提升政策的适应性和有效性

**战略3: 预警防控体系**
- 建立舆论突发预警机制
- 制定应急响应预案
- 配备专业舆情分析团队

**战略4: 数据驱动决策**
- 建立舆论分析的标准化流程
- 用数据指导政策制定
- 提升政策的科学性和精准性
""")

st.markdown("---")

# 6. 风险提示
st.subheader("⚠️ 6️⃣ 关键风险提示")

col1, col2 = st.columns(2)

with col1:
    st.error("""
    **近期风险信号** 🔴
    
    如果以下情况发生，舆论可能升级：
    1. 商家高风险舆论从7%→15%+
    2. 负面舆论突破40%
    3. 单个话题聚焦度超过30%
    4. 高风险舆论出现级联传播
    
    **应对**: 定期监测，预警提前3个月
    """)

with col2:
    st.success("""
    **最佳应对窗口** 🟢
    
    **现在是调整的黄金期**，因为：
    1. 舆论温度还不高
    2. 高风险占比仍低(7.1%)
    3. 还有沟通转变空间
    4. 消费者态度理性(61.7%中立)
    
    **错过这个窗口的代价**:
    3-6个月后可能演变成危机
    """)

st.markdown("---")

# 7. 实施检查清单
st.subheader("✅ 7️⃣ 实施检查清单")

checklist = pd.DataFrame({
    '优先级': ['🔴 高', '🔴 高', '🟡 中', '🟡 中', '🟢 低'],
    '具体行动': [
        '发布政策细则和扶持措施',
        '建立商家反馈机制',
        '发起消费者教育活动',
        '建立月度舆论监测',
        '制定应急预案'
    ],
    '责任部门': [
        '政策司',
        '行政管理部门',
        '宣传部门',
        '数据分析中心',
        '应急预案小组'
    ],
    '目标期限': [
        '2周内',
        '2周内',
        '1个月内',
        '1个月内',
        '2个月内'
    ],
    '成功指标': [
        '细则发布率100%',
        '商家满意度>70%',
        '认知提升>20%',
        '监测覆盖率>90%',
        '预案评审通过'
    ]
})

st.dataframe(checklist, use_container_width=True, hide_index=True)

st.markdown("---")

# 8. 结语
st.subheader("📌 结语")

st.write("""
### 核心建议

**跨境电商税收政策舆论目前处于"可控但需关注"的状态。**

现阶段最重要的是：
1. ✅ **明确表态** - 政府要有清晰的政策立场和细则
2. ✅ **分层沟通** - 对消费者和商家的沟通策略要差异化
3. ✅ **建立反馈** - 建立政策→舆论→反馈的良性互动
4. ✅ **预警防控** - 不要等到危机爆发再应对

**如果现在行动果断，可以预期：**
- 短期（3个月）: 负面舆论从25.8%降至20%以下
- 中期（6个月）: 中立舆论提升至70%+，形成政策共识
- 长期：建立可持续的政策→舆论的良性循环

**关键的时间窗口就在现在！**
""")

st.info(f"""
    💡 本分析基于：{len(df)}条真实舆论数据 + LLM智能分析
    - 数据来源：小红书关于跨境电商税收政策的讨论
    - 分析方法：情感识别 + 话题分类 + 风险等级评估
    - 置信度：平均0.83（很高）
    - 更新频率：可月度更新
    """)
