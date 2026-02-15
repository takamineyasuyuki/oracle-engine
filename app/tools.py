"""
Oracle Engine - Phase 1: External Tools
DuckDuckGo search integration for real-time trend discovery
"""
import logging
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class TrendSearchEngine:
    """Real-time trend discovery using DuckDuckGo"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search_latest_ai_business_trends(
        self,
        year: int = 2026,
        month: str = "February",
        max_results: int = 10
    ) -> List[Dict[str, str]]:
        """
        Search for the latest AI business and side-hustle trends
        
        Args:
            year: Target year
            month: Target month
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and link
        """
        queries = [
            f"AI副業 {year}年 最新トレンド",
            f"AI automation business {year} {month}",
            f"AI副業 稼ぎ方 {year}",
            f"AI agent business opportunities {year}",
            "ChatGPT API ビジネス 自動化",
            f"AI video generation business {year}",
            "SNS自動化 AI ツール",
        ]
        
        all_results = []
        seen_titles = set()
        
        for query in queries:
            try:
                logger.info(f"Searching: {query}")
                results = self.ddgs.text(query, max_results=5)
                
                for result in results:
                    title = result.get('title', '')
                    
                    # Deduplicate by title
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        all_results.append({
                            'title': title,
                            'snippet': result.get('body', ''),
                            'link': result.get('href', ''),
                            'query': query
                        })
                        
                        if len(all_results) >= max_results:
                            break
                            
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue
            
            if len(all_results) >= max_results:
                break
        
        logger.info(f"Found {len(all_results)} unique trend results")
        return all_results[:max_results]
    
    def search_device_specific_tools(
        self,
        device_type: str,
        max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search for device-specific automation tools
        
        Args:
            device_type: "PC" or "MOBILE"
            max_results: Maximum results
            
        Returns:
            List of tool recommendations
        """
        if device_type == "PC":
            queries = [
                "Python automation tools for business 2026",
                "AI API integration Python tutorial",
                "自動化ツール Python ビジネス",
            ]
        else:
            queries = [
                "cloud automation tools no-code 2026",
                "スマホ完結 AI副業 ツール",
                "mobile-first AI automation platforms",
            ]
        
        results = []
        
        for query in queries:
            try:
                search_results = self.ddgs.text(query, max_results=2)
                results.extend([
                    {
                        'title': r.get('title', ''),
                        'snippet': r.get('body', ''),
                        'link': r.get('href', '')
                    }
                    for r in search_results
                ])
            except Exception as e:
                logger.warning(f"Device tool search failed: {e}")
                continue
        
        return results[:max_results]


def calculate_trend_relevance(
    trend: Dict[str, str],
    archetype: str,
    device: str
) -> float:
    """
    Calculate relevance score for a trend based on archetype and device
    
    Args:
        trend: Trend data with title and snippet
        archetype: User's business archetype
        device: User's device type
        
    Returns:
        Relevance score (0.0 - 1.0)
    """
    score = 0.5  # Base score
    
    text = f"{trend.get('title', '')} {trend.get('snippet', '')}".lower()
    
    # Archetype-specific keywords
    archetype_keywords = {
        'ARCHITECT': ['システム', 'architecture', 'design', 'framework', '設計'],
        'COMMANDER': ['management', 'leadership', 'scale', 'team', '統率'],
        'HACKER': ['experiment', 'hack', 'growth', 'viral', 'グロース'],
        'VISIONARY': ['future', 'vision', 'impact', 'innovation', 'ビジョン'],
        'CREATOR': ['content', 'creative', 'art', 'design', 'クリエイティブ'],
        'GUARDIAN': ['reliable', 'stable', 'proven', '安定', '堅実'],
        'PERFORMER': ['social', 'engagement', 'audience', 'SNS', 'インフルエンサー'],
        'CRAFTSMAN': ['skill', 'craft', 'quality', '職人', '技術'],
    }
    
    # Device-specific keywords
    device_keywords = {
        'PC': ['python', 'code', 'API', 'automation', 'script'],
        'MOBILE': ['app', 'cloud', 'no-code', 'browser', 'クラウド'],
    }
    
    # Calculate archetype match
    if archetype in archetype_keywords:
        matches = sum(1 for kw in archetype_keywords[archetype] if kw in text)
        score += min(matches * 0.1, 0.3)
    
    # Calculate device match
    device_key = 'PC' if 'PC' in device else 'MOBILE'
    if device_key in device_keywords:
        matches = sum(1 for kw in device_keywords[device_key] if kw in text)
        score += min(matches * 0.1, 0.2)
    
    return min(score, 1.0)
