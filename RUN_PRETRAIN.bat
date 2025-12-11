@echo off
chcp 65001 > nul

echo.
echo ========================================
echo  🚀 BERTopic 离线预训练
echo ========================================
echo.

cd /d "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"

echo 这会花费 3-5 分钟，请耐心等待...
echo.

python pretrain_bertopic.py

echo.
echo ========================================
echo  完成后请执行:
echo  git push origin main
echo ========================================
echo.

pause
