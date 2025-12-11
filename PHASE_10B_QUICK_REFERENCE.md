# Phase 10B 快速参考指南

## 新增缓存函数速查表

### 数据统计类

| 函数 | 位置 | 用途 | 返回 | 用过页面 |
|------|------|------|------|---------|
| `get_all_distributions()` | data_loader.py L216-237 | 所有主要分布 | dict(sentiment, risk_level, topic, actor, pattern) | P1-P9 |
| `get_quick_stats()` | data_loader.py L448-489 | 快速统计指标 | dict(negative_count/pct, high_risk_count/pct, avg_confidence, total_count) | P2 |
| `get_topic_statistics()` | data_loader.py L387-443 | 话题热敏感度 | DataFrame(heat, risk_index, negative_pct, sensitivity) | P7 |

### 高风险分析类

| 函数 | 位置 | 用途 | 返回 | 用过页面 |
|------|------|------|------|---------|
| `get_high_risk_subset()` | data_loader.py L256-267 | 高风险子集 | DataFrame(filtered) | P3, P5, P9 |
| `get_high_risk_analysis()` | data_loader.py L361-383 | 高风险多维分析 | dict(count, sentiment, topic, actor) | P3 |
| `get_risk_segment_analysis()` | data_loader.py L610-633 | 高风险段群分析 | dict(total, pct, topic_dist, actor_dist) | P6 |

### 参与方分析类

| 函数 | 位置 | 用途 | 返回 | 用过页面 |
|------|------|------|------|---------|
| `get_actors_split_statistics()` | data_loader.py L284-297 | 拆分演员统计 | Series(actor_dist) | P5, P9 |
| `get_actors_sentiment_cross()` | data_loader.py L301-317 | 演员×情感交叉 | DataFrame(crosstab) | P5 |
| `get_actors_risk_cross()` | data_loader.py L321-337 | 演员×风险交叉 | DataFrame(crosstab) | P5 |
| `get_actors_topic_cross()` | data_loader.py L341-357 | 演员×话题交叉 | DataFrame(crosstab) | P5 |
| `get_actor_segment_analysis()` | data_loader.py L552-589 | 参与方段群分析 | dict(count, sentiment_dist, risk_dist, topic_dist) | **P6** |
| `get_actor_statistics_summary()` | data_loader.py L512-551 | 参与方汇总表 | DataFrame(参与方, 意见数, 占比, 负面%, 高风险%) | **P9 Tab6** |

### 话题/政策类

| 函数 | 位置 | 用途 | 返回 | 用过页面 |
|------|------|------|------|---------|
| `get_topic_comparison_data()` | data_loader.py L492-509 | 话题对比数据 | DataFrame(话题, 总数, 负面%, 高风险%, 置信度) | **P9 Tab5** |
| `get_policy_analysis()` | data_loader.py L592-607 | 政策分析 | dict(total, pct, sentiment_dist) | **P6 Tab2** |

---

## 新增UI组件速查表

### 批量展示类

| 函数 | 位置 | 用途 | 参数 | 用过页面 |
|------|------|------|------|---------|
| `display_opinion_batch()` | components.py L334-379 | 批量意见展示 | df, max_items=10, show_fields=None, title=None | **P9 Tab7** |
| `display_search_results()` | components.py L382-413 | 搜索结果展示 | df, keyword=None, max_items=10 | **P9 Tab3** |

### 已有UI组件 (Phase 10A)

| 函数 | 位置 | 用途 |
|------|------|------|
| `display_opinion_expander()` | components.py L22-98 | 单条意见展开器 |
| `display_stat_card()` | components.py L105-122 | 统计卡片 |
| `display_stats_grid()` | components.py L125-140 | 统计网格 |
| `display_summary_box()` | components.py L225-249 | 摘要信息框 |
| `paginate_dataframe()` | components.py L256-277 | 分页处理 |

---

## 模式识别与最佳实践

### ✅ 缓存函数的标准模式

```python
@st.cache_data
def get_something(df):
    """清晰的文档字符串，包含用法示例"""
    result = df[df['condition'] == value]
    return {
        'key1': calculated_value,
        'key2': another_value
    }
```

### ✅ UI 组件的标准模式

```python
def display_something(df, max_items=10, title=None):
    """支持分页、标题、字段定制"""
    if len(df) == 0:
        st.warning("❌ 无结果")
        return
    
    if title:
        st.write(f"**{title}**")
    
    # 处理分页
    if len(df) > max_items:
        start_idx, end_idx = paginate_dataframe(df, page_size=max_items)
        display_df = df.iloc[start_idx:end_idx]
    
    # 逐行展示
    for idx, (_, row) in enumerate(display_df.iterrows()):
        # 展示逻辑
```

### ✅ 复合标签处理模式

```python
# 支持 pipe 分隔的复合标签
for actor in actor_names:
    pattern = rf'(^|\|){actor}($|\|)'  # 关键：使用 regex 匹配
    mask = df['actor'].str.contains(pattern, na=False, regex=True)
    segment_df = df[mask]
```

---

## 常见使用场景

### 场景1: 需要对特定参与方分析

```python
# ❌ 旧方法（重复计算）
consumer_df = df[df['actor'] == 'consumer']
sent_dist = consumer_df['sentiment'].value_counts()
topic_dist = consumer_df['topic'].value_counts()
# ...

# ✅ 新方法（使用缓存）
from utils.data_loader import get_actor_segment_analysis
consumer_analysis = get_actor_segment_analysis(df, 'consumer')
sent_dist = consumer_analysis['sentiment_dist']
topic_dist = consumer_analysis['topic_dist']
```

### 场景2: 需要批量展示意见

```python
# ❌ 旧方法（手写循环）
for idx, (_, row) in enumerate(results.iterrows(), 1):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**#{idx}** {row['source_text'][:80]}...")
    # ... 重复的 UI 代码

# ✅ 新方法（使用组件）
from utils.components import display_search_results
display_search_results(results, keyword=keyword, max_items=20)
```

### 场景3: 需要快速统计指标

```python
# ❌ 旧方法（重复计算）
neg_count = len(result_df[result_df['sentiment'] == 'negative'])
neg_pct = neg_count / len(result_df) * 100
high_risk = len(result_df[result_df['risk_level'].isin(['critical', 'high'])])

# ✅ 新方法（使用缓存）
from utils.data_loader import get_quick_stats
stats = get_quick_stats(result_df)
st.metric("负面占比", f"{stats['negative_pct']:.1f}%")
st.metric("高风险数", stats['high_risk_count'])
```

---

## 页面优化汇总

| 页面 | 删除行数 | 使用缓存函数 | 状态 |
|------|---------|------------|------|
| P1 (总体概览) | 0 | ✅ 已使用库函数 | 优化完成 |
| P2 (意见搜索) | 16 | get_quick_stats | ✅ |
| P3 (风险分析) | 32 | get_high_risk_analysis | ✅ |
| P4 (模式分析) | 20 | 图表库函数 | ✅ |
| P5 (参与方分析) | 36 | 3个缓存函数 | ✅ |
| P6 (政策建议) | 72 | 3个新缓存函数 | ✅ |
| P7 (话题敏感度) | 21 | get_topic_statistics | ✅ |
| P9 (互动分析) | 44 | 2个缓存+2个UI组件 | ✅ |
| **总计** | **-234** | **14 缓存 + 2 UI** | **100% 完成** |

---

## 性能优化验证清单

- [ ] 本地测试所有页面加载速度
- [ ] 验证缓存命中（通过 Streamlit 调试界面）
- [ ] 测试搜索、过滤等交互式操作
- [ ] 确认复合标签数据正确拆分（P5, P6, P9）
- [ ] 验证导出功能（P2, P9）
- [ ] Streamlit Cloud 部署前检查

---

## 快速部署检查表

```bash
# 1. 语法检查（已通过）
python -m py_compile streamlit_app/**/*.py

# 2. 导入检查
python -c "from utils.data_loader import get_quick_stats; print('✅')"
python -c "from utils.components import display_opinion_batch; print('✅')"

# 3. 本地运行
streamlit run streamlit_app/1_总体概览.py

# 4. 逐页访问测试
# P1, P2, P3, P4, P5, P6, P7, P9（无P8）

# 5. 部署
git add -A
git commit -m "Phase 10B: Code optimization, delete 234 lines, add 14 caching functions"
git push origin main
```

---

## 常见问题排查

### Q: 缓存失效了怎么办？
A: Streamlit 缓存基于输入参数的哈希值。如果输入变化，缓存自动失效。
```python
# 缓存依赖输入参数
@st.cache_data
def get_quick_stats(df):  # df 变化 → 自动重新计算
    ...
```

### Q: 复合标签没有正确拆分？
A: 检查是否使用了正确的 regex 模式：
```python
pattern = rf'(^|\|){actor}($|\|)'  # 必须有转义的 pipe
mask = df['actor'].str.contains(pattern, na=False, regex=True)
```

### Q: 页面加载变慢了？
A: 检查是否绕过了缓存函数，直接在页面级计算：
```python
# ❌ 避免这样做（不使用缓存）
df.groupby('actor')['sentiment'].value_counts()

# ✅ 使用缓存函数
get_actor_segment_analysis(df, 'consumer')['sentiment_dist']
```

### Q: 新增加一个参与方，如何维护？
A: 只需在 `data_loader.py` 的 `ACTOR_MAP` 字典中添加映射：
```python
ACTOR_MAP = {
    'consumer': '消费者',
    'enterprise': '企业',
    'new_actor': '新参与方',  # 添加这行
}
```
所有使用 `translate_actor()` 的地方自动支持。

---

## 后续维护指南

### 添加新缓存函数的步骤
1. 在 `data_loader.py` 中定义函数，使用 `@st.cache_data` 装饰
2. 添加详细的文档字符串（包含用法示例）
3. 在页面中导入并使用
4. 更新此快速参考表

### 添加新UI组件的步骤
1. 在 `components.py` 中定义函数
2. 使用现有的 `st` 容器和 `display_*` 组件
3. 支持参数化和定制
4. 更新此快速参考表

### 更新翻译映射
```python
# data_loader.py 中的 ACTOR_MAP, TOPIC_MAP, SENTIMENT_MAP, RISK_MAP
# 添加新的键值对，自动支持所有调用处
```

---

**最后更新**: 2025-12-12  
**版本**: Phase 10B Final  
**维护者**: Code Optimization Team
