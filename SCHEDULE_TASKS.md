# 自动更新定时任务设置指南

**目的**: 让数据分析脚本定期自动运行，无需手动执行

---

## 🪟 Windows 任务计划（推荐）

### 步骤1：配置API密钥（一次性）

1. 打开**控制面板** → **系统和安全** → **系统** → **高级系统设置**
2. 点击**环境变量**按钮
3. 在"系统变量"中点击**新建**
   - 变量名：`ZHIPU_API_KEY`
   - 变量值：`你的API密钥`
4. 点击**确定**保存

### 步骤2：创建定时任务

#### 方式A：图形界面（简单）

1. 按 `Win + R`，输入 `taskschd.msc`，按Enter打开任务计划程序
2. 在左侧点击**创建基本任务**
3. 填写信息：
   - **名称**: `自动分析舆论数据`
   - **描述**: `每周一次自动分析跨境电商舆论数据`
4. **触发器**选项卡：
   - 选择**按周期**
   - 频率：**每周**
   - 星期：选择**星期一**（或你喜欢的日期）
   - 时间：**上午10:00**（选择一个合适时间）
5. **操作**选项卡：
   - 程序或脚本：`f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品\auto_analyze.bat`
   - 起始于：`f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品`
6. **条件**选项卡（可选）：
   - 勾选**计算机使用电源时运行**
7. 完成创建

#### 方式B：PowerShell 脚本（自动）

以管理员身份运行PowerShell，执行以下命令：

```powershell
$TaskName = "自动分析舆论数据"
$ScriptPath = "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品\auto_analyze.bat"
$WorkingDir = "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"

# 创建触发器（每周一上午10:00）
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 10:00am

# 创建操作
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDir

# 创建任务
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -RunLevel Highest -Force

Write-Host "✓ 任务已创建！"
Write-Host "任务名称: $TaskName"
Write-Host "执行时间: 每周一 上午10:00"
```

### 步骤3：验证任务

```powershell
# 查看任务
Get-ScheduledTask -TaskName "自动分析舆论数据"

# 查看任务的执行历史
Get-ScheduledTaskInfo -TaskName "自动分析舆论数据"
```

---

## 🐧 Linux / macOS （使用cron）

### 步骤1：编辑crontab

```bash
crontab -e
```

### 步骤2：添加定时任务

选择一种频率（任选其一）：

**每周一上午10点**
```
0 10 * * 1 cd /path/to/project && python auto_analyze.py >> auto_analyze.log 2>&1
```

**每天下午6点**
```
0 18 * * * cd /path/to/project && python auto_analyze.py >> auto_analyze.log 2>&1
```

**每个工作日（周一-周五）**
```
0 10 * * 1-5 cd /path/to/project && python auto_analyze.py >> auto_analyze.log 2>&1
```

### 步骤3：设置API密钥

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export ZHIPU_API_KEY="your_api_key_here"
```

然后运行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

---

## 🧪 手动测试

在设置定时任务之前，先手动测试一下：

### Windows
```cmd
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品
auto_analyze.bat
```

### Linux/Mac
```bash
cd /path/to/project
python auto_analyze.py
```

---

## 📊 监控和调试

### 查看执行日志

日志保存在同目录的 `auto_analyze.log` 中：

```bash
# Windows (PowerShell)
Get-Content auto_analyze.log -Tail 50

# Linux/Mac
tail -50 auto_analyze.log
```

### 常见问题

#### 问题1：任务没有执行
- ✅ 检查电脑是否在计划时间开机
- ✅ 检查账户权限（需要管理员权限）
- ✅ 查看日志文件看是否有错误

#### 问题2：Python找不到
- ✅ 确保Python安装在系统PATH中
- ✅ 在脚本中使用完整路径：`C:\Python\python.exe auto_analyze.py`

#### 问题3：ZHIPU_API_KEY不被识别
- ✅ 设置后重启电脑
- ✅ 确认环境变量拼写正确
- ✅ 用 `echo %ZHIPU_API_KEY%` (Windows) 或 `echo $ZHIPU_API_KEY` (Linux/Mac) 验证

#### 问题4：权限被拒绝
- ✅ 任务需要以管理员身份运行
- ✅ 项目文件夹需要写入权限

---

## 🚀 建议的更新频率

| 频率 | 适用场景 | API成本 |
|------|--------|--------|
| **每天** | 快速迭代、测试 | 高 |
| **每周** | 常规监测（推荐） | 中 |
| **每月** | 长期追踪趋势 | 低 |
| **手动** | 需要时运行 | 最低 |

**建议**：从**每周一次**开始，根据成本和需求调整

---

## 💰 成本估算

基于Zhipu API的价格（约¥0.0005/token）：

| 更新频率 | 新增数据 | 月度成本 |
|--------|--------|--------|
| 每周 | ~200-300条 | ¥20-40 |
| 每月 | ~500-1000条 | ¥40-80 |

---

## 📞 支持

如有问题，查看：
- 脚本日志：`auto_analyze.log`
- Git提交历史：`git log --oneline`
- Streamlit部署日志：Streamlit Cloud的管理后台

---

**设置完成后，数据将自动保持最新！** 🎉
