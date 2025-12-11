# Phase 3 启动指南 - Streamlit可视化仪表板

## 快速启动（3步）

### 步骤1：打开PowerShell
在项目根目录（`电商舆论数据产品`）按住 Shift + 右键，选择"在此处打开PowerShell"

### 步骤2：运行启动脚本
```powershell
.\START_STREAMLIT.ps1
```

### 步骤3：打开浏览器
自动弹出或手动访问 `http://localhost:8501`

---

## 详细说明

### 系统要求
- Python 3.9+（已检验：Python 3.11）
- 依赖包已全部安装（使用Aliyun镜像）

### 文件结构
```
电商舆论数据产品/
├── streamlit_app/
│   ├── main.py                 # 主页面
│   ├── pages/
│   │   ├── 1_Overview.py       # 详细分析页
│   │   └── 2_Search.py         # 搜索和导出页
│   ├── utils/
│   │   └── data_loader.py      # 数据加载工具
│   ├── .streamlit/
│   │   └── config.toml         # Streamlit配置
│   └── requirements.txt
├── data/
│   ├── clean/
│   │   └── opinions_clean_5000.txt
│   └── analysis/
│       └── analysis_results.json (1399条)
├── START_STREAMLIT.ps1         # 启动脚本
├── START_STREAMLIT.bat         # 备用启动脚本
└── PHASE3_START_GUIDE.md       # 本文件
```

### 应用功能概览

#### 首页 (Main Dashboard)
- **核心指标**: 总记录数、各情感占比、高风险数等
- **数据质量**: 平均置信度（0.88很高）
- **快速摘要**: 一句话总结当前数据特点

#### 详细分析页 (Overview)
1. **情感分布Pie图**
   - 中立 61.7%
   - 负面 25.8%
   - 正面 12.2%

2. **话题分布柱状图** (Top 10)
   - 其他 48.6%
   - 商业风险 15.0%
   - 税收政策 14.6%
   - ... 等

3. **风险等级分布**
   - 低风险 70.6%
   - 中风险 22.3%
   - 高风险 7.1%
   - 严重 0%

4. **参与方分布** (Top 8)
   - 消费者 38.8%
   - 企业 19.4%
   - 跨境卖家 17.8%
   - ... 等

5. **置信度统计**
   - 情感分类: 0.88
   - 话题识别: 0.86
   - 模式分析: 0.69
   - 风险评估: 0.79
   - 参与方识别: 0.83

#### 搜索和导出页 (Search & Export)
- **多条件筛选**: 情感、话题、风险等级、参与方
- **关键词搜索**: 在原文中搜索特定词汇
- **导出功能**: 
  - 导出为Excel (.xlsx)
  - 导出为CSV (.csv)
  - 可选择导出全部或筛选后的数据

---

## 常见问题

### Q1: 启动时很慢（5-10秒）
**A**: 首次启动会加载和缓存数据，属于正常。刷新页面会很快。

### Q2: 页面显示不全或乱码
**A**: 
1. 刷新浏览器 (F5)
2. 尝试不同浏览器（Chrome/Edge推荐）
3. 清除浏览器缓存

### Q3: 数据没有显示
**A**: 检查 `data/analysis/analysis_results.json` 文件是否存在且完整（838KB）

### Q4: 弹出错误信息
**A**: 提供错误截图到群里，通常是：
- 文件路径问题 → 检查工作目录
- 缺少依赖 → 重新运行 `pip install -r requirements.txt`
- JSON编码问题 → 已修复，更新最新代码

### Q5: 想关闭应用
**A**: 在PowerShell窗口按 `Ctrl+C` 即可

---

## 高级操作

### 自定义启动配置
编辑 `streamlit_app/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"      # 主题色
backgroundColor = "#ffffff"   # 背景色
secondaryBackgroundColor = "#f0f2f6"

[client]
toolbarMode = "viewer"        # 隐藏工具栏菜单
```

### 指定端口
```powershell
cd streamlit_app
streamlit run main.py --server.port 8080 --client.email=
```

### 完整的命令行参数
```bash
streamlit run main.py \
  --server.port 8501 \
  --server.address localhost \
  --logger.level error \
  --client.email=
```

---

## 数据说明

### 数据来源
- **原始数据**: 小红书关于跨境电商税收政策的舆论
- **原始数量**: 3,613条
- **清洗后**: 2,313条
- **LLM分析**: 1,399条（索引900-2299）
- **丢失数据**: 索引0-899条共900条（因API连接中断）

### 分析维度
1. **情感** (Sentiment)
   - 值: negative/neutral/positive
   - 置信度: 0.88

2. **话题** (Topic)
   - 值: tax_policy / business_risk / price_impact / compliance / other
   - 置信度: 0.86

3. **风险等级** (Risk Level)
   - 值: low / medium / high / critical
   - 置信度: 0.79

4. **参与方** (Actor)
   - 值: consumer / enterprise / cross_border_seller / general_public / ...
   - 置信度: 0.83

5. **模式** (Pattern)
   - 值: 各种识别的舆论模式
   - 置信度: 0.69

### 数据质量评估
- **样本量**: 1,399（代表性有限，建议补全)
- **置信度**: 平均0.83（很高）
- **缺陷**: 
  - ❌ 缺少0-899索引数据
  - ⚠️ 总数不足完整2,313
  - ✓ 已有数据质量很好

---

## 后续改进计划

### 立即（本周）
- [ ] 验证所有交互功能正常
- [ ] 测试导出功能
- [ ] 检查图表显示质量

### 本月
- [ ] 补全缺失的0-899条数据分析
- [ ] 重新运行LLM获得完整1,399+900=2,299条
- [ ] 添加第3、4、5个分析页面
  - 3_Risk_Analysis.py
  - 4_Pattern_Analysis.py  
  - 5_Actor_Timeline.py

### 本季度
- [ ] 部署到Streamlit Cloud（免费）
- [ ] 添加实时数据更新功能
- [ ] 集成中文NLP文本处理
- [ ] 生成定期报告（PDF）

---

## 技术栈

- **框架**: Streamlit 1.52.1
- **数据处理**: pandas 2.3.3, numpy 2.3.5
- **可视化**: plotly 6.5.0
- **数据格式**: JSON, Excel
- **编码**: UTF-8

---

## 联系和支持

如有问题：
1. 检查本文档常见问题部分
2. 查看 `PHASE3_VERIFICATION.md` 验证报告
3. 提供错误信息截图

**最后更新**: 2025-12-11 14:22
**状态**: Ready for Testing ✓
