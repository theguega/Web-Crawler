import requests
from bs4 import BeautifulSoup, Comment


def word_count(url: str, session: requests.Session) -> tuple[int, list[str]] | tuple[None, None]:
    def tag_visible(element) -> bool:
        if element.parent.name in [
            "style",
            "script",
            "head",
            "title",
            "meta",
            "[document]",
        ] or isinstance(element, Comment) or not element.strip():
            return False
        return True

    def words_from_html() -> list[str]:
        soup = BeautifulSoup(session.get(url).content, "html.parser")
        texts = soup.findAll(string=True)
        visible_texts = filter(tag_visible, texts)
        words = []
        for text in visible_texts:
            for word in text.split():
                words.append(word.strip())
        return words

    try:
        visible_words = words_from_html()
        count = len(visible_words)
        return count, visible_words
    except Exception as e:
        print("Failed to retrieve the webpage:", e)
        return None, None


# Exemple d'utilisation :
# URL = 'https://webapplis.utc.fr/ent/services/services.jsf?sid=668'
# word_count, visible_words = word_count(URL)
#
# if word_count is not None and visible_words is not None:
#     print("Nombre total de mots visibles:", word_count)
#     print("Liste de tous les mots visibles:")
#     for word in visible_words:
#         print(word)
