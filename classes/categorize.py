def categorize_text(text):
    categories = {
        "genre": ["action", "thriller", "comedy", "drama"],
        "director": ["director", "directed by"],
        "runtime": ["runtime", "minutes"],
        "title": ["title", "movie", "film"],
        "release_year": ["release", "year", "released"],
        "rating": ["rating", "rated"],
        "cast": ["cast", "starring", "featuring"],
        "plot": ["plot", "synopsis", "summary"],
    }
    results = {}
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                results[category] = keyword
                break
    return results