import bs4
from bs4 import Comment


def word_count(content: bs4.BeautifulSoup) -> tuple[int, list[str]] | tuple[None, None]:
    def tag_visible(element: bs4.Tag) -> bool:
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
            or isinstance(element, Comment)
            or not element.strip()
        ):
            return False
        return True

    def words_from_html() -> list[str]:
        texts = content.find_all(string=True)
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


# # Pour tester
# import time
# from selenium import webdriver
# from selenium.webdriver import Chrome
# from bs4 import BeautifulSoup
#
# options = webdriver.ChromeOptions()
# options.page_load_strategy = "none"
# options.add_argument("--headless=new")
# driver = Chrome(options=options)
# #driver.implicitly_wait(3)
#
# URL = "https://www.la-spa.fr/"
#
# driver.get(URL)
# time.sleep(3)
#
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# print(word_count(soup))
