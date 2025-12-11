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
