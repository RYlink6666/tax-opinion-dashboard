# 全面修复所有英文 - 执行计划

## 发现的英文位置清单

### 1. main.py 中的英文
- [x] 图表labels中的英文（sentiment/risk/topic/actor）
- [ ] 图表title中的英文
- [ ] 其他st.write中的英文

### 2. 1_Overview.py
- [x] st.write中的英文
- [ ] 图表title：title="话题分布排行" ✅ 已中文
- [ ] 图表title：title="风险分布" ✅ 已中文
- [ ] labels中的英文（需翻译sentiment_labels）

### 3. 2_Search.py
- [x] st.write中的sentiment/topic/actor/risk
- [ ] 需要检查其他英文

### 4. 3_Risk_Analysis.py
- [x] st.write中的sentiment/topic/actor
- [ ] labels中的英文（已有risk_labels字典）

### 5. 4_Pattern_Analysis.py
- [ ] st.write中的pattern
- [ ] 图表labels

### 6. 5_Actor_Analysis.py
- [x] st.write中的actor/topic/sentiment
- [ ] 图表labels中的actor_dist.index

### 7. 6_Policy_Recommendations.py
- [x] st.write中的sentiment/topic/actor
- [ ] 图表labels

## 关键修复

### 修复1: 图表labels翻译
```python
# main.py 第46, 110行
# 需要将labels从原始英文翻译：
labels=sentiment_dist.index,  # ❌
# 改为：
labels=[translate_sentiment(k) for k in sentiment_dist.index],  # ✅

# 同理对topic_dist, risk_ordered, actor_dist等
```

### 修复2: 5_Actor_Analysis.py中的Pie图
```python
# 第44行
labels=actor_dist.index,  # ❌ 显示英文actor
# 改为：
labels=[translate_actor(k) for k in actor_dist.index],  # ✅
```

### 修复3: 其他图表
- Bar图: orientation='h'时，y轴标签需翻译
- Heatmap: x和y轴标签需翻译

## 执行步骤
1. 修复main.py的所有图表labels
2. 修复Overview.py的图表
3. 修复Risk_Analysis.py的risk_labels（已有翻译字典）
4. 修复5_Actor_Analysis.py的actor labels
5. 修复6_Policy的图表
6. 最后检查确保无遗漏的英文

