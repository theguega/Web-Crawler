import bs4


def tag_count(content: bs4.BeautifulSoup) -> int | None:
    try:
        body = content.body
        if body:
            return sum(1 for _ in body.descendants)
        return 0
    except AttributeError as e:
        print("Failed to retrieve the webpage:", e)
        return 0
