# Phase 2 执行指南 - LLM舆论分析（已修复）

## 项目概况
跨境电商税收舆论分析系统，使用智谱清言API进行5维度结构化分析。

- **数据来源**: 小红书爬取的3,613条原始意见
- **数据清洁**: 已完成，得到2,313条清洁意见（`data/clean/opinions_clean_5000.txt`）
- **分析维度**: 5个维度（情感、话题、模式、风险等级、行为主体）
- **API**: 智谱清言 (glm-4-flash)

---

## 修复内容 (2025-12-10)

### 问题1：包导入错误
- **问题**: zhipuai包缺少依赖（sniffio）
- **修复**: `pip install sniffio`

### 问题2：JSON解析错误
- **问题**: API响应被markdown代码块包装 ````json ... ` ```
- **修复**: 在所有脚本中添加JSON提取逻辑
  ```python
  if result_text.startswith("```"):
      start = result_text.find('\n') + 1
      end = result_text.rfind('```')
      result_text = result_text[start:end].strip()
  result = json.loads(result_text)
  ```

### 修复的脚本
- ✅ `test_sample_100.py` - 样本测试（100条）
- ✅ `test_quick_10.py` - 快速测试（10条）**[NEW]**
- ✅ `llm_analyze.py` - 全量分析脚本

---

## 执行步骤

### 步骤1：快速验证（可选，仅需3-5分钟）
```bash
cd "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"
python test_quick_10.py
```

**预期结果**: 10/10 成功，所有意见分析通过

### 步骤2：样本测试（需要30-40分钟）
```bash
python test_sample_100.py
```

**预期结果**:
- 成功率 ≥ 85%（≥85条）
- 平均置信度 ≥ 0.80
- 生成 `data/analysis/sample_100_results.json`

**检查结果**:
```bash
# 查看输出
type data\analysis\sample_100_results.json

# 快速检查成功率
findstr "success_rate" data\analysis\sample_100_results.json
```

### 步骤3：全量分析（如果样本测试通过）（需要1.5-2小时）
```bash
python llm_analyze.py
```

**预期结果**:
- 分析全部2,313条意见
- 生成 `data/analysis/analysis_results.json`
- 输出统计数据（情感分布、话题分布等）

---

## 测试结果总结

### 快速测试 (10条) - ✅ 通过
```
成功率: 100% (10/10)
情感分布: 
  - negative: 3 (30%)
  - neutral: 6 (60%)
  - positive: 1 (10%)
```

### 样本测试 (100条) - ⏳ 进行中...
- 预期完成时间: 12月10日 23:30-23:45
- 结果文件: `data/analysis/sample_100_results.json`

---

## 常见问题

### Q: 运行超时怎么办？
A: API调用每条需要1-3秒，100条需要约30-40分钟。可以：
1. 在后台运行（不要关闭Terminal）
2. 修改脚本中的SAMPLE_SIZE参数来测试更小样本
3. 检查网络连接稳定性

### Q: API密钥过期了怎么办？
A: 如果所有请求都失败：
1. 检查密钥: `57f5636a5d984e18b983ba0e542f3aa4.Ib9C6j2zKNnXvLAm`
2. 验证是否被限速（太多请求）
3. 登录智谱AI控制台重新生成密钥

### Q: JSON解析仍然失败？
A: 检查原始API响应是否包含代码块标记。修复代码已应用到所有脚本。

---

## 后续步骤

当样本测试成功率 ≥ 85% 且平均置信度 ≥ 0.80：
1. 运行全量分析（`python llm_analyze.py`）
2. Phase 3: 网站原型设计（前端+后端）
3. Phase 4: 数据可视化和报告生成
4. Phase 5: 论文撰写和发布

---

## 技术栈
- **数据清洁**: Python (pandas, pathlib)
- **LLM分析**: 智谱AI API (glm-4-flash)
- **输出格式**: JSON
- **编码**: UTF-8

---

**最后更新**: 2025-12-10 23:22
**状态**: 快速测试通过 ✅ | 样本测试进行中 ⏳
