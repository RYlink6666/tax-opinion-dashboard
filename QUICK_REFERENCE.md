# 快速参考指南

## 快速命令

### 检查进度（任意时刻）
```bash
cd "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"
python check_progress.py
```

### 快速验证API (3分钟)
```bash
python test_quick_10.py
```

### 样本测试 (30-40分钟) - 两个版本选一个
```bash
# 版本1: 原始版本（运行中可能看不到细致进度）
python test_sample_100.py

# 版本2: 改进版本（显示逐条进度和时间估计）
python test_sample_100_fixed.py
```

### 全量分析 (1.5-2小时) - 只有样本通过才运行
```bash
python llm_analyze.py
```

---

## 预期结果范围

| 阶段 | 文件 | 预期成功率 | 平均置信度 | 时间 |
|------|------|----------|----------|------|
| 快速测试 | sample_10_results.json | 100% | 0.85+ | 3-5分钟 |
| 样本测试 | sample_100_results.json | ≥85% | ≥0.80 | 30-40分钟 |
| 全量分析 | analysis_results.json | ≥85% | ≥0.75 | 1.5-2小时 |

---

## 文件位置

### 脚本
- `test_quick_10.py` - 快速测试
- `test_sample_100.py` - 样本测试 (原版)
- `test_sample_100_fixed.py` - 样本测试 (改进版)
- `llm_analyze.py` - 全量分析
- `check_progress.py` - 进度检查

### 数据
- 输入: `data/clean/opinions_clean_5000.txt` (2,299条)
- 输出: `data/analysis/sample_10_results.json`
- 输出: `data/analysis/sample_100_results.json`
- 输出: `data/analysis/analysis_results.json`

---

## 关键配置

| 项 | 值 |
|----|-----|
| API模型 | glm-4-flash |
| API温度 | 0.3 |
| Top-P | 0.8 |
| 编码 | UTF-8 |

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| ImportError: sniffio | `pip install sniffio` |
| JSON解析错误 | 检查是否使用了修复版脚本（已包含提取逻辑） |
| API超时 | 检查网络，等待几分钟重试 |
| 成功率低 | 使用改进版 `test_sample_100_fixed.py` 查看详细错误 |

---

## 依赖包

```bash
pip install zhipuai sniffio
```

确认安装:
```bash
pip list | findstr zhipu
pip list | findstr sniffio
```

---

## 分析维度说明

```json
{
  "sentiment": "positive|neutral|negative",           // 情感
  "topic": "tax_policy|price_impact|compliance|...",  // 话题
  "pattern": "0110|9610|9710|9810|1039|Temu|...",    // 模式
  "risk_level": "critical|high|medium|low",          // 风险
  "actor": "enterprise|consumer|government|...",     // 行为主体
  "sentiment_confidence": 0.85,                       // 置信度 (0-1)
  "key_phrase": "关键短语",
  "brief_summary": "简短总结"
}
```

---

## 项目状态 (2025-12-10 23:25)

- ✅ 快速测试完成 (10/10)
- ⏳ 样本测试进行中 (100/100)
- ⏸ 全量分析待启动 (2,313)

**下一步**: 等待样本测试完成，运行 `check_progress.py` 验证

---

**更新**: 2025-12-10  
**项目**: 跨境电商税收舆论分析系统
