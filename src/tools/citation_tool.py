def format_citation(source: dict, index: int) -> str:
    """
    Format a single source as an APA-style citation.
    """
    # For web sources
    if "url" in source and "authors" not in source:
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        return f"[{index}] {title}. Retrieved from {url}"

    # For academic papers
    authors = source.get("authors", [])
    if isinstance(authors, list):
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += " et al."
    else:
        author_str = authors

    year = source.get("year", "n.d.")
    title = source.get("title", "Untitled")
    url = source.get("url", "")

    return f"[{index}] {author_str} ({year}). {title}. {url}"


def format_citations_list(sources: list[dict]) -> str:
    """
    Format a list of sources into a numbered citations section.
    """
    if not sources:
        return "No sources available."

    citations = ["## References\n"]
    for i, source in enumerate(sources, 1):
        citations.append(format_citation(source, i))

    return "\n".join(citations)