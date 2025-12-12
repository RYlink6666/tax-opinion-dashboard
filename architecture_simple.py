"""
简化版系统架构图 - 只需matplotlib
无需额外依赖，直接可用
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.patheffects as path_effects

# 设置字体（Windows通常内置SimHei）
try:
    plt.rcParams['font.sans-serif'] = ['SimHei']
except:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False

# 创建图
fig = plt.figure(figsize=(14, 10), dpi=100)
ax = fig.add_subplot(111)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# ==================== 颜色方案 ====================
colors = {
    'app': '#E8F4F8',      # 应用层 - 浅蓝
    'analysis': '#FFF4E6', # 分析层 - 浅橙
    'lang': '#FFE8E8',     # LangExtract - 浅红
    'bert': '#E8F8E8',     # BERTopic - 浅绿
    'data': '#F0F0F0',     # 数据层 - 浅灰
}

# ==================== 第一层：应用层 ====================
app_box = FancyBboxPatch(
    (0.5, 7.5), 9, 1.5,
    boxstyle="round,pad=0.1",
    edgecolor='#0066CC', facecolor=colors['app'],
    linewidth=3, zorder=1
)
ax.add_patch(app_box)

# 应用层文字
ax.text(5, 8.5, '【应用层】可视化展示',
       fontsize=13, fontweight='bold', ha='center', va='center', zorder=2)
ax.text(5, 8.05, 'Streamlit Web应用 | 9个分析页面 | 交互式仪表板',
       fontsize=10, ha='center', va='center', style='italic', zorder=2)
ax.text(5, 7.65, '(展示LangExtract和BERTopic的所有分析输出)',
       fontsize=9, ha='center', va='center', color='#555555', zorder=2)

# ==================== 第二层：分析层 ====================
# 分析层背景
analysis_bg = FancyBboxPatch(
    (0.5, 3.5), 9, 3.5,
    boxstyle="round,pad=0.1",
    edgecolor='#CC6600', facecolor=colors['analysis'],
    linewidth=3, zorder=1
)
ax.add_patch(analysis_bg)

# 分析层标题
ax.text(5, 6.8, '【分析层】AI智能分析 + 主题建模双引擎',
       fontsize=13, fontweight='bold', ha='center', va='center',
       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, pad=0.3),
       zorder=3)

# -------- LangExtract框 --------
lang_box = FancyBboxPatch(
    (0.8, 4.2), 4.1, 2.3,
    boxstyle="round,pad=0.08",
    edgecolor='#CC0000', facecolor=colors['lang'],
    linewidth=2, zorder=2
)
ax.add_patch(lang_box)

ax.text(2.95, 6.2, '【上游：LangExtract】',
       fontsize=10, fontweight='bold', ha='center', color='#CC0000', zorder=3)
ax.text(2.95, 5.9, '(Google 2023)',
       fontsize=8, ha='center', style='italic', color='#666666', zorder=3)

lang_text = [
    '✓ 5维度结构化分类',
    '✓ 提示工程+Few-shot',
    '✓ 精度 88.5%',
    '✓ JSON结构化输出'
]
y_pos = 5.55
for text in lang_text:
    ax.text(2.95, y_pos, text, fontsize=8.5, ha='center', va='center', zorder=3)
    y_pos -= 0.3

# -------- BERTopic框 --------
bert_box = FancyBboxPatch(
    (5.1, 4.2), 4.1, 2.3,
    boxstyle="round,pad=0.08",
    edgecolor='#009900', facecolor=colors['bert'],
    linewidth=2, zorder=2
)
ax.add_patch(bert_box)

ax.text(7.15, 6.2, '【下游：BERTopic】',
       fontsize=10, fontweight='bold', ha='center', color='#009900', zorder=3)
ax.text(7.15, 5.9, '(荷兰开源 2022)',
       fontsize=8, ha='center', style='italic', color='#666666', zorder=3)

bert_text = [
    '✓ 无监督主题发现',
    '✓ BERT向量 + HDBSCAN',
    '✓ 18个自动聚类话题',
    '✓ 8个交互式可视化'
]
y_pos = 5.55
for text in bert_text:
    ax.text(7.15, y_pos, text, fontsize=8.5, ha='center', va='center', zorder=3)
    y_pos -= 0.3

# -------- 两框架协同箭头 --------
arrow_sync = FancyArrowPatch(
    (4.9, 5.3), (5.1, 5.3),
    arrowstyle='<->', mutation_scale=15,
    linewidth=1.5, color='#666666', linestyle='--', zorder=2
)
ax.add_patch(arrow_sync)
ax.text(5, 5.0, '协同应用', fontsize=8, ha='center',
       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, pad=0.2),
       zorder=3)

# ==================== 第三层：数据层 ====================
data_box = FancyBboxPatch(
    (0.5, 1.5), 9, 1.7,
    boxstyle="round,pad=0.1",
    edgecolor='#666666', facecolor=colors['data'],
    linewidth=3, zorder=1
)
ax.add_patch(data_box)

ax.text(5, 2.9, '【数据层】采集与清洁',
       fontsize=13, fontweight='bold', ha='center', va='center', zorder=2)
ax.text(5, 2.45, 'MediaCrawler(3平台) | 99.3%去重率 | 2,297条清洁数据',
       fontsize=10, ha='center', va='center', zorder=2)
ax.text(5, 2.0, '微博×1,200条 + 知乎×900条 + 小红书×200条',
       fontsize=9, ha='center', va='center', color='#555555', zorder=2)
ax.text(5, 1.65, '时间跨度：6个月（2025年6月-12月）',
       fontsize=8, ha='center', va='center', color='#888888', style='italic', zorder=2)

# ==================== 数据流箭头 ====================
# 应用层 ← 分析层
arrow1 = FancyArrowPatch(
    (5, 7.5), (5, 7.0),
    arrowstyle='->', mutation_scale=25,
    linewidth=2.5, color='#0066CC', zorder=2
)
ax.add_patch(arrow1)

# 分析层 ← 数据层
arrow2 = FancyArrowPatch(
    (5, 4.2), (5, 3.2),
    arrowstyle='->', mutation_scale=25,
    linewidth=2.5, color='#CC6600', zorder=2
)
ax.add_patch(arrow2)

# ==================== 底部说明 ====================
info_text = (
    '系统设计理念 | System Design Philosophy\n'
    '═════════════════════════════════════════════\n'
    '项目线（Project）：数据采集 → LLM分析 → 可视化展示 → 政策启示\n'
    '技术线（Technology）：MediaCrawler → LangExtract+BERTopic → Streamlit → 决策支持\n\n'
    '核心创新点：\n'
    '  ① LangExtract框架 - Google提示工程方案，零样本快速部署\n'
    '  ② BERTopic框架 - 荷兰开源无监督主题建模，自动发现话题\n'
    '  ③ 协同应用 - 有监督分类 + 无监督发现 = 360°舆论理解'
)

ax.text(5, 0.7, info_text,
       fontsize=8, ha='center', va='top',
       family='monospace',
       bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFFACD',
                edgecolor='#FFD700', linewidth=1.5, alpha=0.95),
       zorder=3)

# ==================== 标题 ====================
fig.text(0.5, 0.96, '跨境电商舆论分析平台 - 系统架构',
        fontsize=16, fontweight='bold', ha='center')
fig.text(0.5, 0.925, 'Cross-border E-commerce Opinion Analysis Platform - System Architecture',
        fontsize=11, ha='center', style='italic', color='#666666')

# ==================== 保存 ====================
plt.tight_layout(rect=[0, 0, 1, 0.92])

# 保存为PNG
plt.savefig('系统架构图.png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("✅ PNG已生成：系统架构图.png (300dpi, 高质量)")

# 保存为PDF
try:
    plt.savefig('系统架构图.pdf', bbox_inches='tight', facecolor='white', edgecolor='none')
    print("✅ PDF已生成：系统架构图.pdf (矢量格式)")
except:
    print("⚠️  PDF生成失败（可选）")

# 显示
plt.show()

print("\n" + "="*60)
print("📊 系统架构图绘制完成！")
print("="*60)
print("✅ 输出文件：")
print("   • 系统架构图.png - 高分辨率PNG（可用于报告）")
print("   • 系统架构图.pdf - 矢量PDF（可编辑）")
print("\n💡 用途：")
print("   • 插入到项目汇报文档")
print("   • 投影演讲展示")
print("   • 学术论文图表")
print("="*60)
