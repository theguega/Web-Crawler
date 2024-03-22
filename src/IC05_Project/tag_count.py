import bs4
import requests
from bs4 import BeautifulSoup


def tag_count(content: bs4.BeautifulSoup) -> int | None:
    try:
        body = content.body
        if body:
            print(f"nb balises : {len(body.find_all())}")
            return len(list(body.descendants))
        return None
    except Exception as e:
        print("La requête a échoué avec le code :", e)
        return None


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
# print(tag_count(soup))
