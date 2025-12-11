# Streamlit网站 — 5分钟快速上手

**所需时间**：5分钟阅读 + 2小时部署 + 90分钟自动运行（可后台运行）

---

## 最小化操作清单

### 第1步：准备项目目录（2分钟）

```bash
# 创建项目文件夹
mkdir streamlit_app
cd streamlit_app

# 创建必要的子目录
mkdir pages data utils .streamlit

# 初始化Git
git init
```

### 第2步：创建最小化文件集（5分钟）

#### 📄 requirements.txt
```ini
streamlit==1.31.1
pandas==2.1.4
plotly==5.18.0
python-dotenv==1.0.0
```

#### 📄 .streamlit/config.toml
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
textColor = "#262730"

[client]
showErrorDetails = true
```

#### 📄 main.py - 首页（从06文档复制）

#### 📄 pages/1_📊_Overview.py - 详细总览（从06文档复制）

#### 📄 pages/2_🔄_Modes.py - 模式分析（从06文档复制）

#### 📄 pages/3_⚠️_Risks.py - 风险分析（从06文档复制）

#### 📄 pages/4_📈_Behaviors.py - 行为响应（从06文档复制）

#### 📄 pages/5_🏷️_Keywords.py - 关键词（从06文档复制）

#### 📄 pages/6_📋_Articles.py - 数据详览（从06文档复制）

#### 📄 pages/7_ℹ️_About.py - 关于（从06文档复制）

#### 📄 utils/data_loader.py（从06文档复制）

### 第3步：复制数据文件（1分钟）

```bash
# 将LLM分析结果复制到data目录
cp /path/to/analysis_results_5000.json data/

# 验证文件存在
ls -la data/
```

### 第4步：本地测试（2分钟）

```bash
# 进入项目目录
cd streamlit_app

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run main.py

# 应该看到：
# Local URL: http://localhost:8501
```

**在浏览器访问**：http://localhost:8501

### 第5步：推送到GitHub（2分钟）

```bash
# 添加文件
git add .

# 提交
git commit -m "Initial Streamlit opinion analysis dashboard"

# 推送
git branch -M main
git remote add origin https://github.com/[你的用户名]/opinion-analysis-dashboard.git
git push -u origin main
```

### 第6步：部署到Streamlit Cloud（自动，5-10分钟）

1. 访问 https://streamlit.io/cloud
2. 用GitHub账户登录
3. 点击 "New app"
4. 选择：
   - Repository: `opinion-analysis-dashboard`
   - Branch: `main`
   - Main file path: `streamlit_app/main.py`
5. 点击 "Deploy"

**等待部署完成**（3-5分钟）

**获得URL**：
```
https://[username]-opinion-analysis.streamlit.app/
```

---

## 完整代码速查

所有代码都在 `06_可视化网站_Streamlit完整方案.md` 中，按如下顺序复制：

| 文件 | 来源 | 步骤 |
|-----|------|------|
| main.py | 第三部分，步骤5 | 复制 |
| pages/1_📊_Overview.py | 第三部分，步骤6 | 复制 |
| pages/2_🔄_Modes.py | 第三部分，步骤7 | 复制 |
| pages/3_⚠️_Risks.py | 第三部分，步骤8 | 复制 |
| pages/4_📈_Behaviors.py | 第三部分，步骤9 | 复制 |
| pages/5_🏷️_Keywords.py | 第三部分，步骤10 | 复制 |
| pages/6_📋_Articles.py | 第三部分，步骤11 | 复制 |
| pages/7_ℹ️_About.py | 第三部分，步骤12 | 复制 |
| utils/data_loader.py | 第三部分，步骤4 | 复制 |

---

## 故障排查

### ❌ ModuleNotFoundError

```bash
# 重新安装依赖
pip install -r requirements.txt
```

### ❌ FileNotFoundError: analysis_results_5000.json

```bash
# 确认文件存在
ls -la data/

# 检查LLM分析是否完成（应该是~50MB的JSON文件）
```

### ❌ JSON解析错误

检查 `data/analysis_results_5000.json` 的格式：
```python
import json
with open('data/analysis_results_5000.json') as f:
    data = json.load(f)  # 如果出错，JSON格式有问题
```

### ❌ 图表不显示

- 检查数据是否为空：`len(df) > 0`
- 检查Plotly是否安装：`pip install plotly==5.18.0`

### ❌ Streamlit部署失败

检查 GitHub Actions 日志：
1. 访问你的仓库
2. 点击 "Actions"
3. 查看失败的workflow详情
4. 通常是依赖版本问题，更新 `requirements.txt`

---

## 验证清单

部署完成后，逐项检查：

- [ ] 首页能加载
- [ ] 能看到4个关键指标卡片
- [ ] 情感分布饼图显示正确
- [ ] 模式分布柱状图显示正确
- [ ] 风险排行显示正确
- [ ] 点击左侧菜单能打开其他页面
- [ ] 📊 详细总览页能显示
- [ ] 🔄 模式分析页的Tab能切换
- [ ] ⚠️ 风险分析页的热力图显示正确
- [ ] 📈 行为页的数据分布显示
- [ ] 🏷️ 关键词页的词云显示
- [ ] 📋 数据详览页能搜索和筛选
- [ ] ℹ️ 关于页能显示

---

## 接下来的工作

✅ **网站部署完成后**：

1. **分享链接** → 给论文审稿人或政策制定者
2. **收集反馈** → 了解用户想看什么
3. **添加功能** → 根据反馈迭代
4. **写论文** → 用网站的截图和数据
5. **发表** → 网站可以在论文中引用

---

## 成本确认

| 项目 | 成本 |
|-----|------|
| Streamlit部署 | ¥0 |
| 域名（可选） | ¥50-100/年 |
| GitHub | ¥0 |
| 总计 | **¥0** |

---

## 时间进度表

| 时间 | 任务 | 耗时 |
|-----|------|------|
| **12月16-30日** | ✅ 完成LLM分析 | 完成 |
| **1月1-2日** | 创建项目目录 + 复制代码 | 2小时 |
| **1月3-22日** | （代码已全部提供，不需要额外开发） | — |
| **1月23-25日** | 本地测试 | 2小时 |
| **1月26日** | 推送GitHub | 10分钟 |
| **1月26-31日** | Streamlit Cloud自动部署 | 自动 |
| **预期上线日期** | **1月31日** | ✅ |

---

## 最关键的一步

**这一步决定了能否部署成功**：

```bash
# 确保你的data/analysis_results_5000.json文件格式正确：
python -c "
import json
with open('data/analysis_results_5000.json') as f:
    data = json.load(f)
    print(f'✅ JSON格式正确，共{len(data[\"results\"])}条记录')
"
```

**如果上面命令能执行，说明数据准备无误，网站部署一定成功！**

---

## 联系与支持

有问题的话：

1. **检查06文档** → 完整代码都在里面
2. **检查错误信息** → 通常会告诉你具体问题
3. **查看Streamlit日志** → `streamlit run main.py` 的输出

---

**准备好了吗？现在就可以开始！** 🚀

从创建目录到网站上线，整个过程只需要：
- ⏱️ 实际操作：30分钟
- ⏳ 自动部署：5分钟
- 📝 代码复制：2小时（但是就是复制粘贴，不需要理解代码）

**预计1月31日前完全上线！**
