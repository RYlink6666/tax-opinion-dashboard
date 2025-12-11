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
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False


@st.cache_resource
def get_bertopic_model() -> Optional[Any]:
    """获取缓存的BERTopic模型（仅初始化一次）"""
    if not BERTOPIC_AVAILABLE:
        return None
    
    try:
        # 使用支持中文的embedding模型
        embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
        model = BERTopic(
            embedding_model=embedding_model,
            language="chinese",
            calculate_probabilities=True,
            verbose=False
        )
        return model
    except Exception as e:
        st.warning(f"BERTopic初始化失败: {e}")
        return None


def train_bertopic(texts: List[str], model: Optional[Any] = None) -> tuple:
    """
    训练BERTopic模型提取隐藏主题
    
    返回: (topics, probabilities, model)
    """
    if not BERTOPIC_AVAILABLE:
        st.warning("BERTopic未安装，跳过高级主题分析")
        return None, None, None
    
    if model is None:
        model = get_bertopic_model()
    
    if model is None:
        return None, None, None
    
    try:
        with st.spinner("🤖 正在训练BERTopic模型，提取隐藏主题..."):
            topics, probs = model.fit_transform(texts)
        return topics, probs, model
    except Exception as e:
        st.warning(f"主题提取失败: {e}")
        return None, None, None


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
