import requests
from dotenv import load_dotenv

load_dotenv()

def paper_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search academic papers using Semantic Scholar API.
    """
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,year,abstract,url,citationCount"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for paper in data.get("data", []):
            authors = [a.get("name", "") for a in paper.get("authors", [])]
            results.append({
                "title": paper.get("title", "No title"),
                "authors": authors,
                "year": paper.get("year", "Unknown"),
                "abstract": paper.get("abstract", "No abstract available"),
                "url": paper.get("url", ""),
                "citations": paper.get("citationCount", 0)
            })

        return results

    except Exception as e:
        return [{"error": f"Paper search failed: {str(e)}"}]


def format_paper_results(results: list[dict]) -> str:
    """
    Format paper results into readable text for agents.
    """
    if not results:
        return "No papers found."

    if "error" in results[0]:
        return f"Paper search error: {results[0]['error']}"

    formatted = []
    for i, p in enumerate(results, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        formatted.append(
            f"[{i}] {p['title']} ({p['year']})\n"
            f"    Authors: {authors}\n"
            f"    Citations: {p['citations']}\n"
            f"    {p['abstract'][:250]}...\n"
            f"    URL: {p['url']}\n"
        )

    return "\n".join(formatted)