import bs4


def word_count(content: bs4.BeautifulSoup) -> tuple[int, list[str]] | tuple[None, None]:
    def tag_visible(element: bs4.element.NavigableString) -> bool:
        if (
            element.parent.name
            in [
                "style",
                "script",
                "head",
                "title",
                "meta",
                "[document]",
            ]
            or isinstance(element, bs4.Comment)
            or not element.strip()
        ):
            return False
        return True

    def words_from_html() -> list[str]:
        texts = content.find_all(string=True)
        visible_texts = filter(tag_visible, texts)
        words = [word.strip() for text in visible_texts for word in text.split()]
        return words

    try:
        visible_words = words_from_html()
        count = len(visible_words)
        return count, visible_words
    except Exception as e:
        print("Failed to retrieve the webpage:", e)
        return None, None

