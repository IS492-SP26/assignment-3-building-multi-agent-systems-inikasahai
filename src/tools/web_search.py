import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily and return structured results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not set in .env"}]

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            include_answer=True
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", "No title"),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0.0)
            })

        return results

    except Exception as e:
        return [{"error": f"Web search failed: {str(e)}"}]


def format_search_results(results: list[dict]) -> str:
    """
    Format search results into readable text for agents.
    """
    if not results:
        return "No results found."

    if "error" in results[0]:
        return f"Search error: {results[0]['error']}"

    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[{i}] {r['title']}\n"
            f"    URL: {r['url']}\n"
            f"    {r['content'][:300]}...\n"
        )

    return "\n".join(formatted)
