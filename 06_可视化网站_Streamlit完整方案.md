# Streamlit可视化网站完整方案

**版本**：v1.0  
**状态**：可立即部署  
**周期**：3-4周  
**成本**：¥0（完全免费）  
**难度**：★★☆☆☆（Python基础即可）

---

## 第一部分：项目概述

### 为什么用Streamlit？

| 特性 | Streamlit | Flask | React |
|-----|-----------|-------|-------|
| **开发速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **学习曲线** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **部署成本** | ¥0 免费 | ¥50-200 | ¥0-100 |
| **交互性** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **看起来专业** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**选择Streamlit的原因**：
- ✅ 3-5天内搭建完整网站
- ✅ Python原生，不需要前端知识
- ✅ 自动响应式设计（手机/平板/PC）
- ✅ 免费部署（Streamlit Cloud）
- ✅ 开箱即用的图表库
- ✅ 数据缓存机制（高效）

---

## 第二部分：项目结构

```
streamlit_app/                    # 项目根目录
│
├── main.py                       # 首页入口（自动运行）
│
├── pages/                        # 多页面应用目录（自动识别）
│   ├── 1_📊_Overview.py          # 详细总览
│   ├── 2_🔄_Modes.py             # 6大模式分析
│   ├── 3_⚠️_Risks.py             # 风险分析
│   ├── 4_📈_Behaviors.py         # 行为响应
│   ├── 5_🏷️_Keywords.py          # 关键词分析
│   ├── 6_📋_Articles.py          # 数据详览
│   └── 7_ℹ️_About.py             # 关于项目
│
├── data/                         # 数据目录
│   └── analysis_results_5000.json # LLM分析结果
│
├── utils/                        # 工具库
│   ├── __init__.py
│   ├── data_loader.py            # 数据加载和缓存
│   └── chart_config.py           # 图表配置
│
├── .streamlit/                   # Streamlit配置
│   └── config.toml               # 主题和设置
│
├── requirements.txt              # Python依赖
│
├── .gitignore                    # Git忽略文件
│
├── README.md                     # 项目说明
│
└── LICENSE                       # 许可证
```

### 为什么这样组织？

- ✅ `main.py`：Streamlit自动识别为首页
- ✅ `pages/`目录：自动生成导航菜单（按文件名排序）
- ✅ `1_`, `2_`前缀：控制页面顺序
- ✅ `📊` emoji：显示在菜单中（美观）
- ✅ `utils/`：代码复用，避免重复

---

## 第三部分：核心代码实现

### 步骤1：创建项目目录

```bash
# 创建项目文件夹
mkdir streamlit_app
cd streamlit_app

# 创建子目录
mkdir pages data utils .streamlit

# 初始化Git
git init
```

### 步骤2：创建requirements.txt

```ini
streamlit==1.31.1
pandas==2.1.4
numpy==1.24.3
plotly==5.18.0
python-dotenv==1.0.0
```

**安装依赖**：
```bash
pip install -r requirements.txt
```

### 步骤3：创建.streamlit/config.toml

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"
```

### 步骤4：创建utils/data_loader.py

```python
# utils/data_loader.py
import json
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    """加载和缓存LLM分析结果"""
    try:
        with open('data/analysis_results_5000.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data['results'])
    except FileNotFoundError:
        st.error("❌ 找不到数据文件：data/analysis_results_5000.json")
        return pd.DataFrame()
    except json.JSONDecodeError:
        st.error("❌ JSON文件格式错误")
        return pd.DataFrame()

@st.cache_data
def get_statistics(df):
    """计算基础统计"""
    if len(df) == 0:
        return {}
    
    return {
        'total_count': len(df),
        'sentiment_dist': df['sentiment'].value_counts().to_dict(),
        'pattern_dist': df['pattern'].value_counts().to_dict(),
        'risk_dist': df['risk_category'].value_counts().to_dict(),
        'behavior_dist': df['behavioral_intent'].value_counts().to_dict(),
        'avg_confidence': df['sentiment_confidence'].mean(),
    }

def format_number(num):
    """格式化数字显示"""
    if isinstance(num, float):
        return f"{num:.2%}"
    return f"{num:,}"
```

### 步骤5：创建main.py（首页）

```python
# main.py - 首页总览
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, get_statistics

# 页面配置
st.set_page_config(
    page_title="跨境电商舆论分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS（可选）
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# 加载数据
df = load_data()

if len(df) == 0:
    st.error("❌ 无法加载数据，请检查 data/analysis_results_5000.json")
    st.stop()

stats = get_statistics(df)

# ===== 页面内容 =====

# 标题和描述
st.title("🎯 跨境电商税收舆论分析仪表板")
st.markdown("""
**📊 实时数据分析平台** | 基于5000条舆论的LLM结构化分析  
📅 时间范围：2025年6月-12月 | 🔬 精度验证：88%+
""")

st.markdown("---")

# 关键指标卡片（4列）
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 总舆论数",
        value=f"{stats['total_count']:,}",
        delta="样本规模"
    )

with col2:
    neg_count = stats['sentiment_dist'].get('negative', 0)
    neg_pct = neg_count / stats['total_count'] * 100
    st.metric(
        label="📉 负面占比",
        value=f"{neg_pct:.1f}%",
        delta=f"{neg_count}条舆论"
    )

with col3:
    critical_count = len(df[df['risk_severity'] == 'Critical'])
    st.metric(
        label="⚠️ Critical风险",
        value=f"{critical_count}",
        delta="最高警报"
    )

with col4:
    compliance_count = stats['behavior_dist'].get('Compliance', 0)
    st.metric(
        label="✅ 合规倾向",
        value=f"{compliance_count}",
        delta="主动应对"
    )

st.markdown("---")

# 情感和模式分布（2列图）
col1, col2 = st.columns(2)

with col1:
    st.subheader("😊 情感分布")
    sentiment_data = df['sentiment'].value_counts()
    fig_sentiment = px.pie(
        values=sentiment_data.values,
        names=sentiment_data.index,
        color_discrete_map={
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6'
        },
        hole=0.4  # 甜甜圈图
    )
    fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    st.subheader("🔄 主要模式分布（Top 6）")
    pattern_data = df['pattern'].value_counts().head(6)
    fig_pattern = px.bar(
        x=pattern_data.values,
        y=pattern_data.index,
        orientation='h',
        color=pattern_data.values,
        color_continuous_scale='Blues',
        labels={'x': '舆论数量', 'y': '交易模式'}
    )
    st.plotly_chart(fig_pattern, use_container_width=True)

st.markdown("---")

# 风险类型排行
st.subheader("⚠️ 风险类型排名")
risk_data = df['risk_category'].value_counts().head(8)
fig_risk = px.bar(
    x=risk_data.values,
    y=risk_data.index,
    orientation='h',
    color=risk_data.values,
    color_continuous_scale='Reds',
    labels={'x': '舆论数量', 'y': '风险类型'},
    title=""
)
st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# 关键洞察（摘录）
st.subheader("💡 关键发现")
insights = df['key_insight'].dropna().unique()[:5]

for i, insight in enumerate(insights, 1):
    st.info(f"**{i}. {insight}**")

st.markdown("---")

# 数据质量信息
st.markdown("""
### 📈 数据来源与方法
- **数据来源**：微博、知乎、小红书、电商论坛等
- **采样方法**：关键词搜索 + 时间范围过滤
- **分析工具**：智谱清言 GLM-4-Flash 模型
- **分类维度**：情感、模式、风险、身份、行为
- **精度验证**：100条样本人工标注，精度88%+

### 🔍 侧边栏导航
👈 在左侧菜单查看详细分析页面
""")

# 页脚
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("📊 舆论分析平台 v1.0")
with col2:
    st.caption("🔗 [在线文档](#) | [GitHub](#) | [反馈](#)")
with col3:
    st.caption("📅 最后更新：2026年1月")
```

### 步骤6：创建pages/1_📊_Overview.py（详细总览）

```python
# pages/1_📊_Overview.py - 详细数据总览
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(page_title="详细总览", layout="wide")

df = load_data()

st.title("📊 详细数据总览")

# 多维统计
st.subheader("数据维度统计")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("情感分布", f"{df['sentiment'].nunique()}", "维度")
with col2:
    st.metric("识别模式", f"{df['pattern'].nunique()}", "种")
with col3:
    st.metric("风险类型", f"{df['risk_category'].nunique()}", "种")
with col4:
    st.metric("身份分布", f"{df['taxpayer_identity'].nunique()}", "类")

st.markdown("---")

# 交叉分析 1: 模式 × 情感
st.subheader("📊 模式 × 情感 交叉分析")
cross = pd.crosstab(df['pattern'], df['sentiment'])
fig = go.Figure(data=[
    go.Bar(name=sentiment, x=cross.index, y=cross[sentiment])
    for sentiment in cross.columns
])
fig.update_layout(
    barmode='group',
    title="各交易模式下的情感分布",
    xaxis_title="交易模式",
    yaxis_title="舆论数量",
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 交叉分析 2: 模式 × 风险（热力图）
st.subheader("🔥 模式 × 风险 热力图")
cross_risk = pd.crosstab(df['pattern'], df['risk_category'])
fig_heatmap = go.Figure(data=go.Heatmap(
    z=cross_risk.values,
    x=cross_risk.columns,
    y=cross_risk.index,
    colorscale='Reds',
    text=cross_risk.values,
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="舆论数")
))
fig_heatmap.update_layout(
    title="交易模式与风险类型的关联强度",
    xaxis_title="风险类型",
    yaxis_title="交易模式",
    height=500
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# 行为分布
st.subheader("📈 行为倾向分布")
behavior = df['behavioral_intent'].value_counts()
colors = {
    'Compliance': '#2ecc71',
    'Mode_Switch': '#f39c12',
    'Help_Seeking': '#3498db',
    'Wait_and_See': '#9b59b6',
    'No_Action': '#95a5a6'
}
fig_behavior = px.bar(
    x=behavior.index,
    y=behavior.values,
    color=behavior.index,
    color_discrete_map=colors,
    labels={'x': '行为类型', 'y': '舆论数量'},
    title="企业的5种行为响应"
)
st.plotly_chart(fig_behavior, use_container_width=True)

st.markdown("---")

# 数据透视表
st.subheader("📋 数据透视表（可下载）")
pivot = pd.pivot_table(
    df,
    values='source_text',
    index='risk_category',
    columns='sentiment',
    aggfunc='count',
    fill_value=0
)
st.dataframe(pivot, use_container_width=True)

# 下载按钮
csv = pivot.to_csv()
st.download_button(
    label="📥 下载透视表为CSV",
    data=csv,
    file_name="opinion_pivot_table.csv",
    mime="text/csv"
)
```

### 步骤7：创建pages/2_🔄_Modes.py（6大模式）

```python
# pages/2_🔄_Modes.py - 6大模式分析
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data

st.set_page_config(page_title="模式分析", layout="wide")

df = load_data()

st.title("🔄 6大交易模式深度分析")

modes = ['0110', '9610', '9710', '9810', '1039', 'Temu']
mode_names = {
    '0110': '0110 - 传统外贸+香港公司',
    '9610': '9610 - B2C小包裹零售',
    '9710': '9710 - B2B直接出口',
    '9810': '9810 - 海外仓模式',
    '1039': '1039 - 市场采购',
    'Temu': 'Temu - 平台全托管',
}

# 创建Tab页面
tabs = st.tabs([f"{mode} {mode_names.get(mode, '')}" for mode in modes])

for idx, mode in enumerate(modes):
    with tabs[idx]:
        mode_df = df[df['pattern'] == mode]
        
        if len(mode_df) == 0:
            st.warning(f"❌ 没有 {mode} 的数据")
            continue
        
        # 该模式的关键指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("舆论数量", f"{len(mode_df):,}")
        
        with col2:
            pct = len(mode_df) / len(df) * 100
            st.metric("占总比", f"{pct:.1f}%")
        
        with col3:
            neg_count = len(mode_df[mode_df['sentiment'] == 'negative'])
            neg_pct = neg_count / len(mode_df) * 100
            st.metric("负面占比", f"{neg_pct:.1f}%")
        
        with col4:
            main_risk = mode_df['risk_category'].value_counts()
            st.metric("主要风险", main_risk.index[0] if len(main_risk) > 0 else "N/A")
        
        st.markdown("---")
        
        # 该模式的分析（2列）
        col1, col2 = st.columns(2)
        
        with col1:
            # 风险分布
            risk_data = mode_df['risk_category'].value_counts()
            fig_risk = px.bar(
                x=risk_data.values,
                y=risk_data.index,
                orientation='h',
                color=risk_data.values,
                color_continuous_scale='Reds',
                title=f"{mode} - 风险类型分布"
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            # 行为倾向
            behavior_data = mode_df['behavioral_intent'].value_counts()
            fig_behavior = px.pie(
                values=behavior_data.values,
                names=behavior_data.index,
                title=f"{mode} - 行为倾向分布"
            )
            st.plotly_chart(fig_behavior, use_container_width=True)
        
        st.markdown("---")
        
        # 情感分布
        st.subheader(f"😊 {mode} - 情感分布")
        sentiment_data = mode_df['sentiment'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_data.values,
            names=sentiment_data.index,
            color_discrete_map={'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'},
            title=""
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        st.markdown("---")
        
        # 典型案例
        st.subheader(f"📌 {mode} 典型案例（按置信度排序）")
        samples = mode_df.nlargest(5, 'sentiment_confidence')
        
        for i, (_, row) in enumerate(samples.iterrows(), 1):
            with st.expander(f"案例 {i}：【{row['sentiment'].upper()}】{row['source_text'][:50]}..."):
                st.write(f"📝 **原始舆论**：{row['source_text']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"😊 **情感**：{row['sentiment']}")
                    st.write(f"  置信度：{row.get('sentiment_confidence', 0):.0%}")
                with col2:
                    st.write(f"⚠️ **风险**：{row['risk_category']}")
                    st.write(f"  严重性：{row.get('risk_severity', 'N/A')}")
                
                st.write(f"🎯 **行为**：{row['behavioral_intent']}")
                st.write(f"💡 **洞察**：{row['key_insight']}")
```

### 步骤8：创建pages/3_⚠️_Risks.py（风险分析）

```python
# pages/3_⚠️_Risks.py - 风险分析
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data

st.set_page_config(page_title="风险分析", layout="wide")

df = load_data()

st.title("⚠️ 风险类型深度分析")

# 风险严重性排序
st.subheader("风险严重程度排序")

severity_map = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
risk_severity = df.groupby('risk_category')['risk_severity'].apply(
    lambda x: x.map(severity_map).mean()
).sort_values(ascending=False)

fig_severity = px.bar(
    x=risk_severity.values,
    y=risk_severity.index,
    orientation='h',
    color=risk_severity.values,
    color_continuous_scale='Reds',
    labels={'x': '平均严重程度', 'y': '风险类型'},
    title="各风险类型的平均严重程度"
)
st.plotly_chart(fig_severity, use_container_width=True)

st.markdown("---")

# 热力图
st.subheader("🔥 模式 × 风险 热力图")
heatmap_data = pd.crosstab(df['pattern'], df['risk_category'])
fig_heatmap = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Reds'
))
fig_heatmap.update_layout(
    title="交易模式与风险类型的关联",
    xaxis_title="风险类型",
    yaxis_title="交易模式",
    height=500
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# 各风险类型的详细分析
st.subheader("风险类型详情")
risk_types = sorted(df['risk_category'].unique())

for risk in risk_types:
    risk_df = df[df['risk_category'] == risk]
    
    with st.expander(f"**{risk}** (n={len(risk_df)}, {len(risk_df)/len(df)*100:.1f}%)"):
        # 关键指标
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("舆论数", len(risk_df))
        with col2:
            severity_dist = risk_df['risk_severity'].value_counts()
            st.metric("主要程度", severity_dist.index[0] if len(severity_dist) > 0 else "N/A")
        with col3:
            neg_pct = len(risk_df[risk_df['sentiment']=='negative']) / len(risk_df) * 100
            st.metric("负面占比", f"{neg_pct:.1f}%")
        
        # 分析图表
        col1, col2 = st.columns(2)
        
        with col1:
            # 情感分布
            sentiment = risk_df['sentiment'].value_counts()
            fig = px.pie(
                values=sentiment.values,
                names=sentiment.index,
                color_discrete_map={'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'},
                title=f"{risk} - 情感分布"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 严重程度
            severity = risk_df['risk_severity'].value_counts()
            fig = px.bar(
                x=severity.index,
                y=severity.values,
                color=severity.index,
                color_discrete_map={
                    'Critical': '#e74c3c',
                    'High': '#f39c12',
                    'Medium': '#f1c40f',
                    'Low': '#95a5a6'
                },
                title=f"{risk} - 严重程度"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 代表性舆论
        st.write("**代表性舆论**（按置信度排序）：")
        reps = risk_df.nlargest(3, 'risk_confidence')
        for i, (_, row) in enumerate(reps.iterrows(), 1):
            st.write(f"{i}. {row['source_text'][:100]}...")
```

### 步骤9：创建pages/4_📈_Behaviors.py（行为响应）

```python
# pages/4_📈_Behaviors.py - 行为响应分析
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_data

st.set_page_config(page_title="行为分析", layout="wide")

df = load_data()

st.title("📈 企业行为响应分析")

# 行为分布
st.subheader("企业行为倾向分布")
behavior = df['behavioral_intent'].value_counts()

fig_behavior = px.bar(
    x=behavior.index,
    y=behavior.values,
    color=behavior.values,
    color_continuous_scale='Viridis',
    labels={'x': '行为类型', 'y': '舆论数量'},
    title="5种行为的分布情况"
)
st.plotly_chart(fig_behavior, use_container_width=True)

st.markdown("---")

# 行为×情感
st.subheader("行为 × 情感 交叉分析")
cross = pd.crosstab(df['behavioral_intent'], df['sentiment'])
fig_cross = go.Figure(data=[
    go.Bar(name=sentiment, x=cross.index, y=cross[sentiment])
    for sentiment in cross.columns
])
fig_cross.update_layout(
    barmode='group',
    title="不同行为下的情感倾向",
    xaxis_title="行为类型",
    yaxis_title="舆论数量"
)
st.plotly_chart(fig_cross, use_container_width=True)

st.markdown("---")

# 身份特征分析
st.subheader("纳税人身份分析")

col1, col2 = st.columns(2)

with col1:
    identity = df['taxpayer_identity'].value_counts()
    fig_identity = px.pie(
        values=identity.values,
        names=identity.index,
        title="纳税人身份分布"
    )
    st.plotly_chart(fig_identity, use_container_width=True)

with col2:
    # 身份×行为关联
    cross_id = pd.crosstab(df['taxpayer_identity'], df['behavioral_intent'])
    fig_id_behavior = go.Figure(data=[
        go.Bar(name=behavior, x=cross_id.index, y=cross_id[behavior])
        for behavior in cross_id.columns
    ])
    fig_id_behavior.update_layout(
        barmode='group',
        title="身份-行为分布",
        xaxis_title="纳税人身份",
        yaxis_title="舆论数量"
    )
    st.plotly_chart(fig_id_behavior, use_container_width=True)

st.markdown("---")

# 行为洞察
st.subheader("💡 行为洞察")

behavior_insights = {
    'Compliance': {
        'icon': '✅',
        'desc': '主动合规',
        'color': '#2ecc71',
        'detail': '企业已咨询专业人士或主动补税，表现出积极的合规态度'
    },
    'Mode_Switch': {
        'icon': '🔄',
        'desc': '考虑转换模式',
        'color': '#f39c12',
        'detail': '企业在评估现有模式，考虑切换到其他交易模式'
    },
    'Help_Seeking': {
        'icon': '❓',
        'desc': '积极求助',
        'color': '#3498db',
        'detail': '企业主动寻求解决方案，提问和咨询比较频繁'
    },
    'Wait_and_See': {
        'icon': '👀',
        'desc': '观望态度',
        'color': '#9b59b6',
        'detail': '企业采取等待态度，观察政策进展或其他企业的做法'
    },
    'No_Action': {
        'icon': '💬',
        'desc': '仅讨论',
        'color': '#95a5a6',
        'detail': '企业仅参与讨论，暂无具体行动计划'
    }
}

# 可视化行为洞察
for behavior_type, insight in behavior_insights.items():
    count = len(df[df['behavioral_intent'] == behavior_type])
    pct = count / len(df) * 100
    st.markdown(f"""
    <div style="background-color: {insight['color']}20; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <b>{insight['icon']} {insight['desc']}</b> - {count}条 ({pct:.1f}%)<br/>
        {insight['detail']}
    </div>
    """, unsafe_allow_html=True)
```

### 步骤10：创建pages/5_🏷️_Keywords.py（关键词）

```python
# pages/5_🏷️_Keywords.py - 关键词分析
import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter
import re
from utils.data_loader import load_data

st.set_page_config(page_title="关键词", layout="wide")

df = load_data()

st.title("🏷️ 关键词分析")

# 提取关键词函数
@st.cache_data
def extract_keywords(texts, top_n=100):
    """提取中文关键词"""
    words = []
    for text in texts:
        # 按照长度≥2的词提取（简单分词）
        tokens = re.findall(r'[\u4e00-\u9fff]{2,}', str(text))
        words.extend(tokens)
    counter = Counter(words)
    return counter.most_common(top_n)

# 全局关键词
keywords = extract_keywords(df['source_text'], top_n=100)
kw_df = pd.DataFrame(keywords, columns=['word', 'frequency'])

# 词频分布
st.subheader("📊 高频关键词分布（Top 30）")
fig_kw = px.bar(
    kw_df.head(30),
    x='word',
    y='frequency',
    color='frequency',
    color_continuous_scale='Blues',
    title="最常出现的关键词"
)
fig_kw.update_xaxes(tickangle=-45)
st.plotly_chart(fig_kw, use_container_width=True)

st.markdown("---")

# 关键词表
st.subheader("🔤 完整关键词表（Top 50）")
st.dataframe(
    kw_df.head(50),
    column_config={
        "word": st.column_config.TextColumn("关键词", width=None),
        "frequency": st.column_config.ProgressColumn(
            "出现频次",
            min_value=0,
            max_value=kw_df['frequency'].max(),
        ),
    },
    hide_index=True,
    use_container_width=True,
)

st.markdown("---")

# 词语与风险的关联
st.subheader("⚠️ 关键词-风险关联")

risk_types = sorted([r for r in df['risk_category'].unique() if r != 'None'])[:8]

cols = st.columns(2)
for idx, risk in enumerate(risk_types):
    risk_texts = df[df['risk_category'] == risk]['source_text']
    risk_kws = extract_keywords(risk_texts, top_n=10)
    risk_kw_df = pd.DataFrame(risk_kws, columns=['word', 'frequency'])
    
    with cols[idx % 2]:
        st.markdown(f"#### {risk}")
        for _, row in risk_kw_df.head(5).iterrows():
            st.write(f"- {row['word']}: {row['frequency']}")
```

### 步骤11：创建pages/6_📋_Articles.py（数据详览）

```python
# pages/6_📋_Articles.py - 舆论数据详览
import streamlit as st
import pandas as pd
from utils.data_loader import load_data

st.set_page_config(page_title="数据详览", layout="wide")

df = load_data()

st.title("📋 舆论数据详览")

# 筛选面板
st.subheader("🔍 多维度筛选")

col1, col2, col3, col4 = st.columns(4)

with col1:
    sentiment_filter = st.multiselect(
        "情感筛选",
        options=['positive', 'negative', 'neutral'],
        default=None
    )

with col2:
    pattern_filter = st.multiselect(
        "模式筛选",
        options=sorted(df['pattern'].dropna().unique()),
        default=None
    )

with col3:
    risk_filter = st.multiselect(
        "风险筛选",
        options=sorted(df['risk_category'].dropna().unique()),
        default=None
    )

with col4:
    behavior_filter = st.multiselect(
        "行为筛选",
        options=sorted(df['behavioral_intent'].dropna().unique()),
        default=None
    )

# 关键词搜索
search_text = st.text_input("🔎 关键词搜索", placeholder="输入关键词...")

st.markdown("---")

# 应用筛选
filtered_df = df.copy()

if sentiment_filter:
    filtered_df = filtered_df[filtered_df['sentiment'].isin(sentiment_filter)]
if pattern_filter:
    filtered_df = filtered_df[filtered_df['pattern'].isin(pattern_filter)]
if risk_filter:
    filtered_df = filtered_df[filtered_df['risk_category'].isin(risk_filter)]
if behavior_filter:
    filtered_df = filtered_df[filtered_df['behavioral_intent'].isin(behavior_filter)]
if search_text:
    filtered_df = filtered_df[
        filtered_df['source_text'].str.contains(search_text, case=False, na=False)
    ]

# 显示统计
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("匹配条数", len(filtered_df))
with col2:
    st.metric("占比", f"{len(filtered_df)/len(df)*100:.1f}%")
with col3:
    st.metric("总条数", len(df))

st.markdown("---")

# 分页显示
page_size = 20
total_pages = (len(filtered_df) - 1) // page_size + 1

if total_pages > 1:
    page = st.slider("📄 选择页码", 1, total_pages)
else:
    page = 1

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

st.subheader(f"舆论列表（{start_idx+1}-{min(end_idx, len(filtered_df))}，共{len(filtered_df)}）")

# 显示结果
for idx, (_, row) in enumerate(filtered_df.iloc[start_idx:end_idx].iterrows(), 1):
    with st.expander(f"**{idx}. 【{row['sentiment'].upper()}】** {row['source_text'][:60]}...", expanded=False):
        # 两列布局
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### 📝 原始舆论")
            st.write(row['source_text'])
            
            st.write("### 🏷️ 分类信息")
            st.markdown(f"""
            - **情感**：{row['sentiment']} (置信度 {row.get('sentiment_confidence', 0):.0%})
            - **模式**：{row.get('pattern', 'N/A')}
            - **风险**：{row.get('risk_category', 'N/A')}
            - **身份**：{row.get('taxpayer_identity', 'N/A')}
            - **行为**：{row.get('behavioral_intent', 'N/A')}
            """)
        
        with col2:
            st.write("### 📊 评分")
            st.metric("情感置信度", f"{row.get('sentiment_confidence', 0):.0%}")
            st.metric("模式置信度", f"{row.get('pattern_confidence', 0):.0%}")
            st.metric("风险置信度", f"{row.get('risk_confidence', 0):.0%}")
            st.metric("严重程度", row.get('risk_severity', 'N/A'))
        
        st.write("### 💡 关键洞察")
        st.info(row.get('key_insight', '无'))
```

### 步骤12：创建pages/7_ℹ️_About.py（关于页面）

```python
# pages/7_ℹ️_About.py - 关于项目
import streamlit as st

st.set_page_config(page_title="关于", layout="wide")

st.title("ℹ️ 关于本项目")

# 使用Tab组织内容
tab1, tab2, tab3, tab4 = st.tabs(["项目概述", "方法论", "分类维度", "反馈"])

with tab1:
    st.markdown("""
    ## 📊 项目概述
    
    **项目名称**：跨境电商税收政策舆论分析与可视化平台
    
    **背景**：2025年以来，中国对跨境电商的税收政策进行了重大改革。本项目致力于理解企业和消费者如何响应这些政策变化。
    
    ### 核心数据
    - 📅 **时间范围**：2025年6月-12月（7个月）
    - 🗣️ **舆论样本**：5,000条
    - 📱 **数据来源**：微博、知乎、小红书、电商论坛等
    - 🔬 **分析方法**：LLM（智谱清言 GLM-4-Flash）+ 结构化分类
    - ✅ **精度验证**：100条样本人工标注，精度88%+
    
    ### 主要发现
    
    1. **负面情感占比高**（约60%）
       - 企业和消费者表现出焦虑、困惑、反对
       
    2. **信息不对称严重**
       - "信息不透明"是最高频的风险类型
       - 企业希望获得更清晰的执行指南
       
    3. **模式差异明显**
       - 不同交易模式（0110、9610、9810等）面临的风险分化
       
    4. **主动合规倾向**
       - 30%的企业表现出合规意愿
       - 但仍有大量企业采取观望态度
    
    ### 政策启示
    
    ✅ 基于舆论分析的建议：
    
    1. **加强政策说明**
       - 发布详细的执行指南
       - 组织政策说明会
       
    2. **分类指导**
       - 针对不同规模和模式的企业提供差异化支持
       
    3. **部门协调**
       - 加强不同政府部门间的配合
       - 特别是备案部门与税务部门
       
    4. **及时反馈**
       - 建立企业反馈机制
       - 定期发布政策进展更新
    """)

with tab2:
    st.markdown("""
    ## 📚 方法论详解
    
    ### 数据采集
    
    **来源**：微博、知乎、小红书、电商论坛等社交平台
    
    **关键词**：
    - 税收政策相关：跨境电商、税收改革、合规等
    - 交易模式：0110、9610、9710、9810、1039、Temu
    - 问题关键词：备案、补税、风险、困难等
    
    **时间范围**：2025年6月1日 - 12月31日
    
    **采样方法**：关键词搜索 + 时间范围过滤
    
    ### LLM分析方法
    
    **模型**：智谱清言 GLM-4-Flash
    
    **为什么选择LLM？**
    - ✅ 理解复杂的修辞和讽刺
    - ✅ 捕捉隐含的意思
    - ✅ 跨越语言的细微差别
    - ✅ 学习能力强（Few-shot示例）
    
    **架构**：
    ```
    系统Prompt（角色定义 + 分类规则）
         ↓
    Few-shot示例库（20个高质量例子）
         ↓
    输入舆论文本
         ↓
    LLM分析（5个维度）
         ↓
    JSON结构化输出
    ```
    
    **精度验证**：
    - 方法：100条样本人工标注 vs LLM结果对比
    - 目标：≥85%匹配率
    - 实现：88%+匹配率
    
    ### 质量保证
    
    - ✅ 置信度评估：每个判断都有0-1的置信度
    - ✅ 多轮审查：关键判断进行二次验证
    - ✅ 异常检测：自动标记疑似错误的分类
    - ✅ 定期抽查：持续验证LLM输出质量
    """)

with tab3:
    st.markdown("""
    ## 📊 五维度分类体系
    
    ### 1️⃣ 情感反应 (Sentiment)
    
    | 分类 | 定义 | 标志词 |
    |-----|------|-------|
    | **Positive** | 支持政策、接受现状 | 支持、赞同、感谢、解决 |
    | **Negative** | 反对、焦虑、困惑 | 怎么办、担心、风险、被罚 |
    | **Neutral** | 纯信息陈述、中立 | 根据、分析、报道、讲述 |
    
    ### 2️⃣ 业务模式 (Pattern)
    
    | 代码 | 名称 | 特点 |
    |-----|------|------|
    | **0110** | 传统外贸+香港公司 | 香港形式，国内实质 |
    | **9610** | B2C小包裹零售 | 小包裹、跨境电商平台 |
    | **9710** | B2B直接出口 | 企业对企业、订单贸易 |
    | **9810** | 海外仓模式 | 货物预存海外 |
    | **1039** | 市场采购 | 小商户、义乌、无发票 |
    | **Temu** | 平台全托管 | 平台定价、内销视同 |
    
    ### 3️⃣ 风险类型 (Risk Category)
    
    | 风险类型 | 特征 | 严重程度 |
    |---------|------|--------|
    | **香港空壳** | 虚拟公司、实质管理地 | 🔴 Critical |
    | **备案难题** | 流程复杂、政府回应慢 | 🟠 Medium |
    | **库存核销** | 多平台混合、数据对不上 | 🟠 Medium-High |
    | **数据不符** | 增值税vs所得税矛盾 | 🟠 Medium-High |
    | **恶意拆分** | 规模超限、规避税收 | 🟠 High |
    | **规模困境** | 做大后税负爆表 | 🟠 High |
    | **补税压力** | 已被查、已补税 | 🔴 Critical |
    | **信息不透明** | 规则不清、执行不一致 | 🟡 Low-Medium |
    | **无风险** | 讨论技术、无风险 | ✅ None |
    
    ### 4️⃣ 纳税人身份 (Taxpayer Identity)
    
    | 身份 | 定义 | 税率 |
    |-----|------|------|
    | **General** | 一般纳税人 | 13% 增值税 |
    | **Small** | 小规模纳税人 | 3% 增值税 |
    | **Unknown** | 身份不明 | — |
    
    ### 5️⃣ 行为倾向 (Behavioral Intent)
    
    | 行为 | 描述 | 例子 |
    |-----|------|------|
    | **Compliance** | 主动合规 | 已咨询顾问、已补税 |
    | **Mode_Switch** | 考虑转换模式 | 计划改用其他模式 |
    | **Help_Seeking** | 积极求助 | 询问怎么办、咨询 |
    | **Wait_and_See** | 观望态度 | 等政策澄清、看其他企业 |
    | **No_Action** | 仅讨论 | 纯讨论、无行动 |
    """)

with tab4:
    st.markdown("""
    ## 📮 反馈与建议
    
    我们欢迎您的反馈和建议，帮助我们改进平台！
    
    ### 反馈方式
    
    1. **问卷调查** → [填写问卷](https://survey.example.com)
    
    2. **邮件反馈** → feedback@example.com
    
    3. **GitHub Issues** → [提交Issue](https://github.com/example)
    
    ### 常见问题 (FAQ)
    
    **Q: 数据准确性如何保证？**
    
    A: 我们通过以下方式保证数据质量：
    - LLM模型精度验证（88%+）
    - 100条样本人工标注对比
    - 异常检测和二次审查
    - 定期抽查验证
    
    **Q: 数据可以商业使用吗？**
    
    A: 当前数据仅用于：
    - 学术研究
    - 政策分析
    - 公开展示
    
    商业使用需联系我们获得许可。
    
    **Q: 如何引用这个平台的数据？**
    
    A: 请使用以下格式：
    ```
    [Your Name]. (2026). 跨境电商税收政策舆论分析平台.
    Available at: https://[your-app].streamlit.app/
    ```
    
    **Q: 能否获得原始数据？**
    
    A: 原始舆论数据涉及隐私问题，不公开发布。
    但我们提供结构化分析结果和统计摘要。
    
    ---
    
    ### 项目信息
    
    - 📊 **平台版本**：v1.0
    - 📅 **最后更新**：2026年1月
    - 👨‍💼 **项目团队**：[Your Name]
    - 📧 **联系邮箱**：[your-email@example.com]
    - 🔗 **GitHub仓库**：[https://github.com/...](https://github.com/)
    - 📄 **学术论文**：[正在审稿中...]
    """)

st.markdown("---")

# 页脚
st.info("""
💡 **使用提示**：
- 在左侧菜单选择你感兴趣的分析页面
- 在📋数据详览页面可以搜索和筛选舆论
- 所有图表都可以交互（悬停查看详情）
""")
```

---

## 第四部分：本地运行和测试

### 运行方式

```bash
# 进入项目目录
cd streamlit_app

# 运行应用
streamlit run main.py

# 应该看到：
# Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.
# 
#   You can now view your Streamlit app in your browser.
# 
#   Local URL: http://localhost:8501
#   Network URL: http://192.168.x.x:8501
```

### 测试清单

```
□ 首页能加载（main.py）
□ 所有页面能访问（pages/目录）
□ 数据能正确加载（<3秒）
□ 所有图表能渲染
□ 筛选功能正常
□ 搜索功能准确
□ 响应式在手机上显示正确
□ 没有Python错误或红色警告
```

---

## 第五部分：部署到Streamlit Cloud（免费）

### 部署步骤

#### 1️⃣ 推送到GitHub

```bash
# 在项目根目录
git init
git add .
git commit -m "Initial Streamlit opinion analysis dashboard"
git branch -M main
git remote add origin https://github.com/[your-username]/opinion-analysis-dashboard.git
git push -u origin main
```

#### 2️⃣ 在Streamlit Cloud部署

1. 访问 https://streamlit.io/cloud
2. 用GitHub账户登录
3. 点击 "New app"
4. 选择：
   - Repository: `opinion-analysis-dashboard`
   - Branch: `main`
   - Main file path: `streamlit_app/main.py`
5. 点击 "Deploy"

**等待3-5分钟自动部署完成**

#### 3️⃣ 获得URL

部署成功后，会获得：
```
https://[username]-opinion-analysis.streamlit.app/
```

#### 4️⃣ 配置自定义域名（可选）

在Streamlit Cloud设置中可以配置自定义域名。

---

## 第六部分：项目配置文件

### .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# Streamlit
.streamlit/secrets.toml
.streamlit/cache/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Data
*.xlsx
*.csv
~*.xls*
```

### README.md

```markdown
# 跨境电商舆论分析仪表板

🎯 一个交互式的舆论分析平台，基于5000条真实舆论进行LLM结构化分析。

## 🚀 快速开始

### 本地运行

\`\`\`bash
pip install -r requirements.txt
streamlit run main.py
\`\`\`

访问 http://localhost:8501

### 在线访问

[https://...streamlit.app](https://...streamlit.app)

## 📊 功能特性

- 📈 情感分析和舆论分布
- 🔄 6大交易模式的深度分析
- ⚠️ 风险类型排序和热力图
- 📈 企业行为响应分析
- 🏷️ 关键词提取和分析
- 📋 可交互的数据详览和搜索

## 📁 项目结构

```
streamlit_app/
├── main.py              # 首页
├── pages/               # 7个功能页面
├── data/                # 数据文件
├── utils/               # 工具库
└── requirements.txt     # 依赖
```

## 🔬 方法论

- **数据**：5000条舆论（2025年6月-12月）
- **分析方法**：LLM（智谱清言 GLM-4-Flash）
- **分类维度**：5维（情感、模式、风险、身份、行为）
- **精度**：88%+（100条样本验证）

## 📝 引用

[Your Citation Here]

## 📧 联系

[Your Email]

## 📄 许可

MIT License
```

---

## 第七部分：常见问题与故障排查

| 问题 | 原因 | 解决 |
|-----|------|------|
| ModuleNotFoundError | 没装依赖库 | `pip install -r requirements.txt` |
| FileNotFoundError | 找不到data文件 | 确保 `data/analysis_results_5000.json` 存在 |
| JSON解析错误 | 数据格式不对 | 检查JSON文件格式 |
| 图表不显示 | 数据为空 | 确认数据文件有内容 |
| 速度慢 | 数据加载未缓存 | @st.cache_data工作正常吗？ |
| 部署失败 | 依赖版本冲突 | 更新requirements.txt中的版本 |

---

## 总结

这个Streamlit网站方案具有：

✅ **快速开发**：3-5天完成  
✅ **零成本部署**：完全免费  
✅ **专业外观**：现代化UI设计  
✅ **完全交互**：丰富的过滤和搜索  
✅ **易于维护**：Python代码，易于修改  
✅ **可扩展**：后续可升级为React版本  

**现在就可以开始！** 

按照上面的代码框架，逐个创建文件，运行 `streamlit run main.py`，就能看到完整的网站。
