#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内联执行版 - 无需任何复杂设置
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# 设置字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图
fig = plt.figure(figsize=(14, 10), dpi=100)
ax = fig.add_subplot(111)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

colors = {
    'app': '#E8F4F8',
    'analysis': '#FFF4E6',
    'lang': '#FFE8E8',
    'bert': '#E8F8E8',
    'data': '#F0F0F0',
}

# 应用层
app_box = FancyBboxPatch((0.5, 7.5), 9, 1.5, boxstyle="round,pad=0.1", 
                        edgecolor='#0066CC', facecolor=colors['app'], linewidth=3, zorder=1)
ax.add_patch(app_box)
ax.text(5, 8.5, u'【应用层】可视化展示', fontsize=13, fontweight='bold', ha='center', va='center', zorder=2)
ax.text(5, 8.05, u'Streamlit Web应用 | 9个分析页面 | 交互式仪表板', fontsize=10, ha='center', va='center', style='italic', zorder=2)
ax.text(5, 7.65, u'(展示LangExtract和BERTopic的所有分析输出)', fontsize=9, ha='center', va='center', color='#555555', zorder=2)

# 分析层背景
analysis_bg = FancyBboxPatch((0.5, 3.5), 9, 3.5, boxstyle="round,pad=0.1", 
                            edgecolor='#CC6600', facecolor=colors['analysis'], linewidth=3, zorder=1)
ax.add_patch(analysis_bg)
ax.text(5, 6.8, u'【分析层】AI智能分析 + 主题建模双引擎', fontsize=13, fontweight='bold', ha='center', va='center',
       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, pad=0.3), zorder=3)

# LangExtract框
lang_box = FancyBboxPatch((0.8, 4.2), 4.1, 2.3, boxstyle="round,pad=0.08", 
                         edgecolor='#CC0000', facecolor=colors['lang'], linewidth=2, zorder=2)
ax.add_patch(lang_box)
ax.text(2.95, 6.2, u'【上游：LangExtract】', fontsize=10, fontweight='bold', ha='center', color='#CC0000', zorder=3)
ax.text(2.95, 5.9, u'(Google 2023)', fontsize=8, ha='center', style='italic', color='#666666', zorder=3)

lang_text = [u'✓ 5维度结构化分类', u'✓ 提示工程+Few-shot', u'✓ 精度 88.5%', u'✓ JSON结构化输出']
y_pos = 5.55
for text in lang_text:
    ax.text(2.95, y_pos, text, fontsize=8.5, ha='center', va='center', zorder=3)
    y_pos -= 0.3

# BERTopic框
bert_box = FancyBboxPatch((5.1, 4.2), 4.1, 2.3, boxstyle="round,pad=0.08", 
                         edgecolor='#009900', facecolor=colors['bert'], linewidth=2, zorder=2)
ax.add_patch(bert_box)
ax.text(7.15, 6.2, u'【下游：BERTopic】', fontsize=10, fontweight='bold', ha='center', color='#009900', zorder=3)
ax.text(7.15, 5.9, u'(荷兰开源 2022)', fontsize=8, ha='center', style='italic', color='#666666', zorder=3)

bert_text = [u'✓ 无监督主题发现', u'✓ BERT向量 + HDBSCAN', u'✓ 18个自动聚类话题', u'✓ 8个交互式可视化']
y_pos = 5.55
for text in bert_text:
    ax.text(7.15, y_pos, text, fontsize=8.5, ha='center', va='center', zorder=3)
    y_pos -= 0.3

# 协同箭头
arrow_sync = FancyArrowPatch((4.9, 5.3), (5.1, 5.3), arrowstyle='<->', mutation_scale=15, 
                            linewidth=1.5, color='#666666', linestyle='--', zorder=2)
ax.add_patch(arrow_sync)
ax.text(5, 5.0, u'协同应用', fontsize=8, ha='center',
       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, pad=0.2), zorder=3)

# 数据层
data_box = FancyBboxPatch((0.5, 1.5), 9, 1.7, boxstyle="round,pad=0.1", 
                         edgecolor='#666666', facecolor=colors['data'], linewidth=3, zorder=1)
ax.add_patch(data_box)
ax.text(5, 2.9, u'【数据层】采集与清洁', fontsize=13, fontweight='bold', ha='center', va='center', zorder=2)
ax.text(5, 2.45, u'MediaCrawler(3平台) | 99.3%去重率 | 2,297条清洁数据', fontsize=10, ha='center', va='center', zorder=2)
ax.text(5, 2.0, u'微博×1,200条 + 知乎×900条 + 小红书×200条', fontsize=9, ha='center', va='center', color='#555555', zorder=2)
ax.text(5, 1.65, u'时间跨度：6个月（2025年6月-12月）', fontsize=8, ha='center', va='center', color='#888888', style='italic', zorder=2)

# 箭头
arrow1 = FancyArrowPatch((5, 7.5), (5, 7.0), arrowstyle='->', mutation_scale=25, 
                        linewidth=2.5, color='#0066CC', zorder=2)
ax.add_patch(arrow1)

arrow2 = FancyArrowPatch((5, 4.2), (5, 3.2), arrowstyle='->', mutation_scale=25, 
                        linewidth=2.5, color='#CC6600', zorder=2)
ax.add_patch(arrow2)

# 底部说明
info_text = (u'系统设计理念 | System Design Philosophy\n'
            u'═════════════════════════════════════════════\n'
            u'项目线（Project）：数据采集 → LLM分析 → 可视化展示 → 政策启示\n'
            u'技术线（Technology）：MediaCrawler → LangExtract+BERTopic → Streamlit\n\n'
            u'核心创新点：\n'
            u'  ① LangExtract框架 - Google提示工程方案\n'
            u'  ② BERTopic框架 - 无监督主题建模\n'
            u'  ③ 协同应用 - 有监督+无监督 = 360°舆论理解')

ax.text(5, 0.7, info_text, fontsize=7.5, ha='center', va='top', family='monospace',
       bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFFACD', edgecolor='#FFD700', linewidth=1.5, alpha=0.95), zorder=3)

# 标题
fig.text(0.5, 0.96, u'跨境电商舆论分析平台 - 系统架构', fontsize=16, fontweight='bold', ha='center')
fig.text(0.5, 0.925, u'Cross-border E-commerce Opinion Analysis Platform', fontsize=10, ha='center', style='italic', color='#666666')

# 保存
plt.tight_layout(rect=[0, 0, 1, 0.92])

# 获取输出路径
output_dir = os.path.dirname(os.path.abspath(__file__))
png_file = os.path.join(output_dir, u'系统架构图.png')
pdf_file = os.path.join(output_dir, u'系统架构图.pdf')

plt.savefig(png_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"✅ PNG已生成：{png_file}")

try:
    plt.savefig(pdf_file, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✅ PDF已生成：{pdf_file}")
except:
    print(f"⚠️  PDF生成失败（可选）")

plt.close()

print("\n" + "="*60)
print("✅ 系统架构图绘制成功！")
print("="*60)
print(f"📁 输出位置：{output_dir}")
print("="*60)
