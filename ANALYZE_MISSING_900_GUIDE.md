# 分析缺失的900条记录 - 执行指南

## 当前状态
- ✅ 已分析: 1,399 条
- ❌ 缺失: ~900 条（索引0-899）
- 📊 覆盖率: 60.5%
- 🎯 目标: 扩展到 ~2,300 条（覆盖率99.5%）

## 两种方式执行

### 方式1：使用新脚本（推荐）- 专为补充缺失数据优化

```bash
# 方式1a: Windows (推荐)
double-click analyze_missing_900.bat

# 方式1b: PowerShell
python analyze_missing_900.py

# 方式1c: 命令行
python analyze_missing_900.py
```

**优势:**
- 专门针对缺失记录设计
- 更清晰的进度显示
- 自动合并和推送
- 耗时: 约10-20分钟（900条）

### 方式2: 使用通用脚本 - 适合定期更新

```bash
# Windows
auto_analyze.bat

# 或直接执行
python auto_analyze.py
```

**优势:**
- 通用脚本，可定期调度
- 自动检测任何新增数据
- 支持环境变量配置

---

## 前置条件

### 1. 检查依赖
```bash
pip install zhipuai
```

### 2. 验证API密钥
```bash
# 方式A: 设置环境变量（推荐用于长期运行）
set ZHIPU_API_KEY=91cff4bec1fe4bdfa2cb35fc5ca03002.YngoEUjQqKF0f6qN

# 方式B: 脚本中已内置（用于临时运行）
# 已在 analyze_missing_900.py 和 auto_analyze.py 中内置
```

### 3. 检查网络
```bash
ping api.zhipuai.com
```

---

## 执行流程

### 步骤1: 准备阶段
```bash
# 进入项目目录
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品

# 检查数据文件
dir data\clean\opinions_clean_5000.json
dir data\analysis\analysis_results.json
```

### 步骤2: 运行分析
```bash
# 推荐：使用新脚本
python analyze_missing_900.py

# 或者双击
analyze_missing_900.bat
```

### 步骤3: 监控进度
脚本会显示:
```
🔍 检查未分析的意见...
   已分析: 1399 条
   未分析: 914 条
   总计: 2313 条
   覆盖率: 60.5%

🤖 开始分析 914 条意见...
   [  10/914] ✓ | 成功:   10 | 失败:   0 | 速率: 5.2/min | 剩余: 2m 52s
   [  20/914] ✓ | 成功:   20 | 失败:   0 | 速率: 5.4/min | 剩余: 2m 45s
   ...
```

### 步骤4: 等待完成
脚本会自动:
- ✓ 分析所有缺失的记录
- ✓ 合并到现有数据
- ✓ 保存到 analysis_results.json
- ✓ 推送到 GitHub
- ✓ 触发 Streamlit 自动部署

---

## 预期结果

### 时间
- 分析 900 条: 约 **15-20 分钟**
- 上传到 GitHub: 约 **1-2 分钟**
- Streamlit 重新部署: 约 **3-5 分钟**
- **总耗时: 20-30 分钟**

### 数据更新
```json
{
  "total": 2313,
  "model": "glm-4-flash",
  "api_key_prefix": "91cff4bec1",
  "last_updated": "2025-12-11T14:30:45.123456",
  "data": [
    // 现在包含所有2313条记录的分析结果
  ]
}
```

### 网站变化
访问 https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/
- 总记录数: 1,399 → 2,313
- 覆盖率: 60.5% → 99.9%
- 所有图表数据重新计算

---

## 常见问题

### Q1: 分析被中断怎么办？
**A:** 重新运行脚本，它会自动检查已分析的部分，只分析缺失的。

### Q2: API限速报错
**A:** 脚本已内置每50条休息3秒的限速，如果仍然超限：
```bash
# 修改analyze_missing_900.py的第170行
if idx % 50 == 0:
    time.sleep(5)  # 改为5秒
```

### Q3: 网络中断
**A:** 脚本具有重试机制，会自动重试3次。如果仍失败，等待网络恢复后重新运行。

### Q4: 推送到GitHub失败
**A:** 可能是网络问题。尝试：
```bash
# 手动推送
git add data/analysis/analysis_results.json
git commit -m "Manual: 分析缺失的900条记录"
git push origin main
```

---

## 后续步骤

### 1. 验证数据完整性
```bash
python check_progress.py
```

### 2. 设置定期更新（可选）
见 `SCHEDULE_TASKS.md`
- Windows: 任务计划程序
- Linux/Mac: cron 任务

### 3. 备份（可选）
```bash
git tag -a "v1.0-complete-2313-records" -m "All 2313 records analyzed"
git push origin v1.0-complete-2313-records
```

---

## 技术细节

### 数据匹配逻辑
- **来源**: `opinions_clean_5000.json` 中的 `content` 字段
- **已分析**: `analysis_results.json` 中的 `source_text` 字段
- **匹配方式**: 完全文本匹配

### API调用参数
```python
{
    "model": "glm-4-flash",
    "temperature": 0.3,      # 降低随机性
    "top_p": 0.8,            # 增加多样性
    "5维度分析": [
        "sentiment (正/中/负)",
        "topic (税收/价格/合规/风险/倡议/其他)",
        "pattern (跨境电商模式)",
        "risk_level (严重/高/中/低)",
        "actor (企业/消费者/政府/卖家/大众)"
    ]
}
```

### 重试机制
- 失败自动重试 3 次
- 每次重试间隔 2 秒
- JSON 解析失败返回 None

---

## 成功标志

✅ 脚本完成后，检查:
1. 控制台显示 "✨ 数据已更新！"
2. `data/analysis/analysis_results.json` 文件大小增加
3. GitHub commit 记录出现新提交
4. Streamlit 网站在 3-5 分钟后显示新数据

---

## 获取帮助

- **脚本错误**: 查看控制台输出的错误消息
- **API问题**: 检查 Zhipu API 余额和密钥
- **网络问题**: 使用移动热点或检查代理设置
- **数据问题**: 查看 `logs/` 目录的日志文件

---

**开始时间**: [运行脚本时自动记录]
**预期完成**: 20-30分钟后
**验证方式**: 访问网站或检查 analysis_results.json 的 last_updated 时间戳
