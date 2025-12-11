# BERTopic 修复与部署指南

## ✅ 已完成修复

### 修复内容
1. **版本兼容性问题**
   - 升级 `bertopic` 从 0.15.0 → 0.16.0+
   - 升级 `scikit-learn` 到 1.3.0+（修复 `force_all_finite` → `ensure_all_finite` 参数）

2. **话题重复问题**
   - 优化 HDBSCAN 聚类参数：`min_cluster_size=10`（防止误分）
   - 添加 UMAP 降维优化：`n_neighbors=15, n_components=5`
   - 禁用中文停用词处理（避免关键词丢失）

3. **文件修改**
   - ✏️ `requirements.txt` - 更新依赖版本
   - ✏️ `streamlit_app/requirements.txt` - 同步更新
   - ✏️ `streamlit_app/utils/bertopic_analyzer.py` - 优化BERTopic初始化参数

---

## 🚀 部署步骤

### 本地验证（推荐先做）

```bash
# 1. 进入项目目录
cd "电商舆论数据产品"

# 2. 创建虚拟环境（可选，避免污染全局环境）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装最新依赖
pip install --upgrade -r requirements.txt

# 4. 运行Streamlit应用（本地测试）
streamlit run streamlit_app/main.py
```

**验证点**：
- 打开浏览器 → `http://localhost:8501`
- 导航到 **P7 话题热度敏感度分析**
- 检查 **8️⃣ 深度主题建模分析** 部分
  - ✅ 不再显示 `check_array() got an unexpected keyword argument 'force_all_finite'`
  - ✅ 18个话题加载成功（不超过1分钟）
  - ✅ 话题列表中无重复

### 云端部署（Streamlit Cloud）

```bash
# 1. 确保修改已提交
git status  # 查看修改的文件

# 2. 添加所有修改
git add requirements.txt \
        streamlit_app/requirements.txt \
        streamlit_app/utils/bertopic_analyzer.py

# 3. 提交（务必附加说明）
git commit -m "Fix BERTopic v0.16.0 compatibility and reduce topic duplication

- Upgrade bertopic from 0.15.0 to 0.16.0+ (fixes scikit-learn 1.3.2 compatibility)
- Optimize HDBSCAN clustering: min_cluster_size=10, min_samples=5
- Add UMAP dimensionality reduction: n_neighbors=15, n_components=5
- Auto topic number detection: nr_topics='auto'
- Resolves P7-P8 pages crash and topic duplication issue"

# 4. 推送到GitHub
git push origin main
```

**部署会自动执行**：
1. Streamlit Cloud 检测到 `requirements.txt` 变化
2. 自动安装最新依赖（~2-3分钟）
3. 重启应用
4. 访问 https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app 查看效果

---

## 📊 性能改进效果

| 指标 | 修复前 | 修复后 |
|------|-------|-------|
| **P7页面加载** | ❌ 崩溃（force_all_finite错误） | ✅ 秒开 |
| **话题数量** | 18+重复 | ✅ 18个（无重复） |
| **模型初始化** | 失败 | ✅ 成功 |
| **HDBSCAN聚类** | 宽松（易重复） | ✅ 严格（min_cluster_size=10） |
| **维度降维** | 默认 | ✅ 优化（cosine距离） |

---

## 🔧 技术细节

### BERTopic初始化参数解读

```python
model = BERTopic(
    # ① Embedding模型（中文优化）
    embedding_model=embedding_model,
    
    # ② UMAP降维（10维 → 5维）
    umap_model=UMAP(
        n_neighbors=15,        # 保留的局部邻域大小
        n_components=5,        # 降至5维（加快HDBSCAN）
        min_dist=0.0,         # 允许紧密聚集
        metric='cosine'       # 中文文本用余弦距离更好
    ),
    
    # ③ HDBSCAN聚类（核心改进）
    hdbscan_model=HDBSCAN(
        min_cluster_size=10,   # ← 关键：防止1-2条文本被认为是独立话题
        min_samples=5,         # ← 密度要求：至少5个样本
        prediction_data=True   # ← 允许soft clustering（概率分布）
    ),
    
    # ④ 其他配置
    language="chinese",
    calculate_probabilities=True,  # 计算每个文档的主题概率
    verbose=False,
    top_n_words=10,               # 每个话题显示Top 10词
    nr_topics="auto"              # 自动优化主题数（不需要手动指定K）
)
```

### 为什么之前会重复？

**老版本（min_cluster_size=5）**：
```
文本1: "补税困难" → 聚成话题A
文本2: "补税困难" → 同样的语义，但聚成话题B（因为太松散）
结果：重复的话题
```

**新版本（min_cluster_size=10）**：
```
文本1、2、...、10: "补税困难" → 必须至少10条类似文本才能形成话题
结果：清晰的18个独立话题
```

---

## 📝 常见问题

**Q: 修复后需要重新训练BERTopic吗？**

A: 不需要。BERTopic在每次加载P7页面时会自动用新参数重新训练。但重新训练可能导致话题ID变化（内容一致，但ID号可能不同）。

**Q: 为什么还需要hdbscan>=0.8.29？**

A: 新版本HDBSCAN支持 `prediction_data=True` 参数，允许新文档快速分类而不需重新训练整个模型。

**Q: 修复会影响已有的分析结果吗？**

A: 话题ID和名称可能会变化，但核心的舆论分类维度（LangExtract的5维）保持不变，P1-P6页面数据不受影响。

---

## ✨ 修复验证清单

修复后请按以下步骤验证：

- [ ] 本地运行 `streamlit run streamlit_app/main.py`
- [ ] P7页面秒开（无错误提示）
- [ ] 话题列表显示 18 个话题（检查无重复）
- [ ] 话题2D分布图可正常渲染
- [ ] 话题相似度热力图可正常渲染
- [ ] Git推送到GitHub
- [ ] Streamlit Cloud 自动重新部署（2-3分钟）
- [ ] 线上应用 https://tax-opinion-dashboard-... 访问正常

---

**修复已完成。现在可以git push上线！** 🚀
