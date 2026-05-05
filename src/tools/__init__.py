"""
Research Tools Module
Contains tools for web search, paper search, citation extraction, etc.
"""

from .web_search import web_search, format_search_results
from .paper_search import paper_search, format_paper_results
from .citation_tool import format_citation, format_citations_list

__all__ = [
    "web_search",
    "format_search_results",
    "paper_search",
    "format_paper_results",
    "format_citation",
    "format_citations_list",
]