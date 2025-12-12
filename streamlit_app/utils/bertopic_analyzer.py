"""
BERTopic主题分析工具 - 深度话题建模
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, List, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from umap import UMAP
    from hdbscan import HDBSCAN
    BERTOPIC_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Import failed: {e}")
    import traceback
    traceback.print_exc()
    BERTOPIC_AVAILABLE = False


def get_bertopic_model() -> Optional[Any]:
    """获取BERTopic模型"""
    import os
    from pathlib import Path
    
    print("DEBUG: get_bertopic_model() called")
    if not BERTOPIC_AVAILABLE:
        print("DEBUG: BERTOPIC_AVAILABLE is False")
        return None
    
    try:
        # 使用轻量级英文模型（无需HuggingFace网络连接，已内置）
        # all-MiniLM-L6-v2: 22MB，超轻，已在sentence-transformers中预载
        print("DEBUG: 尝试加载轻量级embedding模型...")
        try:
            embedding_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device='cpu'  # 强制CPU模式，避免GPU问题
            )
            print("DEBUG: all-MiniLM-L6-v2加载成功")
        except Exception as e1:
            print(f"DEBUG: all-MiniLM-L6-v2加载失败，尝试备选模型: {e1}")
            try:
                # 备选：极轻的多语言模型
                embedding_model = SentenceTransformer(
                    'distiluse-base-multilingual-cased-v2',
                    device='cpu'
                )
                print("DEBUG: 多语言模型加载成功")
            except Exception as e2:
                print(f"DEBUG: 所有网络模型加载失败: {e2}")
                print("WARNING: 将使用TF-IDF向量作为embedding的备选方案")
                # 降级：使用本地TF-IDF向量
                embedding_model = None
        
        # 优化HDBSCAN聚类参数（防止话题重复）
        umap_model = UMAP(
            n_neighbors=20,           # ← 增加到20（保留更多全局结构）
            n_components=5,
            min_dist=0.1,             # ← 增加到0.1（避免过度聚集）
            metric='cosine',
            random_state=42
        )
        
        hdbscan_model = HDBSCAN(
            min_cluster_size=30,      # ← 大幅提高到30（防止小话题被分离）
            min_samples=10,           # ← 提高到10（密度要求更严格）
            cluster_selection_epsilon=0.5,  # ← 添加：进一步合并相似簇
            prediction_data=True      # ← 支持新文档预测
        )
        
        # 如果embedding模型加载失败，使用TF-IDF向量
        if embedding_model is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            print("DEBUG: 降级使用TF-IDF向量方案")
            # 不设embedding_model，BERTopic会自动使用TF-IDF
        
        model = BERTopic(
            embedding_model=embedding_model,  # 可以为None
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            language="chinese",
            calculate_probabilities=True,
            verbose=False,
            top_n_words=10,
            nr_topics="auto"          # ← 自动优化主题数
        )
        return model
    except Exception as e:
        print(f"DEBUG: BERTopic初始化失败详细错误: {e}")
        import traceback
        traceback.print_exc()
        st.warning(f"BERTopic初始化失败: {e}")
        return None


@st.cache_resource
def train_bertopic_cached(texts_tuple: tuple) -> tuple:
     """
     缓存版BERTopic训练（只训练一次，结果保存）
     
     参数：texts_tuple - 文本列表的元组版本（便于缓存）
     返回: (topics, probabilities, model)
     """
     if not BERTOPIC_AVAILABLE:
         st.warning("BERTopic未安装，跳过高级主题分析")
         return None, None, None
     
     try:
         with st.spinner("🤖 正在训练BERTopic模型，提取隐藏主题..."):
             model = get_bertopic_model()
             if model is None:
                 return None, None, None
             
             texts = list(texts_tuple)
             topics, probs = model.fit_transform(texts)
         return topics, probs, model
     except Exception as e:
         st.warning(f"主题提取失败: {e}")
         return None, None, None


def train_bertopic(texts: List[str], model: Optional[Any] = None) -> tuple:
     """
     训练BERTopic模型提取隐藏主题（自动缓存版本）
     
     返回: (topics, probabilities, model)
     """
     if not BERTOPIC_AVAILABLE:
         st.warning("BERTopic未安装，跳过高级主题分析")
         return None, None, None
     
     # 转换为元组便于streamlit缓存
     texts_tuple = tuple(texts)
     
     return train_bertopic_cached(texts_tuple)


def visualize_topics_2d(model: Optional[Any], topics: Optional[np.ndarray]) -> Optional[object]:
    """生成2D主题可视化（交互式图表）"""
    if model is None or topics is None:
        return None
    
    try:
        return model.visualize_topics()
    except Exception as e:
        st.warning(f"主题可视化生成失败: {e}")
        return None


def visualize_topic_hierarchy(model: Optional[Any]) -> Optional[object]:
    """生成主题层级关系图"""
    if model is None:
        return None
    
    try:
        # 尝试生成层级关系
        if len(model.get_topic_info()) > 2:
            hierarchical_topics = model.hierarchical_topics(
                model.documents,
                linkage_function=lambda x: __import__('scipy').cluster.hierarchy.linkage(x, "ward")
            )
            return model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
        else:
            st.info("💡 主题数量太少，无法生成层级关系图")
            return None
    except Exception as e:
        st.warning(f"层级关系图生成失败: {e}")
        return None


def visualize_topic_similarity(model: Optional[Any]) -> Optional[object]:
    """生成主题相似度热力图"""
    if model is None:
        return None
    
    try:
        return model.visualize_heatmap(n_clusters=5)
    except Exception as e:
        st.warning(f"相似度热力图生成失败: {e}")
        return None


def visualize_topic_terms(model: Optional[Any], top_n: int = 5) -> Optional[object]:
    """生成主题词语的重要性图表"""
    if model is None:
        return None
    
    try:
        return model.visualize_terms(top_n_terms=top_n)
    except Exception as e:
        st.warning(f"词语重要性图表生成失败: {e}")
        return None


def get_topic_keywords(model: Optional[Any], topic: int, top_n: int = 5) -> List[tuple]:
    """获取指定主题的关键词"""
    if model is None:
        return []
    
    try:
        topic_info = model.get_topic(topic)
        return topic_info[:top_n] if topic_info else []
    except Exception as e:
        return []


def get_topics_summary(model: Optional[Any]) -> pd.DataFrame:
    """获取所有主题的摘要信息"""
    if model is None:
        return pd.DataFrame()
    
    try:
        topic_info = model.get_topic_info()
        return topic_info[['Topic', 'Count', 'Name']].copy()
    except Exception as e:
        return pd.DataFrame()


def get_documents_by_topic(df: pd.DataFrame, topics: np.ndarray, topic_id: int, top_n: int = 5) -> pd.DataFrame:
    """获取指定主题下的文档列表"""
    if topics is None:
        return pd.DataFrame()
    
    try:
        mask = topics == topic_id
        topic_docs = df[mask].head(top_n)[['source_text', 'sentiment', 'risk_level']].copy()
        return topic_docs
    except Exception as e:
        return pd.DataFrame()


def visualize_documents_2d(model: Optional[Any], docs: List[str], topics: np.ndarray) -> Optional[object]:
    """生成文档在2D空间的分布（Umap降维）"""
    if model is None or topics is None:
        return None
    
    try:
        return model.visualize_documents(docs, topics=topics, hide_document_hover=False)
    except Exception as e:
        try:
            # 如果有embedding就用，没有就简化版本
            return model.visualize_documents(docs, hide_document_hover=True)
        except:
            return None


def visualize_term_distribution(model: Optional[Any], top_n_topics: int = 5) -> Optional[object]:
    """生成各主题的词频分布"""
    if model is None:
        return None
    
    try:
        return model.visualize_barchart(top_n_topics=top_n_topics)
    except Exception as e:
        return None


def generate_topic_tree(model: Optional[Any], df: pd.DataFrame, topics: np.ndarray) -> str:
    """生成主题的树形结构文本"""
    if model is None or topics is None:
        return ""
    
    try:
        topic_info = model.get_topic_info()
        tree_text = ""
        
        for idx, row in topic_info[topic_info['Topic'] != -1].iterrows():
            topic_id = row['Topic']
            topic_name = row['Name']
            count = row['Count']
            
            # 获取该主题的前3个文档
            mask = topics == topic_id
            docs = df[mask].head(3)
            
            tree_text += f"**话题{int(topic_id)}: {topic_name}** ({count} 条文档)\n"
            
            for i, (_, doc) in enumerate(docs.iterrows(), 1):
                text_preview = doc['source_text'][:60] + "..." if len(doc['source_text']) > 60 else doc['source_text']
                tree_text += f"  ├─ {i}. \"{text_preview}\"\n"
                tree_text += f"     情感: {doc['sentiment']} | 风险: {doc['risk_level']}\n"
            
            tree_text += "\n"
        
        return tree_text
    except Exception as e:
        return f"生成失败: {e}"


def visualize_term_score_decline(model: Optional[Any], top_n_topics: int = 5) -> Optional[object]:
    """生成c-TF-IDF分数衰减图（显示词汇权重的递减）"""
    if model is None:
        return None
    
    try:
        return model.visualize_term_rank(top_n_topics=top_n_topics, log_scale=False)
    except Exception as e:
        return None


def get_hierarchical_topics(model: Optional[Any]) -> Optional[pd.DataFrame]:
    """计算并返回层级主题结构"""
    if model is None:
        return None
    
    try:
        # 需要有足够的主题才能生成层级
        if len(model.get_topic_info()) > 2:
            hierarchical_topics = model.hierarchical_topics(
                model.documents,
                linkage_function=lambda x: __import__('scipy').cluster.hierarchy.linkage(x, "ward")
            )
            return hierarchical_topics
        else:
            return None
    except Exception as e:
        return None


def visualize_hierarchical_documents(model: Optional[Any], texts: List[str], topics: np.ndarray) -> Optional[object]:
    """生成分层文档可视化（在层级树的2D空间中）"""
    if model is None or topics is None or len(texts) == 0:
        return None
    
    try:
        # 获取分层主题
        if len(model.get_topic_info()) > 2:
            hierarchical_topics = model.hierarchical_topics(
                model.documents,
                linkage_function=lambda x: __import__('scipy').cluster.hierarchy.linkage(x, "ward")
            )
            # 尝试可视化分层文档
            return model.visualize_hierarchical_documents(texts, hierarchical_topics=hierarchical_topics, hide_document_hover=True)
        else:
            return None
    except Exception as e:
        return None


def get_topic_keywords_detailed(model: Optional[Any], topic_id: int, top_n: int = 10) -> pd.DataFrame:
    """获取指定主题的关键词及其c-TF-IDF分数"""
    if model is None:
        return pd.DataFrame()
    
    try:
        topic_info = model.get_topic(topic_id)
        if topic_info:
            # topic_info 是 [(word, score), ...] 的列表
            keywords_df = pd.DataFrame(topic_info[:top_n], columns=['关键词', 'c-TF-IDF分数'])
            keywords_df['排名'] = range(1, len(keywords_df) + 1)
            return keywords_df[['排名', '关键词', 'c-TF-IDF分数']]
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


def get_topic_text_representation(model: Optional[Any], topic_id: int) -> str:
    """获取主题的文本表示（由生成模型生成）"""
    if model is None:
        return ""
    
    try:
        # 获取主题的标签（如果有的话）
        topic_info = model.get_topic_info()
        if topic_info is not None and len(topic_info) > 0:
            topic_row = topic_info[topic_info['Topic'] == topic_id]
            if not topic_row.empty:
                return topic_row.iloc[0]['Name']
        return f"话题{topic_id}"
    except Exception as e:
        return f"话题{topic_id}"


def calculate_topic_distribution(model: Optional[Any], texts: List[str]) -> Optional[np.ndarray]:
    """计算文档的主题分布概率矩阵"""
    if model is None or len(texts) == 0:
        return None
    
    try:
        # 如果使用了calculate_probabilities=True，可以直接获取
        if hasattr(model, 'probabilities_') and model.probabilities_ is not None:
            return model.probabilities_
        else:
            # 否则尝试估计主题分布
            return model.approximate_distribution(texts)
    except Exception as e:
        return None


def visualize_topic_per_class(model: Optional[Any], df: pd.DataFrame, class_column: str = 'sentiment') -> Optional[object]:
    """按分类（如情感类别）生成主题分布可视化"""
    if model is None or df is None or class_column not in df.columns:
        return None
    
    try:
        # 获取所有唯一的类别
        classes = df[class_column].unique()
        
        # 创建简单的柱状图对比
        import plotly.graph_objects as go
        
        fig = go.Figure()
        topic_info = model.get_topic_info()
        
        for class_val in classes:
            class_mask = df[class_column] == class_val
            topic_counts = []
            
            for topic_id in topic_info['Topic']:
                if topic_id == -1:  # 跳过噪声
                    continue
                count = len(df[class_mask & (df.index.isin([i for i, t in enumerate(model.topics_) if t == topic_id]))])
                topic_counts.append(count)
            
            fig.add_trace(go.Bar(
                name=str(class_val),
                x=topic_info[topic_info['Topic'] != -1]['Topic'].astype(str),
                y=topic_counts,
                text=topic_counts,
                textposition='auto',
            ))
        
        fig.update_layout(
            title="按分类统计的主题分布",
            xaxis_title="主题ID",
            yaxis_title="文档数量",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        return None


# ============================================================================
# Phase 4 新增函数 - F101, F102, F103
# ============================================================================

def visualize_distribution(model: Optional[Any], topic_id: int, probabilities: Optional[np.ndarray] = None, 
                          min_probability: float = 0.015) -> Optional[object]:
    """
    F101: 单文档主题概率分布可视化
    
    显示某条文档属于各主题的置信度百分比（柱状图）
    
    参数:
        model: BERTopic模型
        topic_id: 文档在模型中的index
        probabilities: 单条文档的主题概率数组 (shape: [n_topics])
        min_probability: 最小显示概率阈值
    
    返回:
        Plotly交互式柱状图
    """
    if model is None:
        return None
    
    try:
        # 如果没提供probabilities，尝试从模型获取
        if probabilities is None:
            if hasattr(model, 'probabilities_') and model.probabilities_ is not None:
                if topic_id < len(model.probabilities_):
                    probabilities = model.probabilities_[topic_id]
                else:
                    st.warning(f"文档索引{topic_id}超出范围")
                    return None
            else:
                st.warning("模型未计算概率，请在BERTopic初始化时设置calculate_probabilities=True")
                return None
        
        # 获取主题信息
        topic_info = model.get_topic_info()
        if topic_info is None or len(topic_info) == 0:
            return None
        
        # 过滤低概率主题
        valid_indices = probabilities >= min_probability
        filtered_probs = probabilities[valid_indices]
        
        if len(filtered_probs) == 0:
            st.info("💡 该文档的主题概率都很低，可能是噪声文档")
            return None
        
        # 获取对应的主题标签
        valid_topics = np.where(valid_indices)[0]
        topic_labels = []
        for idx in valid_topics:
            matching = topic_info[topic_info['Topic'] == idx]
            if not matching.empty:
                topic_labels.append(f"话题{int(idx)}: {matching.iloc[0]['Name'][:15]}")
            else:
                topic_labels.append(f"话题{int(idx)}")
        
        # 创建图表
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Bar(
            x=topic_labels,
            y=filtered_probs,
            marker=dict(color=filtered_probs, colorscale='Viridis', showscale=True),
            text=[f'{p:.2%}' for p in filtered_probs],
            textposition='outside'
        )])
        
        fig.update_layout(
            title=f"文档{topic_id}的主题概率分布",
            xaxis_title="主题",
            yaxis_title="概率",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    except Exception as e:
        st.warning(f"概率分布可视化生成失败: {e}")
        return None


def visualize_approximate_distribution(model: Optional[Any], texts: List[str], 
                                       doc_index: int = 0, calculate_tokens: bool = True) -> Optional[object]:
    """
    F102: Token级别主题分布分析
    
    精确到单词级别，显示哪些词触发了哪个主题
    
    参数:
        model: BERTopic模型
        texts: 所有文本列表
        doc_index: 要分析的文档索引
        calculate_tokens: 是否计算token级别的分布
    
    返回:
        包含token级分布的DataFrame或可视化
    """
    if model is None or doc_index >= len(texts):
        return None
    
    try:
        # 获取近似分布（approximate_distribution）
        topic_distr, topic_token_distr = model.approximate_distribution(
            [texts[doc_index]],
            calculate_tokens=calculate_tokens
        )
        
        if topic_distr is None:
            return None
        
        # 转换为DataFrame显示
        topic_info = model.get_topic_info()
        
        # 主题级分布
        result_data = []
        for topic_id, prob in enumerate(topic_distr[0]):
            if prob > 0.01:  # 只显示概率>1%的主题
                matching = topic_info[topic_info['Topic'] == topic_id]
                topic_name = matching.iloc[0]['Name'] if not matching.empty else f"话题{topic_id}"
                result_data.append({
                    '主题': f"{topic_id}: {topic_name}",
                    '概率': f"{prob:.2%}",
                    '是否为目标主题': prob > 0.3
                })
        
        result_df = pd.DataFrame(result_data)
        
        # Token级分布（如果可用）
        if calculate_tokens and topic_token_distr is not None and len(topic_token_distr) > 0:
            # 创建token标记
            text = texts[doc_index]
            words = text.split()
            
            token_info = []
            for word_idx, word in enumerate(words):
                if word_idx < len(topic_token_distr[0]):
                    top_topic = np.argmax(topic_token_distr[0][word_idx])
                    prob = topic_token_distr[0][word_idx][top_topic]
                    matching = topic_info[topic_info['Topic'] == top_topic]
                    topic_name = matching.iloc[0]['Name'] if not matching.empty else f"话题{top_topic}"
                    
                    token_info.append({
                        '词': word,
                        '主题': f"{top_topic}: {topic_name}",
                        '置信度': f"{prob:.2%}"
                    })
            
            token_df = pd.DataFrame(token_info)
            return {'主题分布': result_df, '词级分布': token_df}
        
        return {'主题分布': result_df}
    
    except Exception as e:
        st.warning(f"近似分布计算失败: {e}")
        return None


def reduce_outliers(model: Optional[Any], topics: np.ndarray, 
                   strategy: str = "probabilities", threshold: float = 0.1) -> tuple:
     """
     F103: 离群值自动重分类
     
     将noise文档(标签-1)重新分配到有效主题
     
     参数:
         model: BERTopic模型
         topics: 原始主题数组
         strategy: 重分类策略
             - "probabilities": 基于HDBSCAN软聚类概率
             - "distributions": 基于近似主题分布
             - "c-tf-idf": 基于词频相似度（最快）
             - "embeddings": 基于语义embedding相似度（最准）
         threshold: 分配置信度阈值 (0.05-0.3)
     
     返回:
         (新的topics数组, 统计报告dict)
     """
     if model is None or topics is None:
         return topics, {}
     
     try:
         # 计算统计信息
         noise_mask = topics == -1
         noise_count_before = np.sum(noise_mask)
         
         if noise_count_before == 0:
             return topics, {'message': '没有离群值需要处理'}
         
         # 调用BERTopic的reduce_outliers方法
         new_topics = model.reduce_outliers(
             topics,
             strategy=strategy,
             threshold=threshold
         )
         
         # 计算改进效果
         noise_count_after = np.sum(new_topics == -1)
         reclassified_count = noise_count_before - noise_count_after
         reclassified_pct = reclassified_count / noise_count_before * 100 if noise_count_before > 0 else 0
         
         report = {
             'strategy': strategy,
             'threshold': threshold,
             '重分类前噪声数': int(noise_count_before),
             '重分类后噪声数': int(noise_count_after),
             '重新分配数': int(reclassified_count),
             '改进率': f"{reclassified_pct:.1f}%",
             '状态': '成功' if reclassified_count > 0 else '无改进'
         }
         
         return new_topics, report
     
     except Exception as e:
         st.warning(f"离群值处理失败: {e}")
         return topics, {'error': str(e)}


# ============================================================================
# Phase 5 新增函数 - F104, F105, F106
# ============================================================================

def set_topic_labels(model: Optional[Any], topic_labels_dict: dict) -> tuple:
    """
    F104: 自定义主题标签设置
    
    允许用户为主题指定自定义名称，替换自动生成的标签
    
    参数:
         model: BERTopic模型
         topic_labels_dict: 标签映射字典 {topic_id: custom_label}
         例如: {0: "用户体验", 1: "产品质量", 2: "配送速度"}
    
    返回:
         (更新后的模型, 操作结果dict)
    """
    if model is None or not topic_labels_dict:
        return model, {'status': '失败', 'message': '模型或标签为空'}
    
    try:
         # BERTopic的set_topic_labels方法
         model.set_topic_labels(topic_labels_dict)
         
         result = {
             'status': '成功',
             'message': f'已设置{len(topic_labels_dict)}个主题的自定义标签',
             'labels_count': len(topic_labels_dict)
         }
         
         return model, result
    
    except Exception as e:
        return model, {'status': '失败', 'message': str(e)}


def visualize_barchart_comparison(model: Optional[Any], top_n_topics: int = 5, top_n_words: int = 10) -> Optional[object]:
    """
    F105: 多主题词权重对比柱状图
    
    并行显示多个主题的Top词及其权重，方便进行主题对比
    
    参数:
         model: BERTopic模型
         top_n_topics: 显示多少个主题
         top_n_words: 每个主题显示多少个Top词
    
    返回:
         Plotly交互式可视化对象
    """
    if model is None:
        return None
    
    try:
        # 调用BERTopic的visualize_barchart方法
        fig = model.visualize_barchart(top_n_topics=top_n_topics, top_n_words=top_n_words)
        return fig
    
    except Exception as e:
        st.warning(f"多主题词权重对比生成失败: {e}")
        return None


def search_topics(model: Optional[Any], keywords: List[str], top_n: int = 5) -> pd.DataFrame:
    """
    F106: 关键词主题搜索
    
    输入关键词，返回包含这些词的主题列表及相关性排名
    
    参数:
         model: BERTopic模型
         keywords: 搜索关键词列表
         top_n: 返回排名前n的相关主题
    
    返回:
         包含主题、匹配词、相关性分数的DataFrame
    """
    if model is None or not keywords:
        return pd.DataFrame()
    
    try:
        topic_info = model.get_topic_info()
        results = []
        
        for topic_id in topic_info['Topic']:
            if topic_id == -1:  # 跳过噪声
                continue
            
            # 获取该主题的所有词
            topic_words = model.get_topic(topic_id)
            if not topic_words:
                continue
            
            word_list = [word for word, score in topic_words]
            
            # 检查关键词匹配
            matched_words = []
            match_scores = []
            
            for keyword in keywords:
                for idx, (word, score) in enumerate(topic_words):
                    if keyword in word or word in keyword:
                        matched_words.append(word)
                        match_scores.append(score * (1 / (idx + 1)))  # 权重：排名越高分数越高
                        break
            
            if matched_words:
                # 该主题与搜索词相关
                avg_score = np.mean(match_scores) if match_scores else 0
                topic_name = topic_info[topic_info['Topic'] == topic_id].iloc[0]['Name']
                
                results.append({
                    '主题ID': int(topic_id),
                    '主题名称': topic_name,
                    '匹配词': ', '.join(matched_words),
                    '平均相关性': f"{avg_score:.3f}",
                    '文档数': int(topic_info[topic_info['Topic'] == topic_id].iloc[0]['Count'])
                })
        
        if results:
            results_df = pd.DataFrame(results)
            # 按相关性排序
            results_df['相关性分数'] = results_df['平均相关性'].astype(float)
            results_df = results_df.sort_values('相关性分数', ascending=False).head(top_n)
            results_df = results_df.drop('相关性分数', axis=1)
            return results_df
        else:
            return pd.DataFrame()
    
    except Exception as e:
        st.warning(f"关键词搜索失败: {e}")
        return pd.DataFrame()


# ============================================================================
# Phase 6 新增函数 - F109
# ============================================================================

def get_representative_documents(df: pd.DataFrame, model: Optional[Any], topics: np.ndarray, 
                                 topic_id: int, top_n: int = 3) -> pd.DataFrame:
    """
    F109: 主题代表文档提取
    
    获取某个主题最具代表性的Top N文档，用于理解主题的核心内容
    
    参数:
         df: 数据框（包含source_text, sentiment, risk_level等列）
         model: BERTopic模型
         topics: 主题数组
         topic_id: 要提取代表文档的主题ID
         top_n: 返回多少个代表文档（默认3）
    
    返回:
         包含代表文档及其属性的DataFrame
    """
    if model is None or topics is None or df is None:
        return pd.DataFrame()
    
    try:
        # 获取该主题的所有文档索引
        mask = topics == topic_id
        
        if not mask.any():
            return pd.DataFrame()
        
        # 获取该主题的概率矩阵（如果有）
        if hasattr(model, 'probabilities_') and model.probabilities_ is not None:
            # 按概率排序（概率高 = 代表性强）
            topic_probs = model.probabilities_[mask, topic_id]
            indices = np.argsort(topic_probs)[::-1][:top_n]
            doc_indices = np.where(mask)[0][indices]
        else:
            # 没有概率信息，返回前top_n个文档
            doc_indices = np.where(mask)[0][:top_n]
        
        # 构建结果DataFrame
        results = []
        
        for idx, doc_idx in enumerate(doc_indices, 1):
            doc = df.iloc[doc_idx]
            
            # 获取该文档对该主题的置信度
            conf = None
            if hasattr(model, 'probabilities_') and model.probabilities_ is not None:
                if doc_idx < len(model.probabilities_):
                    conf = model.probabilities_[doc_idx, topic_id]
            
            results.append({
                '排名': idx,
                '文档ID': doc_idx,
                '内容': doc['source_text'][:100] + ('...' if len(doc['source_text']) > 100 else ''),
                '完整内容': doc['source_text'],
                '情感': doc.get('sentiment', '未知'),
                '风险': doc.get('risk_level', '未知'),
                '置信度': f"{conf:.2%}" if conf else "N/A"
            })
        
        result_df = pd.DataFrame(results)
        return result_df
    
    except Exception as e:
        st.warning(f"代表文档提取失败: {e}")
        return pd.DataFrame()


def get_all_topics_representative_docs(df: pd.DataFrame, model: Optional[Any], 
                                       topics: np.ndarray, top_n: int = 3) -> dict:
    """
    F109 扩展: 为所有主题批量提取代表文档
    
    参数:
         df: 数据框
         model: BERTopic模型
         topics: 主题数组
         top_n: 每个主题的代表文档数
    
    返回:
         {topic_id: representative_docs_df} 的字典
    """
    if model is None:
        return {}
    
    try:
        topic_info = model.get_topic_info()
        all_docs = {}
        
        for topic_id in topic_info['Topic']:
            if topic_id == -1:  # 跳过噪声
                continue
            
            docs_df = get_representative_documents(df, model, topics, topic_id, top_n)
            
            if not docs_df.empty:
                all_docs[topic_id] = docs_df
        
        return all_docs
    
    except Exception as e:
        return {}


# ============================================================================
# Phase 7 新增函数 - F107
# ============================================================================

def export_visualization_to_file(fig: Optional[object], filename: str, format: str = 'png', 
                                dpi: int = 300, width: int = 1200, height: int = 700) -> bytes:
    """
    F107: 论文级静态图导出
    
    将Plotly可视化导出为高分辨率的静态图（PNG/PDF/SVG）用于报告和论文
    
    参数:
         fig: Plotly图对象
         filename: 输出文件名（不含扩展名）
         format: 导出格式 ('png', 'pdf', 'svg', 'jpg')
         dpi: 分辨率（每英寸像素数，推荐300用于打印）
         width: 图片宽度（像素）
         height: 图片高度（像素）
    
    返回:
         bytes: 文件内容（可用于下载）
    """
    if fig is None:
        st.error("❌ 图表对象为空")
        return None
    
    try:
        # 调整图表尺寸和样式以适应导出
        fig.update_layout(
            width=width,
            height=height,
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        # 使用kaleido导出（需要安装）
        format_lower = format.lower()
        if format_lower == 'png':
            file_content = fig.to_image(format='png', width=width, height=height, scale=dpi/100)
        elif format_lower == 'pdf':
            file_content = fig.to_image(format='pdf', width=width, height=height)
        elif format_lower == 'svg':
            file_content = fig.to_image(format='svg', width=width, height=height)
        elif format_lower == 'jpg':
            file_content = fig.to_image(format='jpg', width=width, height=height, quality=95)
        else:
            st.error(f"❌ 不支持的格式: {format}")
            return None
        
        return file_content
    
    except ImportError:
        st.warning("⚠️ 需要安装kaleido: pip install kaleido")
        # 降级方案：尝试用plotly的离线导出
        try:
            if format.lower() in ['html']:
                return fig.to_html().encode('utf-8')
            else:
                st.error("❌ 需要kaleido库才能导出静态图片")
                return None
        except:
            return None
    
    except Exception as e:
        st.error(f"❌ 导出失败: {e}")
        return None


def batch_export_visualizations(figures_dict: dict, export_format: str = 'png', 
                               output_folder: str = 'exports', dpi: int = 300) -> dict:
    """
    F107 扩展: 批量导出多个图表
    
    参数:
         figures_dict: {name: fig_object} 的字典
         export_format: 导出格式
         output_folder: 输出文件夹路径
         dpi: 导出分辨率
    
    返回:
         {name: file_content} 的字典
    """
    if not figures_dict:
        return {}
    
    try:
        import os
        
        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)
        
        exported = {}
        
        for name, fig in figures_dict.items():
            try:
                file_content = export_visualization_to_file(
                    fig, 
                    name, 
                    format=export_format, 
                    dpi=dpi
                )
                
                if file_content:
                    exported[name] = file_content
            
            except Exception as e:
                st.warning(f"⚠️ {name}导出失败: {e}")
        
        return exported
    
    except Exception as e:
        st.error(f"❌ 批量导出失败: {e}")
        return {}


def create_summary_report(model: Optional[Any], df: pd.DataFrame, topics: np.ndarray,
                         title: str = "BERTopic分析报告") -> str:
    """
    F107 扩展: 生成文本格式的分析报告摘要
    
    参数:
         model: BERTopic模型
         df: 数据框
         topics: 主题数组
         title: 报告标题
    
    返回:
         str: Markdown格式的报告文本
    """
    if model is None or topics is None:
        return ""
    
    try:
        topic_info = model.get_topic_info()
        
        report = f"""# {title}

## 数据概览

- **总文档数**: {len(df)}
- **唯一主题数**: {len(np.unique(topics)) - 1}（不含噪声）
- **噪声文档数**: {np.sum(topics == -1)} ({100*np.sum(topics == -1)/len(df):.1f}%)
- **数据覆盖率**: {100*(len(df)-np.sum(topics==-1))/len(df):.1f}%

## 主题统计

| 主题ID | 主题名称 | 文档数 | 占比 | Top 5关键词 |
|--------|---------|--------|------|-----------|
"""
        
        for _, row in topic_info[topic_info['Topic'] != -1].iterrows():
            topic_id = int(row['Topic'])
            topic_name = row['Name']
            count = row['Count']
            pct = 100 * count / (len(df) - np.sum(topics == -1))
            
            # 获取Top 5关键词
            topic_words = model.get_topic(topic_id)
            if topic_words:
                top_words = ', '.join([word for word, _ in topic_words[:5]])
            else:
                top_words = "N/A"
            
            report += f"| {topic_id} | {topic_name} | {count} | {pct:.1f}% | {top_words} |\n"
        
        report += f"""

## 数据质量指标

- **平均主题概率**: """
        
        if hasattr(model, 'probabilities_') and model.probabilities_ is not None:
            avg_prob = np.max(model.probabilities_, axis=1).mean()
            report += f"{avg_prob:.3f}\n"
        else:
            report += "未计算\n"
        
        report += f"""
## 生成信息

- **生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
- **使用工具**: BERTopic (Phase 4-7 分析框架)
- **覆盖的分析函数**: F101-F109

---

*本报告由自动分析系统生成。建议结合人工审核确保准确性。*
"""
        
        return report
    
    except Exception as e:
        return f"报告生成失败: {e}"
