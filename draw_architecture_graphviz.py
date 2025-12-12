"""
用Graphviz绘制系统架构图 - 更清晰的专业风格
"""

from graphviz import Digraph
import os

def create_architecture_diagram():
    """创建系统架构diagram"""
    
    # 创建图对象
    dot = Digraph(name='系统架构', format='png', encoding='utf-8')
    dot.attr(rankdir='TB', splines='ortho')
    dot.attr('graph', bgcolor='white', pad='0.5', nodesep='0.5', ranksep='0.8')
    
    # 节点样式定义
    dot.attr('node', fontname='SimHei', shape='box', style='filled', margin='0.3,0.2')
    
    # ==================== 应用层 ====================
    dot.node('app', 
            '【应用层】可视化展示\n\nStreamlit Web应用\n9个分析页面 | 交互式仪表板',
            fillcolor='#E8F4F8', color='#0066CC', penwidth='2.5', fontsize='11')
    
    # ==================== 分析层 ====================
    # LangExtract子框
    dot.node('langextract',
            '【上游：LangExtract】\n(Google 2023)\n\n✓ 5维度结构化分类\n✓ 提示工程+Few-shot\n✓ 精度88.5%\n✓ 输出：JSON',
            fillcolor='#FFE8E8', color='#CC0000', penwidth='2', fontsize='10')
    
    # BERTopic子框
    dot.node('bertopic',
            '【下游：BERTopic】\n(荷兰开源 2022)\n\n✓ 无监督主题发现\n✓ BERT+HDBSCAN\n✓ 18个话题\n✓ 8个可视化',
            fillcolor='#E8F8E8', color='#009900', penwidth='2', fontsize='10')
    
    # 分析层容器
    dot.node('analysis', '【分析层】AI智能分析 + 主题建模双引擎',
            fillcolor='#FFF4E6', color='#CC6600', penwidth='2.5', fontsize='11', 
            shape='box', style='filled')
    
    # ==================== 数据层 ====================
    dot.node('data',
            '【数据层】采集与清洁\n\nMediaCrawler(3平台) | 99.3%去重\n微博×1200 + 知乎×900 + 小红书×200\n2,297条清洁数据 | 时间跨度6个月',
            fillcolor='#F0F0F0', color='#666666', penwidth='2.5', fontsize='11')
    
    # ==================== 箭头关系 ====================
    # 应用层 ← 分析层
    dot.edge('analysis', 'app', label='输出展示', color='#0066CC', penwidth='2.5',
            arrowsize='1.5')
    
    # LangExtract, BERTopic → 分析层
    dot.edge('langextract', 'analysis', label='5维度分类\n精度88.5%', 
            color='#CC0000', penwidth='2', arrowsize='1.5')
    dot.edge('bertopic', 'analysis', label='18个话题\n自动聚类', 
            color='#009900', penwidth='2', arrowsize='1.5')
    
    # LangExtract ↔ BERTopic 协同
    dot.edge('langextract', 'bertopic', label='协同应用', 
            color='#666666', style='dashed', penwidth='1.5', arrowtype='both')
    
    # 分析层 ← 数据层
    dot.edge('data', 'analysis', label='输入数据', 
            color='#CC6600', penwidth='2.5', arrowsize='1.5')
    
    # ==================== 输出 ====================
    # 保存为多种格式
    output_dir = '.'
    
    # PNG (最高质量)
    dot.render(os.path.join(output_dir, '系统架构图'), 
              format='png', cleanup=True, quiet=False)
    print("✅ PNG已生成：系统架构图.png")
    
    # PDF
    dot.render(os.path.join(output_dir, '系统架构图_矢量'), 
              format='pdf', cleanup=True, quiet=False)
    print("✅ PDF已生成：系统架构图_矢量.pdf")
    
    # SVG
    dot.render(os.path.join(output_dir, '系统架构图_svg'), 
              format='svg', cleanup=True, quiet=False)
    print("✅ SVG已生成：系统架构图_svg.svg")
    
    print("\n📊 系统架构图绘制完成！可用于报告展示。")

if __name__ == "__main__":
    try:
        create_architecture_diagram()
    except Exception as e:
        print(f"⚠️  错误：{e}")
        print("\n提示：如果提示Graphviz未找到，请先安装：")
        print("  Windows: pip install graphviz （需先装Graphviz软件）")
        print("  Mac: brew install graphviz")
        print("  Linux: sudo apt-get install graphviz")
