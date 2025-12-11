"""
互动分析工具页面 - Phase 4 可解释性功能
BERTopic F101-F103: 单文档分析、Token级分析、离群值处理
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic
)
from utils.bertopic_analyzer import (
    train_bertopic,
    visualize_distribution,
    visualize_approximate_distribution,
    reduce_outliers,
    get_topics_summary,
    set_topic_labels,
    visualize_barchart_comparison,
    search_topics,
    BERTOPIC_AVAILABLE
)

st.set_page_config(page_title="互动分析工具", page_icon="🔮", layout="wide")

st.title("🔮 互动分析工具 (Phase 4)")
st.write("使用BERTopic的高级交互功能，深入理解AI的决策过程")

if not BERTOPIC_AVAILABLE:
    st.error("⚠️ BERTopic未安装，无法使用互动分析工具")
    st.stop()

def load_data():
    return load_analysis_data()

df = load_data()

# 训练模型（缓存结果以加速）
with st.spinner("🤖 初始化BERTopic模型..."):
    texts = df['source_text'].tolist()
    topics, probs, model = train_bertopic(texts)

if model is None or topics is None:
    st.error("❌ 模型训练失败")
    st.stop()

st.success(f"✅ 模型训练完成！发现{len(np.unique(topics))-1}个隐藏主题")

st.markdown("---")

# 创建6个Tab
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📄 单文档主题分析",
    "🔤 Token级词分析",
    "🧹 离群值处理",
    "🏷️ 自定义标签",
    "📊 词权重对比",
    "🔍 关键词搜索"
])

# ============================================================================
# Tab 1: 单文档主题概率分布 (F101)
# ============================================================================
with tab1:
    st.subheader("📄 单文档主题概率分布分析 (F101)")
    st.write("选择一条意见，查看AI如何分配各主题概率，理解模型的决策过程")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 文档选择
        doc_selector = st.slider(
            "选择文档",
            0, len(df) - 1, 0,
            help="滑动选择要分析的文档索引"
        )
    
    with col2:
        st.metric("当前文档", f"#{doc_selector}")
    
    st.markdown("---")
    
    # 显示文档内容
    selected_doc = df.iloc[doc_selector]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**原文内容**:")
        st.markdown(f"> {selected_doc['source_text']}")
    
    with col2:
        st.write("**文档属性**:")
        st.write(f"情感: {translate_sentiment(selected_doc['sentiment'])}")
        st.write(f"风险: {translate_risk(selected_doc['risk_level'])}")
        st.write(f"话题: {translate_topic(selected_doc['topic'])}")
    
    st.markdown("---")
    
    # 生成概率分布可视化
    st.write("**主题概率分布**:")
    st.write("下图展示该文档属于各主题的置信度（仅显示>1.5%的主题）")
    
    min_prob = st.slider("最小概率阈值", 0.0, 0.1, 0.015, 0.005, key="f101_prob")
    
    viz = visualize_distribution(model, doc_selector, min_probability=min_prob)
    if viz:
        st.plotly_chart(viz, use_container_width=True)
    else:
        st.warning("⚠️ 无法生成可视化（模型可能未启用calculate_probabilities=True）")
    
    st.markdown("---")
    
    st.info("""
    💡 **如何理解这个图**:
    - X轴: 文档可能属于的各个主题
    - Y轴: 概率（0-1）
    - 柱子高度越高，说明模型越确信该文档属于该主题
    - 概率分散 = 文档涉及多个主题；概率集中 = 文档主题明确
    
    **可解释性价值**:
    ✓ 理解模型对单条意见的判断信心
    ✓ 识别多主题文档（概率分散的情况）
    ✓ 调试模型置信度，发现异常分类
    """)

# ============================================================================
# Tab 2: Token级主题分析 (F102)
# ============================================================================
with tab2:
    st.subheader("🔤 Token级词主题分析 (F102)")
    st.write("精确到单词级别，看哪些关键词触发了哪个主题")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        doc_selector2 = st.slider(
            "选择文档进行词级分析",
            0, len(df) - 1, 0,
            help="选择要分析的文档",
            key="f102_doc"
        )
    
    with col2:
        st.metric("当前文档", f"#{doc_selector2}")
    
    st.markdown("---")
    
    # 显示文档内容
    selected_doc2 = df.iloc[doc_selector2]
    
    st.write("**待分析文档**:")
    st.markdown(f"> {selected_doc2['source_text']}")
    
    st.markdown("---")
    
    # 生成Token级分布
    st.write("**词级主题分布**:")
    st.write("以下表格展示每个词最可能属于的主题及置信度")
    
    result = visualize_approximate_distribution(model, texts, doc_selector2, calculate_tokens=True)
    
    if result and isinstance(result, dict):
        # 显示主题级分布
        if '主题分布' in result:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**主题级概率分布**:")
                st.dataframe(result['主题分布'], use_container_width=True)
            
            with col2:
                st.write("**词级分布**:")
                if '词级分布' in result:
                    st.dataframe(result['词级分布'], use_container_width=True)
                else:
                    st.info("💡 词级分布计算中...")
    else:
        st.warning("⚠️ 无法计算Token级分布（可能需要启用approximate_distribution）")
    
    st.markdown("---")
    
    st.info("""
    💡 **如何理解Token级分析**:
    - 每个词都会激活某个主题（置信度）
    - 高置信度的词是该主题的"关键触发词"
    - 可用于理解为什么该文档被分到某个主题
    
    **可解释性价值**:
    ✓ 看清AI的"视角" - 哪些词最重要
    ✓ 质量检测 - 发现错误分类的原因
    ✓ 模型改进 - 识别需要调整的词汇权重
    """)

# ============================================================================
# Tab 3: 离群值处理 (F103)
# ============================================================================
with tab3:
    st.subheader("🧹 离群值自动重分类 (F103)")
    st.write("将无法清晰分类的文档(Noise=-1)重新分配到合适主题")
    
    st.markdown("---")
    
    # 当前统计
    col1, col2, col3 = st.columns(3)
    
    noise_count = np.sum(topics == -1)
    total_count = len(topics)
    noise_pct = noise_count / total_count * 100 if total_count > 0 else 0
    
    with col1:
        st.metric("当前离群值数量", noise_count)
    
    with col2:
        st.metric("离群值占比", f"{noise_pct:.1f}%")
    
    with col3:
        st.metric("可分配主题数", len(np.unique(topics[topics != -1])))
    
    st.markdown("---")
    
    st.write("**重分类配置**:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy = st.radio(
            "选择重分类策略",
            [
                "probabilities - HDBSCAN软聚类概率（最稳定）",
                "distributions - 近似主题分布（较快）",
                "c-tf-idf - 词频相似度（最快）",
                "embeddings - 语义相似度（最准确但最慢）"
            ],
            help="不同策略的精度和速度权衡",
            key="reduce_strategy"
        )
        # 提取策略名称
        strategy_name = strategy.split(" - ")[0]
    
    with col2:
        threshold = st.slider(
            "置信度阈值",
            0.05, 0.5, 0.1, 0.05,
            help="只重分配置信度>阈值的离群值（越低越激进）"
        )
    
    st.markdown("---")
    
    # 执行重分类
    if st.button("🚀 执行重分类", key="reduce_outliers_btn"):
        with st.spinner(f"正在使用{strategy_name}策略重分类离群值..."):
            new_topics, report = reduce_outliers(model, topics, strategy=strategy_name, threshold=threshold)
        
        st.markdown("---")
        
        st.write("**重分类结果**:")
        
        # 显示报告
        if report:
            if 'error' in report:
                st.error(f"❌ 错误: {report['error']}")
            else:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("重分类前离群值", report['重分类前噪声数'])
                
                with col2:
                    st.metric("重分类后离群值", report['重分类后噪声数'])
                
                with col3:
                    st.metric("新增分配数", report['重新分配数'])
                
                with col4:
                    st.metric("改进率", report['改进率'])
                
                st.markdown("---")
                
                # 显示详细报告
                report_df = pd.DataFrame([report])
                st.dataframe(report_df, use_container_width=True)
                
                st.markdown("---")
                
                # 选项：保存新的topics
                if report['重新分配数'] > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ 保存为session state（当前会话）", key="save_topics"):
                            st.session_state.reduced_topics = new_topics
                            st.success("✅ 已保存，可在其他分析中使用")
                    
                    with col2:
                        if st.button("📥 下载处理后的topics数组", key="download_topics"):
                            topics_csv = pd.DataFrame({
                                'document_index': range(len(new_topics)),
                                'topic_id': new_topics
                            })
                            csv = topics_csv.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="点击下载 topics.csv",
                                data=csv,
                                file_name="reduced_topics.csv",
                                mime="text/csv"
                            )
    
    st.markdown("---")
    
    st.info("""
    💡 **如何理解离群值处理**:
    - Noise(标签-1)：无法清晰分配到任何主题的文档
    - 重分类：尝试把Noise分配到最合适的主题
    - 策略选择：速度和精度的平衡
    
    **可解释性价值**:
    ✓ 提高数据利用率（减少"未分类"）
    ✓ 完整覆盖（获得更完整的主题分布）
    ✓ 数据质量改进（可手动审核重分配结果）
    
    **4种策略对比**:
    | 策略 | 速度 | 精度 | 何时用 |
    |------|------|------|--------|
    | probabilities | 中 | 高 | 推荐默认 |
    | distributions | 快 | 中 | 大数据 |
    | c-tf-idf | 很快 | 中 | 快速试验 |
    | embeddings | 慢 | 很高 | 小数据集 |
    """)

# ============================================================================
# Tab 4: 自定义主题标签设置 (F104)
# ============================================================================
with tab4:
     st.subheader("🏷️ 自定义主题标签设置 (F104)")
     st.write("为主题指定有意义的自定义名称，替换自动生成的标签")
     
     st.markdown("---")
     
     # 显示当前主题标签
     topic_info = get_topics_summary(model)
     
     if not topic_info.empty:
         st.write("**当前主题标签**:")
         st.dataframe(topic_info[topic_info['Topic'] != -1], use_container_width=True)
         
         st.markdown("---")
         
         st.write("**自定义标签编辑**:")
         st.write("输入JSON格式的标签映射，或使用下面的表单")
         
         col1, col2 = st.columns([1, 1])
         
         with col1:
             st.write("**选项1: JSON格式输入**")
             st.write("例: {0: \"用户体验\", 1: \"产品质量\", 2: \"配送速度\"}")
             
             json_input = st.text_area(
                 "输入标签JSON（仅包含要更新的主题）",
                 value="{}",
                 height=150,
                 key="json_labels"
             )
         
         with col2:
             st.write("**选项2: 表单编辑**")
             
             label_dict = {}
             
             # 为每个非噪声主题创建编辑框
             for _, row in topic_info[topic_info['Topic'] != -1].iterrows():
                 topic_id = int(row['Topic'])
                 current_name = row['Name']
                 
                 new_label = st.text_input(
                     f"话题{topic_id}",
                     value=current_name,
                     key=f"label_topic_{topic_id}"
                 )
                 
                 if new_label != current_name:
                     label_dict[topic_id] = new_label
         
         st.markdown("---")
         
         # 处理JSON输入
         if st.button("🚀 应用自定义标签", key="apply_labels_btn"):
             try:
                 # 优先使用JSON输入，如果为空则使用表单输入
                 if json_input.strip() != "{}":
                     import json
                     json_dict = json.loads(json_input)
                     label_dict.update(json_dict)
                 
                 if label_dict:
                     with st.spinner("正在应用自定义标签..."):
                         updated_model, result = set_topic_labels(model, label_dict)
                         model = updated_model
                     
                     if result['status'] == '成功':
                         st.success(f"✅ {result['message']}")
                         st.info("💡 刷新页面以查看更新后的标签效果")
                     else:
                         st.error(f"❌ {result['message']}")
                 else:
                     st.warning("⚠️ 请输入至少一个自定义标签")
             
             except Exception as e:
                 st.error(f"❌ 标签应用失败: {e}")
         
         st.markdown("---")
         
         st.info("""
         💡 **自定义标签的用途**:
         - 提高可读性：用业务术语替换自动标签
         - 一致性：与公司或领域的标准术语对齐
         - 文档化：为后续分析提供清晰的标签
         
         **使用建议**:
         1. 审查自动生成的标签
         2. 根据话题词的关键词含义改进标签
         3. 保持标签简洁（5个字以内）
         4. 使用业务相关的术语
         """)
     else:
         st.warning("⚠️ 无法加载主题信息")

# ============================================================================
# Tab 5: 多主题词权重对比 (F105)
# ============================================================================
with tab5:
     st.subheader("📊 多主题词权重对比 (F105)")
     st.write("并行显示多个主题的Top词及其权重，便于进行主题对比分析")
     
     st.markdown("---")
     
     col1, col2 = st.columns([1, 1])
     
     with col1:
         top_n_topics = st.slider(
             "显示多少个主题",
             2, min(10, len(np.unique(topics)) - 1), 5,
             help="选择要对比的主题数量",
             key="f105_topics"
         )
     
     with col2:
         top_n_words = st.slider(
             "每个主题显示多少个Top词",
             3, 15, 10,
             help="每个主题的关键词数量",
             key="f105_words"
         )
     
     st.markdown("---")
     
     if st.button("🔄 生成词权重对比图", key="gen_barchart_btn"):
         with st.spinner("正在生成对比图表..."):
             fig = visualize_barchart_comparison(model, top_n_topics=top_n_topics, top_n_words=top_n_words)
         
         if fig:
             st.plotly_chart(fig, use_container_width=True)
             
             st.markdown("---")
             
             st.info("""
             💡 **如何解读对比图**:
             - X轴：关键词排序（越靠前权重越高）
             - Y轴：c-TF-IDF权重分数
             - 多个主题并排显示，便于对比
             - 高权重词是该主题的"代表词"
             
             **可用于**:
             ✓ 理解不同主题的核心关注点
             ✓ 识别相似主题（词汇重叠很多）
             ✓ 发现主题之间的差异和关联
             ✓ 手动验证主题建模效果
             """)
         else:
             st.warning("⚠️ 对比图生成失败，请检查数据或模型配置")

# ============================================================================
# Tab 6: 关键词主题搜索 (F106)
# ============================================================================
with tab6:
     st.subheader("🔍 关键词主题搜索 (F106)")
     st.write("输入关键词，自动查找包含这些词汇的相关主题")
     
     st.markdown("---")
     
     # 关键词输入
     col1, col2 = st.columns([2, 1])
     
     with col1:
         keywords_input = st.text_input(
             "输入搜索关键词（用逗号分隔）",
             value="用户,服务,产品",
             placeholder="例: 用户,服务,产品",
             key="search_keywords"
         )
     
     with col2:
         top_n_results = st.slider(
             "返回排名前N个主题",
             1, 10, 5,
             key="f106_top_n"
         )
     
     st.markdown("---")
     
     # 执行搜索
     if st.button("🚀 搜索相关主题", key="search_topics_btn"):
         # 解析关键词
         keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
         
         if keywords:
             with st.spinner(f"正在搜索包含 {keywords} 的主题..."):
                 results_df = search_topics(model, keywords, top_n=top_n_results)
             
             if not results_df.empty:
                 st.success(f"✅ 找到{len(results_df)}个相关主题")
                 
                 st.markdown("---")
                 
                 st.write("**搜索结果**:")
                 st.dataframe(results_df, use_container_width=True)
                 
                 st.markdown("---")
                 
                 # 详细展示每个主题
                 st.write("**详细信息**:")
                 
                 for idx, row in results_df.iterrows():
                     with st.expander(f"📌 {row['主题名称']} (相关性: {row['平均相关性']})"):
                         col1, col2, col3 = st.columns(3)
                         
                         with col1:
                             st.metric("主题ID", int(row['主题ID']))
                         
                         with col2:
                             st.metric("匹配词数", len(row['匹配词'].split(',')))
                         
                         with col3:
                             st.metric("包含文档数", row['文档数'])
                         
                         st.write(f"**匹配词**: {row['匹配词']}")
             else:
                 st.warning(f"⚠️ 未找到包含 {keywords} 的相关主题")
         else:
             st.error("❌ 请输入至少一个关键词")
     
     st.markdown("---")
     
     st.info("""
     💡 **关键词搜索的应用场景**:
     - 快速定位特定话题（如"物流"、"售后"）
     - 发现潜在的主题聚类（相似词出现在多个主题中）
     - 质量检查：验证自动标签是否准确
     - 业务导向：根据运营关键词查找相关意见
     
     **搜索策略**:
     ✓ 使用行业术语或常见业务词汇
     ✓ 逐个关键词搜索，再组合搜索
     ✓ 使用搜索结果指导主题标签优化
     """)

st.markdown("---")

st.subheader("📊 Phase 4-5 功能总览")

st.markdown("""
### ✅ 已实现的6个功能

| 功能ID | 功能名称 | 所在位置 | 用途 |
|--------|--------|--------|------|
| **F101** | 单文档主题概率分布 | Tab1 | 理解模型对单条意见的判断，调试置信度 |
| **F102** | Token级主题分析 | Tab2 | 看清AI的"视角"，识别关键触发词 |
| **F103** | 离群值自动重分类 | Tab3 | 提高数据利用率，改进主题覆盖 |
| **F104** | 自定义主题标签设置 | Tab4 | 用业务术语定制标签，提高可读性 |
| **F105** | 多主题词权重对比 | Tab5 | 并行对比主题特征，识别相似主题 |
| **F106** | 关键词主题搜索 | Tab6 | 快速定位特定话题，质量检查 |

### 后续计划

**Phase 6** (可选): F107-F109
- F107: 论文级静态图导出（高分辨率PNG/PDF）
- F108: 主题表示优化（更新主题名称生成模型）
- F109: 主题代表文档提取（每个主题显示top3代表文档）

---

💡 **推荐使用顺序**:
1. **第一步**: Tab1-3（理解、分析、清理数据）
2. **第二步**: Tab4-6（优化标签、对比分析、快速搜索）
3. **输出**: 发布到P7进行全面展示

**完整工作流**:
- 使用F101/F102理解单个意见的分类逻辑
- 用F103改进数据质量（减少噪声）
- 用F104定制业务相关的标签
- 用F105/F106进行对比和验证
- 最后输出到P7_话题热度敏感度分析页面展示

**技术要求**: BERTopic已启用 `calculate_probabilities=True`
""")
