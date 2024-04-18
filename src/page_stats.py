import bs4


class PageStats:
    @staticmethod
    def word_count(
        content: bs4.BeautifulSoup,
    ) -> tuple[int, list[str]] | tuple[int, None]:
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

        try:
            texts = content.find_all(string=True)
            visible_texts = filter(tag_visible, texts)
            words = [word.strip() for text in visible_texts for word in text.split()]
            count = len(words)
            return count, words
        except Exception as e:
            print("Failed to retrieve the webpage:", e)
            return 0, None

    @staticmethod
    def tag_count(content: bs4.BeautifulSoup) -> int:
        try:
            body = content.body
            if body:
                return sum(1 for _ in body.descendants)
            return 0
        except AttributeError as e:
            print("Failed to retrieve the webpage:", e)
            return 0

