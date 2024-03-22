from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from word_count import word_count

options = webdriver.ChromeOptions()
options.page_load_strategy = "none"
#options.add_argument("--headless=new")
driver = Chrome(options=options)

login_url = "https://cas.utc.fr/cas/login.jsf"
# URL de la page à scraper après la connexion
target_url = "https://webapplis.utc.fr/ent/index.jsf"

# Navigate to the login page
driver.get(target_url)
time.sleep(3)
# Find login elements
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")

login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

# Input login credentials
username_field.send_keys("beziatsa")
password_field.send_keys("Gavnie348")

login_button.click()
# time.sleep(3)
# driver.quit()
#
# driver = Chrome(options=options)
# driver.get(target_url)
time.sleep(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
print(word_count(soup))