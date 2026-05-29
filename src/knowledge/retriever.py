"""
知识检索服务
整合多引擎搜索、学术检索、向量检索
"""

from typing import Optional

from src.agent.state import KnowledgeSource
from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class KnowledgeRetriever:
    """知识检索器 - 多源医学知识检索"""

    def __init__(self):
        self._tavily_key = settings.tavily_api_key

    async def search_web(self, query: str, max_results: int = 5) -> list[KnowledgeSource]:
        """
        Web 搜索（通过 Tavily API）
        """
        if not self._tavily_key:
            logger.warning("Tavily API Key 未配置，跳过 Web 搜索")
            return []

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self._tavily_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": max_results,
                        "include_domains": ["pubmed.ncbi.nlm.nih.gov", "mayoclinic.org", "msdmanuals.cn"],
                    },
                )
                data = response.json()

                results = []
                for item in data.get("results", []):
                    results.append(KnowledgeSource(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source_type="web",
                        relevance_score=item.get("score", 0.0),
                    ))

                logger.info(f"Web 搜索完成: query={query}, results={len(results)}")
                return results

        except Exception as e:
            logger.error(f"Web 搜索失败: {e}")
            return []

    async def search_academic(self, query: str, max_results: int = 5) -> list[KnowledgeSource]:
        """
        学术搜索（PubMed / Semantic Scholar）
        """
        try:
            import httpx

            # PubMed E-utilities API
            async with httpx.AsyncClient(timeout=30) as client:
                # 搜索
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance",
                }
                search_resp = await client.get(search_url, params=params)
                search_data = search_resp.json()

                id_list = search_data.get("esearchresult", {}).get("idlist", [])
                if not id_list:
                    return []

                # 获取摘要
                fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json",
                }
                fetch_resp = await client.get(fetch_url, params=fetch_params)
                fetch_data = fetch_resp.json()

                results = []
                for pmid in id_list:
                    article = fetch_data.get("result", {}).get(pmid, {})
                    results.append(KnowledgeSource(
                        title=article.get("title", ""),
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        snippet=article.get("elocationid", ""),
                        source_type="academic",
                        relevance_score=0.8,
                    ))

                logger.info(f"学术搜索完成: query={query}, results={len(results)}")
                return results

        except Exception as e:
            logger.error(f"学术搜索失败: {e}")
            return []

    async def retrieve(self, query: str) -> list[KnowledgeSource]:
        """
        综合检索：并行执行 Web 搜索和学术搜索
        """
        import asyncio

        web_task = asyncio.create_task(self.search_web(query))
        academic_task = asyncio.create_task(self.search_academic(query))

        web_results, academic_results = await asyncio.gather(web_task, academic_task)

        all_results = web_results + academic_results
        logger.info(f"综合检索完成: query={query}, total={len(all_results)}")
        return all_results


# 全局单例
knowledge_retriever = KnowledgeRetriever()
