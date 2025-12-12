#!/bin/bash
cd "f:/研究生经济学/税收经济学科研/最优税收理论/电商舆论数据产品"

echo "=========================================="
echo "  BERTopic 修复推送"
echo "=========================================="
echo ""

echo "1️⃣  查看修改状态..."
git status --short
echo ""

echo "2️⃣  暂存修改..."
git add requirements.txt streamlit_app/requirements.txt streamlit_app/utils/bertopic_analyzer.py BERTOPIC_FIX_DEPLOYMENT.md
echo "✅ 已添加 4 个文件"
echo ""

echo "3️⃣  创建提交..."
git commit -m "Fix BERTopic compatibility and topic duplication

- Upgrade bertopic 0.15.0 to 0.16.0+ (fixes scikit-learn 1.3.2 compatibility)
- Add HDBSCAN min_cluster_size=10 to prevent duplicate topics  
- Optimize UMAP clustering parameters: n_neighbors=15, n_components=5
- Auto topic number detection: nr_topics='auto'
- Resolves P7-P8 pages crash and topic duplication issue"
echo ""

echo "4️⃣  推送到 GitHub..."
git push origin main
echo ""

if [ $? -eq 0 ]; then
    echo "✅ ✅ ✅ 推送成功！"
    echo ""
    echo "最新提交："
    git log --oneline -1
    echo ""
    echo "🌐 Streamlit Cloud 会在 2-3 分钟内自动重新部署"
    echo "📱 访问: https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app"
    echo "🔥 进入 P7 页面查看话题分析是否正常"
else
    echo "❌ 推送失败"
    echo "请检查网络连接或凭证"
fi
