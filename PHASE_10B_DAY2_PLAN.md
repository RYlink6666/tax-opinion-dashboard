# Phase 10B Day 2 执行计划

**执行日期**: 2025-12-12 Day 2  
**工作范围**: P3与P7的优化  
**预期目标**: 删除30-50行代码

---

## 📋 P3 风险分析页面优化

### 当前分析
**代码行数**: 150行  
**问题**: L76-93有手动统计计算重复

### 优化方案

**问题1: 手动计算高风险舆论的多维统计 (L76-93)**

```python
# ❌ 当前代码
sent_dist = high_risk_df['sentiment'].value_counts()
for sent, count in sent_dist.items():
    pct = count / len(high_risk_df) * 100
    st.write(f"{translate_sentiment(sent)}: {count} ({pct:.1f}%)")

topic_dist = high_risk_df['topic'].value_counts().head(5)
for topic, count in topic_dist.items():
    ...

actor_dist = high_risk_df['actor'].value_counts().head(5)
for actor, count in actor_dist.items():
    ...
```

**优化方案**: 创建缓存函数聚合这些计算

```python
# ✅ 新函数 in data_loader.py
@st.cache_data
def get_high_risk_analysis(df):
    """获取高风险舆论的多维统计"""
    high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]
    return {
        'sentiment': high_risk_df['sentiment'].value_counts(),
        'topic': high_risk_df['topic'].value_counts().head(5),
        'actor': high_risk_df['actor'].value_counts().head(5)
    }

# ✅ P3中使用
high_risk_stats = get_high_risk_analysis(df)
sent_dist = high_risk_stats['sentiment']
```

**预期删除**: -8行 (3个循环简化 + 多维计算集中)

---

## 📋 P7 话题热度敏感度分析页面优化

### 当前分析
**代码行数**: 688行  
**问题**: L49-85的话题统计计算可优化

### 优化方案

**问题1: 话题的多维统计计算 (L49-87)**

```python
# ❌ 当前代码 (40行)
topic_stats = []
for topic in df['topic'].unique():
    topic_df = df[df['topic'] == topic]
    count = len(topic_df)
    
    # 热度 = 出现频次
    heat = count
    
    # 风险指数...
    high_risk_count = len(topic_df[topic_df['risk_level'].isin(['critical', 'high'])])
    risk_index = high_risk_count / count * 100 if count > 0 else 0
    
    # 负面占比...
    negative_count = len(topic_df[topic_df['sentiment'] == 'negative'])
    negative_pct = negative_count / count * 100 if count > 0 else 0
    
    # 中立占比...
    # 正面占比...
    # 敏感度计算...
    
    topic_stats.append({...})

topic_stats_df = pd.DataFrame(topic_stats).sort_values('热度', ascending=False)
```

**优化方案**: 创建缓存函数

```python
# ✅ 新函数 in data_loader.py
@st.cache_data
def get_topic_statistics(df):
    """计算所有话题的热度、敏感度和情感分布统计"""
    topic_stats = []
    for topic in df['topic'].unique():
        topic_df = df[df['topic'] == topic]
        count = len(topic_df)
        
        high_risk_count = len(topic_df[topic_df['risk_level'].isin(['critical', 'high'])])
        risk_index = high_risk_count / count * 100 if count > 0 else 0
        
        negative_count = len(topic_df[topic_df['sentiment'] == 'negative'])
        negative_pct = negative_count / count * 100 if count > 0 else 0
        
        neutral_count = len(topic_df[topic_df['sentiment'] == 'neutral'])
        neutral_pct = neutral_count / count * 100 if count > 0 else 0
        
        positive_count = len(topic_df[topic_df['sentiment'] == 'positive'])
        positive_pct = positive_count / count * 100 if count > 0 else 0
        
        sensitivity = risk_index * 0.6 + negative_pct * 0.4
        
        topic_stats.append({
            'topic': topic,
            'heat': count,
            'risk_index': risk_index,
            'negative_pct': negative_pct,
            'neutral_pct': neutral_pct,
            'positive_pct': positive_pct,
            'sensitivity': sensitivity,
        })
    
    return pd.DataFrame(topic_stats).sort_values('heat', ascending=False)

# ✅ P7中使用
topic_stats_df = get_topic_statistics(df)
```

**预期删除**: -25行 (大块计算循环提取为缓存函数)

---

**问题2: P7中L523-544的手动go.Figure创建**

```python
# ❌ 当前代码 (22行)
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
fig.update_layout(height=400, ...)
st.plotly_chart(fig, use_container_width=True)
```

**优化方案**: 考虑用库函数，但这个特殊需求（权重柱）可能需要保留。**保留不优化**

---

## 🎯 Day 2具体执行步骤

### Step 1: 创建P3的新缓存函数 (5分钟)
```python
# data_loader.py 新增函数
@st.cache_data
def get_high_risk_analysis(df):
    """高风险舆论的多维统计分析"""
    high_risk_df = df[df['risk_level'].isin(['critical', 'high'])]
    return {
        'count': len(high_risk_df),
        'sentiment': high_risk_df['sentiment'].value_counts(),
        'topic': high_risk_df['topic'].value_counts().head(5),
        'actor': high_risk_df['actor'].value_counts().head(5)
    }
```

### Step 2: 优化P3页面 (10分钟)
```python
# P3 导入新函数
from utils.data_loader import get_high_risk_analysis

# 修改 L69-93
high_risk_df = get_high_risk_subset(df)
high_risk_stats = get_high_risk_analysis(df)

# 使用stats显示统计
```

### Step 3: 创建P7的话题统计缓存函数 (10分钟)
```python
# data_loader.py 新增函数
@st.cache_data
def get_topic_statistics(df):
    """计算话题的热度、敏感度和情感分布"""
    # 40行代码提取到这里
```

### Step 4: 优化P7页面 (10分钟)
```python
# P7 导入新函数
from utils.data_loader import get_topic_statistics

# 修改 L49-87: 用缓存函数替换
topic_stats_df = get_topic_statistics(df)

# 后续代码无需改变
```

### Step 5: 测试和验证 (5分钟)
```bash
python -m py_compile streamlit_app/pages/3_风险分析.py
python -m py_compile streamlit_app/pages/7_话题热度敏感度分析.py
python -m py_compile streamlit_app/utils/data_loader.py
```

---

## 📊 Day 2目标

| 内容 | 预期 |
|------|------|
| P3优化 | -8行 |
| P7优化 | -25行 |
| 新缓存函数 | +50行 (在data_loader.py) |
| 净删减 | -33行 |
| 缓存函数增加 | 2个 |

**累计进度**: Day 1 (-56行) + Day 2 (-33行) = **-89行** (18% 完成)

---

## ✅ 完成标准

- [ ] data_loader.py新增2个缓存函数
- [ ] P3修改 L76-93 (统计显示简化)
- [ ] P7修改 L49-87 (话题统计集中化)
- [ ] 所有文件通过语法检查
- [ ] 功能完整性验证
- [ ] 生成Day 2完成报告

---

**执行时间**: ~45分钟  
**难度**: 中等  
**风险**: 低 (提取现有逻辑，无新算法)
