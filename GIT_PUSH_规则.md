# Git 推送规则文档

**最后更新**: 2025-12-11  
**项目**: 跨境电商税收政策舆论可视化系统  
**仓库**: https://github.com/RYlink6666/tax-opinion-dashboard

---

## 📋 快速参考

### 日常推送（推荐）

```bash
# 方式1：使用自动脚本（最简单）
double-click push.bat

# 方式2：命令行
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品
git push origin main
```

### 必需配置（一次性）

已配置完成：
- ✅ `credential.helper = wincred`（Windows凭证管理器）
- ✅ `remote origin = https://github.com/RYlink6666/tax-opinion-dashboard.git`（纯HTTPS）
- ✅ `backup_2b7195e.bundle`（备份已创建）

---

## 🔄 标准推送流程

### 步骤1：查看修改状态
```bash
cd f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品
git status
```

预期输出：
```
On branch main
Your branch is ahead of 'origin/main' by X commit(s).
  (use "git push" to publish your local commits)

Changes not staged for commit:
  modified: streamlit_app/...
  ...
```

### 步骤2：暂存修改（如果有未提交的文件）
```bash
# 暂存所有修改
git add .

# 或只暂存特定文件
git add streamlit_app/utils/data_loader.py
```

### 步骤3：创建提交
```bash
git commit -m "简洁的修改描述"
```

**提交信息规范**：
- ✅ `Fix compound label translation`
- ✅ `Add Risk Analysis page`
- ✅ `Update data loading function`
- ❌ `update`（太模糊）
- ❌ `fixes bug and adds feature`（一次做太多）

### 步骤4：推送到GitHub
```bash
git push origin main
```

---

## ✅ 推送成功的标志

### 命令行输出（成功）
```
To https://github.com/RYlink6666/tax-opinion-dashboard.git
   70bcbf0..2b7195e  main -> main
```

### 验证方法
```bash
# 查看最新提交
git log --oneline -1
# 应该显示你刚才的commit

# 查看远程同步状态
git log origin/main --oneline -1
# 应该与本地一致
```

### GitHub网页验证
1. 打开 https://github.com/RYlink6666/tax-opinion-dashboard
2. 查看 **Commits** 标签
3. 应该看到最新的提交消息和时间戳

---

## ❌ 常见问题与解决

### 问题1：`fatal: Authentication failed`

**原因**：凭证过期或不正确

**解决**：
```bash
# 方法1：删除旧凭证，重新保存
# 控制面板 → 凭证管理器 → Windows凭证 → 删除github.com条目
# 然后运行：
git push origin main
# 输入用户名和密码，选择保存

# 方法2：检查凭证配置
git config --global credential.helper
# 应该输出：wincred
```

### 问题2：`remote: Invalid username or token`

**原因**：Remote URL包含无效token

**解决**：
```bash
# 检查remote URL
git remote -v
# 应该是：https://github.com/RYlink6666/tax-opinion-dashboard.git
# 不应该包含 token 或 @

# 修复
git remote set-url origin https://github.com/RYlink6666/tax-opinion-dashboard.git
```

### 问题3：`fatal: unable to access ... port 443 timeout`

**原因**：网络无法连接GitHub（HTTPS 443端口）

**解决**：
```bash
# 方法1：检查网络
ping github.com

# 方法2：试试用手机热点或VPN

# 方法3：用Git备份（网络恢复后恢复）
git bundle create backup_latest.bundle main
```

### 问题4：`Your branch is ahead of 'origin/main' by X commits`

**原因**：本地有未推送的提交

**解决**：
```bash
# 查看未推送的提交
git log origin/main..HEAD --oneline

# 推送到GitHub
git push origin main
```

---

## 🎯 最佳实践

### ✅ DO（应该做）

| 操作 | 说明 |
|------|------|
| 每次修改后立即推送 | 避免丢失代码 |
| 提交前查看diff | `git diff` 确认修改内容 |
| 使用清晰的提交信息 | 便于日后追溯 |
| 定期检查remote状态 | `git log origin/main -1` |
| 推送前备份重要代码 | 虽然GitHub有版本控制 |

### ❌ DON'T（不应该做）

| 操作 | 原因 |
|------|------|
| 不检查status就push | 可能遗漏文件 |
| 强制推送 (`git push -f`) | 会覆盖远程历史 |
| 在token中混入URL | 安全风险 |
| 提交密码或敏感信息 | 被推到GitHub后永久存在 |
| 修改已推送的提交 | 会导致版本混乱 |

---

## 🔐 安全注意事项

### 凭证保护
- ✅ 凭证存储在Windows凭证管理器（本地加密）
- ❌ 不要在命令行或配置文件中暴露token

### 代码安全
- ✅ `.gitignore` 会忽略敏感文件
- ❌ 不要推送API key、密码、敏感数据

### 已保存的凭证
```bash
# 查看凭证列表
cmdkey /list

# 删除特定凭证
cmdkey /delete:github.com
```

---

## 📊 推送历史参考

| 提交 | 日期 | 内容 |
|------|------|------|
| 2b7195e | 2025-12-11 | Fix compound label translation |
| 70bcbf0 | 2025-12-11 | Add Chinese translation for labels |
| 176ddc8 | 2025-12-10 | Add Policy Recommendations page |
| 7fe0853 | 2025-12-10 | Add 3 analysis pages (Risk/Pattern/Actor) |
| 6a9f8df | 2025-12-10 | Phase 3: Streamlit visualization |

---

## 🚀 自动推送脚本

### push.bat（Windows）

位置: `f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品\push.bat`

使用方法：
1. 做完修改后，保存文件
2. 双击 `push.bat`
3. 脚本会自动：
   - 显示当前修改
   - 执行 `git push origin main`
   - 显示推送结果和最新commit

---

## 📞 联系与支持

### 如果推送一直失败
1. 检查网络连接
2. 验证凭证管理器中的github.com凭证
3. 查看 `git remote -v` 确保URL正确
4. 查看本文件的故障排查部分

### 保存备份
```bash
# 创建本地备份
git bundle create backup_$(date +%Y%m%d).bundle main

# 备份存放位置：项目根目录
```

---

## ✨ 规则总结

| 规则 | 优先级 |
|------|--------|
| 修改后立即`git add .` | 🔴 高 |
| 提交前写清楚commit message | 🔴 高 |
| 每个commit后执行`git push` | 🔴 高 |
| 定期检查remote同步状态 | 🟡 中 |
| 做重要修改前创建备份 | 🟡 中 |
| 月度检查凭证有效性 | 🟢 低 |

---

**记住**：最简单的方式就是**修改 → add → commit → push**，重复这个流程即可。

**有问题？用 `git status` 查看状态，那是你最好的朋友。**
