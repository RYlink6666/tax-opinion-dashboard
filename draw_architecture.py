"""
绘制系统架构图 - 三层架构 + 两大框架
输出格式：PNG / PDF / SVG
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def draw_architecture():
    """绘制系统架构图"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 颜色定义
    color_app = '#E8F4F8'      # 应用层 - 浅蓝
    color_analysis = '#FFF4E6' # 分析层 - 浅橙
    color_data = '#F0F0F0'     # 数据层 - 浅灰
    color_lang = '#FFE8E8'     # LangExtract - 浅红
    color_bert = '#E8F8E8'     # BERTopic - 浅绿
    
    # ==================== 第一层：应用层 ====================
    app_box = FancyBboxPatch((0.5, 7.5), 9, 1.5, 
                            boxstyle="round,pad=0.1", 
                            edgecolor='#0066CC', facecolor=color_app,
                            linewidth=2.5)
    ax.add_patch(app_box)
    
    ax.text(5, 8.5, '【应用层】可视化展示', 
           fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(5, 8.05, 'Streamlit Web应用 | 9个分析页面 | 交互式仪表板', 
           fontsize=11, ha='center', va='center', style='italic')
    ax.text(5, 7.65, '(展示LangExtract和BERTopic的所有分析输出)', 
           fontsize=10, ha='center', va='center', color='#666666')
    
    # ==================== 第二层：分析层 ====================
    analysis_box = FancyBboxPatch((0.5, 3.5), 9, 3.5, 
                                 boxstyle="round,pad=0.1", 
                                 edgecolor='#CC6600', facecolor=color_analysis,
                                 linewidth=2.5)
    ax.add_patch(analysis_box)
    
    ax.text(5, 6.8, '【分析层】AI智能分析 + 主题建模双引擎', 
           fontsize=14, fontweight='bold', ha='center', va='center')
    
    # 左框：LangExtract
    lang_box = FancyBboxPatch((0.8, 4.2), 4.1, 2.3, 
                             boxstyle="round,pad=0.08", 
                             edgecolor='#CC0000', facecolor=color_lang,
                             linewidth=2)
    ax.add_patch(lang_box)
    
    ax.text(2.95, 6.2, '【上游：LangExtract框架】', 
           fontsize=11, fontweight='bold', ha='center', color='#CC0000')
    ax.text(2.95, 5.85, '(Google 2023)', 
           fontsize=9, ha='center', style='italic', color='#666666')
    
    ax.text(2.95, 5.55, '✓ 5维度结构化文本分类', 
           fontsize=9, ha='center', va='center')
    ax.text(2.95, 5.25, '✓ 提示工程+Few-shot', 
           fontsize=9, ha='center', va='center')
    ax.text(2.95, 4.95, '  精度88.5%', 
           fontsize=9, ha='center', va='center')
    ax.text(2.95, 4.65, '✓ 输出：JSON', 
           fontsize=9, ha='center', va='center')
    ax.text(2.95, 4.35, '  {sentiment,pattern,risk,...}', 
           fontsize=8, ha='center', va='center', family='monospace')
    
    # 右框：BERTopic
    bert_box = FancyBboxPatch((5.1, 4.2), 4.1, 2.3, 
                             boxstyle="round,pad=0.08", 
                             edgecolor='#009900', facecolor=color_bert,
                             linewidth=2)
    ax.add_patch(bert_box)
    
    ax.text(7.15, 6.2, '【下游：BERTopic框架】', 
           fontsize=11, fontweight='bold', ha='center', color='#009900')
    ax.text(7.15, 5.85, '(荷兰开源 2022)', 
           fontsize=9, ha='center', style='italic', color='#666666')
    
    ax.text(7.15, 5.55, '✓ 无监督主题自动发现', 
           fontsize=9, ha='center', va='center')
    ax.text(7.15, 5.25, '✓ BERT向量+HDBSCAN', 
           fontsize=9, ha='center', va='center')
    ax.text(7.15, 4.95, '  聚类，18个话题', 
           fontsize=9, ha='center', va='center')
    ax.text(7.15, 4.65, '✓ 8个交互式可视化', 
           fontsize=9, ha='center', va='center')
    ax.text(7.15, 4.35, '  功能', 
           fontsize=9, ha='center', va='center')
    
    # ==================== 第三层：数据层 ====================
    data_box = FancyBboxPatch((0.5, 1.5), 9, 1.7, 
                             boxstyle="round,pad=0.1", 
                             edgecolor='#666666', facecolor=color_data,
                             linewidth=2.5)
    ax.add_patch(data_box)
    
    ax.text(5, 2.85, '【数据层】采集与清洁', 
           fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(5, 2.4, 'MediaCrawler(3平台) | 数据去重99.3% | 2,297条最终数据', 
           fontsize=11, ha='center', va='center')
    ax.text(5, 1.9, '微博×1200条 + 知乎×900条 + 小红书×200条 | 时间跨度6个月', 
           fontsize=10, ha='center', va='center', color='#666666', style='italic')
    
    # ==================== 数据流箭头 ====================
    # 应用层 → 分析层
    arrow1 = FancyArrowPatch((5, 7.5), (5, 7.0),
                            arrowstyle='->', mutation_scale=30, 
                            linewidth=2.5, color='#0066CC')
    ax.add_patch(arrow1)
    
    # 分析层 → 数据层
    arrow2 = FancyArrowPatch((5, 4.2), (5, 3.2),
                            arrowstyle='->', mutation_scale=30, 
                            linewidth=2.5, color='#CC6600')
    ax.add_patch(arrow2)
    
    # LangExtract ↔ BERTopic 双向箭头（展示协同）
    arrow_lr = FancyArrowPatch((4.9, 5.3), (5.1, 5.3),
                              arrowstyle='<->', mutation_scale=20, 
                              linewidth=1.5, color='#666666', linestyle='--')
    ax.add_patch(arrow_lr)
    
    ax.text(5, 5.0, '协同应用', fontsize=9, ha='center', 
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ==================== 底部技术说明 ====================
    tech_text = (
        '核心创新：\n'
        '① LangExtract框架 - Google的提示工程方案，实现零样本快速部署\n'
        '② BERTopic框架 - 荷兰开源的无监督主题建模，自动发现话题\n'
        '③ 两框架协同 - 有监督分类 + 无监督发现 = 360度舆论理解'
    )
    
    ax.text(5, 0.6, tech_text, 
           fontsize=9, ha='center', va='top',
           bbox=dict(boxstyle='round', facecolor='#FFFACD', 
                    edgecolor='#FFD700', linewidth=1.5, alpha=0.9),
           family='monospace')
    
    # ==================== 标题 ====================
    fig.suptitle('跨境电商舆论分析平台 - 系统架构', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # 保存为多种格式
    plt.savefig('系统架构图.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✅ PNG图已保存：系统架构图.png")
    
    plt.savefig('系统架构图.pdf', bbox_inches='tight', facecolor='white')
    print("✅ PDF图已保存：系统架构图.pdf")
    
    plt.savefig('系统架构图.svg', bbox_inches='tight', facecolor='white')
    print("✅ SVG图已保存：系统架构图.svg")
    
    plt.show()

if __name__ == "__main__":
    draw_architecture()
    print("\n📊 系统架构图绘制完成！")
    print("   - 系统架构图.png (高分辨率PNG)")
    print("   - 系统架构图.pdf (矢量PDF)")
    print("   - 系统架构图.svg (矢量SVG)")
