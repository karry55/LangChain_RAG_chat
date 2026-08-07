"""高级检索器: 向量检索 + MMR 去重"""
from typing import List
from langchain_core.documents import Document
from loguru import logger

from app.core.config import get_settings
from app.rag.embedder import embed_texts
from app.rag.vector_store import similarity_search_with_score

settings = get_settings()


class AdvancedRetriever:
    """高级检索器，组合多种策略提升检索质量"""

    def __init__(self):
        self.top_k = settings.retrieval_top_k
        self.fetch_k = settings.mmr_fetch_k
        self.lambda_mult = settings.mmr_lambda_mult
        self.final_k = settings.final_top_k

    def retrieve(self, query: str) -> List[tuple]:
        """执行检索流程: 向量检索 → MMR → 返回结果

        Returns:
            List[(Document, float)]: (文档, 相似度分数) 列表
        """
        # Step 1: 初检 - 语义检索 Top-K
        logger.info(f"检索: Top-{self.fetch_k} 初检")
        results = similarity_search_with_score(query, k=self.fetch_k)

        if not results:
            logger.warning("未检索到任何结果")
            return []

        # Step 2: MMR 去重
        logger.info(f"MMR 去重: {len(results)} → {self.final_k} (λ={self.lambda_mult})")
        selected = self._mmr_select(
            candidates=results,
            k=self.final_k,
            lambda_mult=self.lambda_mult,
        )

        logger.info(f"检索完成，返回 {len(selected)} 个片段")
        return selected

    def _mmr_select(
        self,
        candidates: List[tuple],
        k: int,
        lambda_mult: float = 0.7,
    ) -> List[tuple]:
        """MMR (Maximal Marginal Relevance) 算法

        在相关性和多样性之间平衡:
        - lambda_mult 趋近 1: 更注重相关性
        - lambda_mult 趋近 0: 更注重多样性

        优化: 一次性批嵌入所有候选文本，避免 O(k*n) 次 API 调用
        """
        n = len(candidates)
        if n <= k:
            return candidates

        # 批嵌入所有候选文本（一次 API 调用，含缓存）
        try:
            texts = [doc.page_content for doc, _ in candidates]
            candidate_vecs = embed_texts(texts)
        except Exception as e:
            logger.warning(f"批嵌入失败，回退到按分数排序: {e}")
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:k]

        selected = []
        remaining = list(range(n))

        # 首次选择：相关性最高的
        best_idx = max(remaining, key=lambda i: candidates[i][1])
        selected.append(best_idx)
        remaining.remove(best_idx)

        # 贪心选择：平衡相关性和多样性
        for _ in range(k - 1):
            if not remaining:
                break

            best_score = float("-inf")
            best_idx = remaining[0]

            for i in remaining:
                # 相关性得分（来自向量检索）
                relevance = candidates[i][1]
                # 多样性惩罚：与已选中文档的最大相似度
                max_sim = max(
                    self._cosine_similarity(candidate_vecs[i], candidate_vecs[s])
                    for s in selected
                )
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            selected.append(best_idx)
            remaining.remove(best_idx)

        return [candidates[i] for i in selected]

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        import math
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
