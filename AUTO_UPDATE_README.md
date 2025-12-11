# 半自动化数据更新系统

**核心思想**: 一键运行分析脚本，自动完成：数据分析 → 保存结果 → 推送GitHub → 网站自动部署

---

## 快速开始（3步）

### 1️⃣ 设置API密钥（一次性）

**Windows：**
```cmd
set ZHIPU_API_KEY=sk_your_api_key_here
```

或在系统环境变量中设置（见 SCHEDULE_TASKS.md）

**Linux/Mac：**
```bash
export ZHIPU_API_KEY=sk_your_api_key_here
```

### 2️⃣ 手动运行分析（测试）

**Windows：**
```cmd
双击 auto_analyze.bat
或
python auto_analyze.py
```

**Linux/Mac：**
```bash
python auto_analyze.py
```

脚本会自动：
- 📥 加载原始数据（5000条）
- 📋 检查已分析vs未分析
- 🤖 调用Zhipu AI分析新数据
- 💾 保存结果到JSON
- 📤 推送到GitHub
- 🚀 Streamlit自动部署更新

### 3️⃣ 设置定时任务（可选）

见 `SCHEDULE_TASKS.md`

---

## 工作流程图

```
原始数据 (5000条)
    ↓
auto_analyze.py 脚本
    ├→ 加载已分析结果 (当前1399条)
    ├→ 查找未分析的 (剩余3601条)
    ├→ 批量调用Zhipu API
    ├→ 合并新旧结果
    └→ 保存到 analysis_results.json
    ↓
git add / commit / push
    ↓
GitHub 仓库更新
    ↓
Streamlit Cloud 自动部署
    ↓
网站显示最新数据 ✨
```

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `auto_analyze.py` | 核心分析脚本（Python） |
| `auto_analyze.bat` | Windows启动脚本 |
| `SCHEDULE_TASKS.md` | 定时任务设置指南 |
| `data/clean/opinions_clean_5000.json` | 原始数据（已清理） |
| `data/analysis/analysis_results.json` | 分析结果（不断更新） |
| `auto_analyze.log` | 运行日志（自动生成） |

---

## 完整分析流程

### 数据来源
```
小红书、微博、知乎等
    ↓
数据爬虫（需自己维护）
    ↓
opinions_clean_5000.json
```

### 分析过程
```
原始文本
    ↓
Zhipu AI LLM
    ├→ 情感分析 (positive/neutral/negative)
    ├→ 话题分类 (tax_policy/business_risk/...)
    ├→ 风险等级 (critical/high/medium/low)
    ├→ 参与方识别 (consumer/enterprise/...)
    └→ 模式识别 (opinion_pattern)
    ↓
JSON结构化数据
    ↓
Streamlit网页可视化
```

---

## 成本参考

基于Zhipu API定价（约¥0.0005/token）：

**当前状态**：
- 已分析：1,399条 ≈ ¥100-150
- 待分析：3,601条 ≈ ¥250-350

**建议更新策略**：
1. **初始化**（现在）：一次性分析全部5000条 ≈ ¥300-400
2. **定期维护**（之后）：每周新增200-300条 ≈ ¥20-40/周

---

## 常见问题

### Q: 脚本会自动爬虫吗？
**A**: 不会。原始数据需要自己通过爬虫获取，放在 `data/clean/` 目录。脚本只负责分析已有的原始数据。

### Q: 可以修改API吗？
**A**: 可以。修改 `auto_analyze.py` 中的 `analyze_with_zhipu()` 函数，支持其他LLM（如OpenAI、Claude等）。

### Q: 分析会很慢吗？
**A**: 取决于数据量和API速度。1000条数据通常需要5-10分钟。

### Q: 能只分析某些特定话题吗？
**A**: 可以。修改脚本添加过滤条件，或手动删除不需要的原始数据再运行。

### Q: 网站更新需要多久？
**A**: 推送GitHub后，Streamlit通常在2-5分钟内自动部署新版本。

---

## 进阶配置

### 自定义分析字段

编辑 `auto_analyze.py` 的 `analyze_with_zhipu()` 函数，可以：
- 添加新的分析维度（如舆论热度、传播力等）
- 修改LLM Prompt
- 改变API调用参数

### 多源数据合并

如果要从多个平台爬取数据：

```python
# 合并多个JSON文件
opinions = []
for file in ['小红书.json', '微博.json', '知乎.json']:
    with open(file) as f:
        opinions.extend(json.load(f))

# 去重和清理
opinions = deduplicate_and_clean(opinions)

# 保存到标准位置
with open('data/clean/opinions_clean_5000.json', 'w') as f:
    json.dump(opinions, f, ensure_ascii=False)
```

### 批量处理大数据

如果数据超过10000条，建议分批处理：

```bash
# 分批分析
python auto_analyze.py --batch-size 500
```

---

## 系统要求

- **Python**: 3.8+
- **依赖**: requests, pandas, zhipuai, streamlit
- **网络**: 需要能访问GitHub和Zhipu API
- **存储**: 原始数据 + 分析结果 ≈ 50-100MB

---

## 维护建议

| 任务 | 频率 | 说明 |
|------|------|------|
| 运行分析脚本 | 每周 | 保持数据最新 |
| 检查成本 | 每月 | 监控API支出 |
| 更新原始数据 | 按需 | 添加新的舆论数据 |
| 备份分析结果 | 每月 | 防止数据丢失 |
| 检查日志 | 运行后 | 确保没有错误 |

---

## 下一步

1. ✅ 测试脚本：`python auto_analyze.py`
2. ✅ 查看日志：`auto_analyze.log`
3. ✅ 设置定时任务：见 `SCHEDULE_TASKS.md`
4. ✅ 监控网站：https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/

---

**问题？** 查看脚本输出或日志文件，通常能快速诊断问题。

**需要改进？** 直接编辑脚本，Python易于修改！
