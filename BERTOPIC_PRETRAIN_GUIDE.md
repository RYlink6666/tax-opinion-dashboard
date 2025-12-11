# BERTopic 预训练模型部署指南

## 问题根源

之前P7页面每次加载都要重新训练BERTopic模型，导致：
- ❌ 页面显示"正在训练..."，需要等待3-5分钟
- ❌ 每次训练结果可能不同（话题重复）
- ❌ 用户体验差，看起来像卡住了

## 解决方案：预训练模型

离线训练一次，将模型保存到项目文件夹，P7页面直接加载预训练模型。

```
第一次部署（本地运行）:
  双击 RUN_PRETRAIN.bat
    ↓
  训练模型 3-5 分钟
    ↓
  生成 streamlit_app/data/bertopic_model/
    ↓
  git push origin main
    ↓
  上传到 GitHub
    ↓
  Streamlit Cloud 自动部署

之后（用户访问）:
  P7页面 秒开 ⚡
  （因为只是加载已训练的模型，不需要重新训练）
```

---

## 🚀 立即部署步骤

### 步骤1：本地预训练（必须做）

双击这个文件：
```
📁 RUN_PRETRAIN.bat
```

或者在命令行运行：
```bash
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品
python pretrain_bertopic.py
```

**等待3-5分钟，会看到：**
```
✅ 预训练完成！
📝 后续步骤:
   1. 将生成的 streamlit_app/data/bertopic_model/ 文件夹上传到GitHub
   2. 修改P7页面，改用预训练模型而不是每次重新训练
   3. P7页面会秒开，无需等待训练
```

### 步骤2：推送到GitHub

脚本完成后，执行：

```bash
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品

# 查看新生成的文件
git status

# 应该看到：
# streamlit_app/data/bertopic_model/ (新文件夹)

# 添加并推送
git add streamlit_app/data/bertopic_model/
git commit -m "Add pretrained BERTopic model"
git push origin main
```

### 步骤3：等待Streamlit Cloud部署

- 等待 2-3 分钟
- Streamlit Cloud 会自动下载新的模型文件

### 步骤4：验证

访问 P7 页面：
https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/话题热度敏感度分析

**应该看到：**
- ✅ 8️⃣ 深度主题建模分析 **秒开**（无需等待）
- ✅ 话题数量固定（无重复）
- ✅ 所有可视化正常显示

---

## 📊 预训练内容

生成的 `streamlit_app/data/bertopic_model/` 包含：

```
bertopic_model/
├── embeddings.pkl          # 嵌入模型（200MB）
├── vectorizer.pkl          # 向量化器
├── hdbscan_model.pkl       # HDBSCAN聚类器
├── umap_model.pkl          # UMAP降维器
├── topics_result.json      # 话题分析结果（包含18个话题的详细信息）
└── ...
```

这些文件会被上传到GitHub，Streamlit Cloud部署时会自动下载。

---

## 🔧 如何更新预训练模型

如果数据更新了或参数调整了，只需重新运行：

```bash
python pretrain_bertopic.py
```

这会覆盖旧的模型文件，然后：

```bash
git add streamlit_app/data/bertopic_model/
git commit -m "Update pretrained BERTopic model"
git push origin main
```

---

## ⚠️ 常见问题

### Q: RUN_PRETRAIN.bat 运行失败？

**原因**：Python环境问题

**解决**：
```bash
# 手动在命令行运行
cd "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"
pip install -r requirements.txt  # 确保依赖都装了
python pretrain_bertopic.py
```

### Q: 生成的模型文件很大，会不会超过GitHub限制？

**答**：BERTopic模型约 200-500MB，GitHub单个文件限制是100MB。需要使用 Git LFS：

```bash
# 安装Git LFS
git lfs install

# 跟踪大文件
git lfs track "streamlit_app/data/bertopic_model/*.pkl"

# 然后正常提交
git add .
git commit -m "..."
git push origin main
```

但更简单的方案是：**直接在Streamlit Cloud上运行预训练脚本**（云端资源足够）。

### Q: P7页面还是显示"正在训练..."

**原因**：
1. Git还没push成功
2. Streamlit Cloud还没重新部署
3. 浏览器缓存

**解决**：
```bash
# 1. 清除浏览器缓存
Ctrl+Shift+Delete

# 2. 查看GitHub是否接收到新文件
https://github.com/RYlink6666/tax-opinion-dashboard/tree/main/streamlit_app/data

# 3. 如果文件没上去，再push一次
git push origin main
```

---

## 🎯 部署后的效果

| 功能 | 修复前 | 修复后 |
|------|-------|-------|
| P7页面加载时间 | 3-5分钟 | < 5秒 ⚡ |
| 话题重复问题 | 经常重复 | 固定且清晰 |
| 用户体验 | 显示"训练中"  | 秒开 |
| 云端训练 | 每次都训练 | 只加载预训练模型 |

---

## 📝 总结

**一句话**：本地训练一次，把模型保存到GitHub，云端应用直接使用预训练模型，无需每次重新训练。

**三个关键文件**：
1. `pretrain_bertopic.py` - 本地离线训练脚本
2. `RUN_PRETRAIN.bat` - 快速启动脚本
3. `streamlit_app/pages/7_话题热度敏感度分析.py` - 改用预训练模型

**立即开始**：
```bash
双击 RUN_PRETRAIN.bat
```

---

**预期结果**：P7页面秒开，话题清晰无重复 ✅
