"""
EarnFlow 智能任务匹配引擎模块 / Intelligent Task Matching Engine Module

提供基于关键词、分类和标签的任务匹配与评分功能。
实现简化的TF-IDF评分算法用于关键词匹配。
Provides task matching and scoring based on keywords, categories, and tags.
Implements a simplified TF-IDF scoring algorithm for keyword matching.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

from earnflow.models import Task, TaskCategory, TaskPriority, PRIORITY_WEIGHTS
from earnflow.utils import clamp


# ============================================================
# 文本处理工具 / Text Processing Utilities
# ============================================================


def tokenize(text: str) -> List[str]:
    """
    简单分词 / Simple tokenization

    将文本转换为小写token列表，支持中英文混合。
    Convert text to lowercase token list, supporting mixed Chinese and English.

    Args:
        text: 输入文本 / Input text

    Returns:
        token列表 / Token list
    """
    # 英文分词 / English tokenization
    english_tokens = re.findall(r"[a-zA-Z]+", text.lower())
    # 中文按字符分词（简化处理）/ Chinese character-level tokenization (simplified)
    chinese_tokens = list(re.findall(r"[\u4e00-\u9fff]", text))
    return english_tokens + chinese_tokens


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """
    计算词频（Term Frequency）/ Compute Term Frequency

    Args:
        tokens: token列表 / Token list

    Returns:
        词频字典 / Term frequency dictionary
    """
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {word: count / total for word, count in counts.items()}


def compute_idf(documents: List[List[str]]) -> Dict[str, float]:
    """
    计算逆文档频率（Inverse Document Frequency）/ Compute IDF

    Args:
        documents: 文档列表（每个文档是token列表）/ Document list (each doc is a token list)

    Returns:
        IDF字典 / IDF dictionary
    """
    if not documents:
        return {}

    total_docs = len(documents)
    doc_freq: Counter = Counter()

    for doc_tokens in documents:
        unique_tokens = set(doc_tokens)
        for token in unique_tokens:
            doc_freq[token] += 1

    # 使用平滑的IDF公式 / Use smoothed IDF formula
    return {
        word: math.log((total_docs + 1) / (freq + 1)) + 1
        for word, freq in doc_freq.items()
    }


def compute_tfidf(
    tokens: List[str],
    tf: Dict[str, float],
    idf: Dict[str, float],
) -> Dict[str, float]:
    """
    计算TF-IDF值 / Compute TF-IDF values

    Args:
        tokens: token列表 / Token list
        tf: 词频字典 / Term frequency dictionary
        idf: IDF字典 / IDF dictionary

    Returns:
        TF-IDF字典 / TF-IDF dictionary
    """
    return {word: tf_val * idf.get(word, 1.0) for word, tf_val in tf.items()}


# ============================================================
# 任务匹配引擎 / Task Matching Engine
# ============================================================


class TaskMatcher:
    """
    智能任务匹配引擎 / Intelligent Task Matching Engine

    基于关键词TF-IDF评分、分类匹配和标签匹配进行综合评分。
    Performs comprehensive scoring based on keyword TF-IDF, category matching, and tag matching.

    Attributes:
        keyword_weight: 关键词匹配权重 / Keyword matching weight
        category_weight: 分类匹配权重 / Category matching weight
        tag_weight: 标签匹配权重 / Tag matching weight
        priority_bonus: 优先级加分 / Priority bonus
    """

    def __init__(
        self,
        keyword_weight: float = 0.4,
        category_weight: float = 0.3,
        tag_weight: float = 0.3,
        priority_bonus: float = 5.0,
    ) -> None:
        """
        初始化匹配引擎 / Initialize matching engine

        Args:
            keyword_weight: 关键词权重 / Keyword weight
            category_weight: 分类权重 / Category weight
            tag_weight: 标签权重 / Tag weight
            priority_bonus: 优先级加分 / Priority bonus
        """
        self.keyword_weight = keyword_weight
        self.category_weight = category_weight
        self.tag_weight = tag_weight
        self.priority_bonus = priority_bonus

        # 归一化权重 / Normalize weights
        total = keyword_weight + category_weight + tag_weight
        if total > 0:
            self.keyword_weight /= total
            self.category_weight /= total
            self.tag_weight /= total

        # 缓存IDF数据 / Cached IDF data
        self._idf_cache: Optional[Dict[str, float]] = None
        self._reference_docs: List[List[str]] = []

    def _build_idf_index(self, tasks: List[Task]) -> None:
        """
        构建IDF索引 / Build IDF index

        Args:
            tasks: 任务列表 / Task list
        """
        self._reference_docs = []
        for task in tasks:
            text = f"{task.title} {task.description} {' '.join(task.tags)}"
            tokens = tokenize(text)
            if tokens:
                self._reference_docs.append(tokens)
        self._idf_cache = compute_idf(self._reference_docs)

    def _keyword_score(self, query_tokens: List[str], task: Task) -> float:
        """
        计算关键词匹配分数 / Calculate keyword matching score

        使用简化的TF-IDF余弦相似度。
        Uses simplified TF-IDF cosine similarity.

        Args:
            query_tokens: 查询token列表 / Query token list
            task: 任务 / Task

        Returns:
            关键词匹配分数（0-100）/ Keyword matching score (0-100)
        """
        if not query_tokens:
            return 0.0

        # 任务文档token / Task document tokens
        task_text = f"{task.title} {task.description} {' '.join(task.tags)}"
        task_tokens = tokenize(task_text)

        if not task_tokens:
            return 0.0

        # 计算TF / Compute TF
        query_tf = compute_tf(query_tokens)
        task_tf = compute_tf(task_tokens)

        # 使用缓存的IDF或默认值 / Use cached IDF or defaults
        idf = self._idf_cache or {}
        for token in set(query_tokens + task_tokens):
            if token not in idf:
                idf[token] = 1.0

        # 计算TF-IDF向量 / Compute TF-IDF vectors
        query_tfidf = compute_tfidf(query_tokens, query_tf, idf)
        task_tfidf = compute_tfidf(task_tokens, task_tf, idf)

        # 余弦相似度 / Cosine similarity
        all_tokens = set(query_tfidf.keys()) | set(task_tfidf.keys())
        dot_product = sum(query_tfidf.get(t, 0) * task_tfidf.get(t, 0) for t in all_tokens)

        query_norm = math.sqrt(sum(v ** 2 for v in query_tfidf.values()))
        task_norm = math.sqrt(sum(v ** 2 for v in task_tfidf.values()))

        if query_norm == 0 or task_norm == 0:
            return 0.0

        similarity = dot_product / (query_norm * task_norm)
        return clamp(similarity * 100, 0, 100)

    def _category_score(self, query_category: Optional[TaskCategory], task: Task) -> float:
        """
        计算分类匹配分数 / Calculate category matching score

        Args:
            query_category: 查询分类 / Query category
            task: 任务 / Task

        Returns:
            分类匹配分数（0-100）/ Category matching score (0-100)
        """
        if query_category is None:
            return 50.0  # 未指定分类时返回中间值 / Return middle value when no category specified
        return 100.0 if task.category == query_category else 0.0

    def _tag_score(self, query_tags: List[str], task: Task) -> float:
        """
        计算标签匹配分数 / Calculate tag matching score

        Args:
            query_tags: 查询标签列表 / Query tag list
            task: 任务 / Task

        Returns:
            标签匹配分数（0-100）/ Tag matching score (0-100)
        """
        if not query_tags:
            return 50.0

        if not task.tags:
            return 0.0

        query_set = set(t.lower() for t in query_tags)
        task_set = set(t.lower() for t in task.tags)
        intersection = query_set & task_set

        if not query_set:
            return 0.0

        return (len(intersection) / len(query_set)) * 100

    def _priority_score(self, task: Task) -> float:
        """
        计算优先级加分 / Calculate priority bonus

        Args:
            task: 任务 / Task

        Returns:
            优先级加分 / Priority bonus
        """
        weight = PRIORITY_WEIGHTS.get(task.priority, 1)
        return (weight / 4) * self.priority_bonus

    def match(
        self,
        query: str,
        tasks: List[Task],
        category: Optional[TaskCategory] = None,
        tags: Optional[List[str]] = None,
        top_n: int = 10,
    ) -> List[Tuple[Task, float]]:
        """
        匹配任务 / Match tasks

        根据查询条件对任务进行综合评分和排序。
        Score and rank tasks based on query conditions.

        Args:
            query: 查询文本 / Query text
            tasks: 候选任务列表 / Candidate task list
            category: 目标分类（可选）/ Target category (optional)
            tags: 目标标签（可选）/ Target tags (optional)
            top_n: 返回前N个结果 / Return top N results

        Returns:
            排序后的(任务, 分数)列表 / Sorted (task, score) list
        """
        if not tasks:
            return []

        # 构建IDF索引 / Build IDF index
        self._build_idf_index(tasks)

        # 分词查询 / Tokenize query
        query_tokens = tokenize(query)
        query_tags = tags or []

        # 计算每个任务的综合分数 / Calculate composite score for each task
        scored: List[Tuple[Task, float]] = []
        for task in tasks:
            kw_score = self._keyword_score(query_tokens, task)
            cat_score = self._category_score(category, task)
            tag_score = self._tag_score(query_tags, task)
            pri_score = self._priority_score(task)

            # 加权综合分 / Weighted composite score
            composite = (
                self.keyword_weight * kw_score
                + self.category_weight * cat_score
                + self.tag_weight * tag_score
                + pri_score
            )
            composite = clamp(composite, 0, 100)
            scored.append((task, round(composite, 2)))

        # 按分数降序排序 / Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def match_single(
        self,
        query: str,
        task: Task,
        category: Optional[TaskCategory] = None,
        tags: Optional[List[str]] = None,
    ) -> float:
        """
        对单个任务进行匹配评分 / Score a single task

        Args:
            query: 查询文本 / Query text
            task: 任务 / Task
            category: 目标分类 / Target category
            tags: 目标标签 / Target tags

        Returns:
            匹配分数（0-100）/ Match score (0-100)
        """
        results = self.match(query, [task], category, tags, top_n=1)
        if results:
            return results[0][1]
        return 0.0

    def filter_by_score(
        self,
        query: str,
        tasks: List[Task],
        min_score: float = 30.0,
        category: Optional[TaskCategory] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Tuple[Task, float]]:
        """
        过滤并返回达到最低分数的任务 / Filter and return tasks meeting minimum score

        Args:
            query: 查询文本 / Query text
            tasks: 任务列表 / Task list
            min_score: 最低匹配分数 / Minimum match score
            category: 目标分类 / Target category
            tags: 目标标签 / Target tags

        Returns:
            过滤后的(任务, 分数)列表 / Filtered (task, score) list
        """
        results = self.match(query, tasks, category, tags)
        return [(task, score) for task, score in results if score >= min_score]
