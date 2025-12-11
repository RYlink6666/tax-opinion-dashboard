# 第二阶段：LLM分析执行指南（12.16-30）

## 📊 现状

✅ **第一阶段完成**
- 原始数据：3,613 条
- 清洁数据：2,313 条
- 输出：`data/clean/opinions_clean_5000.txt`

## 🎯 第二阶段目标

分析2,313条清洁舆论，输出5维度结构化数据：

| 维度 | 取值范围 | 说明 |
|------|---------|------|
| **sentiment** | positive / neutral / negative | 情感倾向 |
| **topic** | tax_policy / price_impact / compliance / business_risk / advocacy / other | 核心话题 |
| **pattern** | 0110 / 9610 / 9710 / 9810 / 1039 / Temu / multiple / unknown | 跨境模式 |
| **risk_level** | critical / high / medium / low | 风险程度 |
| **actor** | enterprise / consumer / government / cross_border_seller / general_public / multiple | 参与方 |

**关键配置**：
- API密钥：已配置
- 模型：`glm-4-flash`（速度快，精度好）
- 费用：0元（用已有token）

---

## 🚀 执行步骤

### 步骤1：环境检查（5分钟）

```bash
# 检查Python
python --version

# 安装zhipu-ai
pip install zhipu-ai
```

### 步骤2：样本测试（30分钟）

**先用100条样本验证分析质量**

```bash
python test_sample_100.py
```

**预期输出**：
```
[OK] Sample test complete!

[STATS] Quality check
Total analyzed: 100/100
Success rate: 100.0%

[SENTIMENT] Distribution:
  positive: 25 (25%)
  negative: 45 (45%)
  neutral: 30 (30%)

[CONFIDENCE] Sentiment avg: 0.88
```

**验证检查清单**：
- [ ] 成功率 ≥ 85%
- [ ] 平均置信度 ≥ 0.80
- [ ] 能否区分正负面（负面通常多于正面）
- [ ] 话题识别合理（应该主要是tax_policy）

### 步骤3：全量分析（8-12小时）

如果样本测试满意（>=85%成功率），进行全量分析：

```bash
python llm_analyze.py
```

**预期输出**：
```
[OK] Analysis complete
[OUTPUT] data/analysis/analysis_results.json

[STATS] Analysis summary
======================================

[SENTIMENT] Distribution:
  negative: 1100 (47.6%)
  neutral: 650 (28.1%)
  positive: 563 (24.3%)

[TOPIC] Distribution:
  tax_policy: 1450 (62.7%)
  price_impact: 520 (22.5%)
  compliance: 200 (8.7%)
  ...

[RISK] Distribution:
  high: 890 (38.5%)
  medium: 890 (38.5%)
  low: 533 (23.0%)

[CONFIDENCE] Average: 0.85
```

### 步骤4：质量验证（30分钟）

```bash
python validate_analysis.py  # （后续提供）
```

---

## 📁 输出文件

| 文件 | 大小 | 用途 |
|------|------|------|
| `data/analysis/sample_100_results.json` | ~200KB | 样本验证 |
| `data/analysis/analysis_results.json` | ~5-8MB | 最终结果 |
| `logs/analysis.log` | ~1MB | 执行日志 |

---

## ⚙️ 关键参数

### API调用参数

```python
temperature = 0.3    # 保守，结果稳定
top_p = 0.8         # 多样性适中
batch_size = 50     # 每批处理50条
retry_times = 3     # 失败重试3次
delay = 1秒          # 批次间隔（避免限流）
```

### 时间预估

| 阶段 | 耗时 | 说明 |
|------|------|------|
| 环境检查 | 5分钟 | 安装依赖 |
| 样本测试 | 30分钟 | 100条×API平均速度 |
| 全量分析 | 8-12小时 | 2313条，API QPS限制 |
| 质量验证 | 30分钟 | 统计和检查 |
| **合计** | **9-13小时** | **可在一晚完成** |

---

## 🛠️ 故障排查

### 问题1：ImportError: No module named 'zhipu_ai'

```bash
pip install zhipu-ai
```

### 问题2：API Key错误

检查API密钥是否正确：
```python
# 在llm_analyze.py中检查
API_KEY = "57f5636a5d984e18b983ba0e542f3aa4.Ib9C6j2zKNnXvLAm"
```

### 问题3：JSON解析失败

部分API响应可能不是有效JSON，脚本会自动跳过并继续。最终成功率应 ≥85%。

### 问题4：API调用超限

如果出现429错误，增加延迟：
```python
# 在llm_analyze.py中修改
time.sleep(2)  # 改为2秒
```

---

## 📋 检查清单

### 开始前
- [ ] Python环境 ≥ 3.8
- [ ] zhipu-ai包已安装
- [ ] API密钥有效
- [ ] `data/clean/opinions_clean_5000.txt` 存在

### 样本测试后
- [ ] 100条全部成功处理
- [ ] 情感分布合理（负面>正面）
- [ ] 平均置信度 ≥ 0.80
- [ ] 话题识别准确

### 全量分析后
- [ ] 2313条全部处理
- [ ] 成功率 ≥ 85%
- [ ] JSON文件有效
- [ ] 统计数据合理

---

## 📞 后续步骤

✅ 完成本阶段 → 

**第三阶段（2026.1.1-31）**：Streamlit网站开发

**第四阶段（2026.2.1-28）**：网站优化与反馈

**第五阶段（2026.3.1-31）**：论文撰写与发表

---

**预计完成时间**：12月30日  
**关键deadline**：12月31日前必须完成  
**质量目标**：精度 ≥ 85%，可用性 100%
