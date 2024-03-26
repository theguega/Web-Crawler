import time
import networkx as nx
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from login import credentials

from word_count import word_count
from tag_count import tag_count


# ---------------------- Préparations préliminaires ----------------------


# Créer un graphe NetworkX
G = nx.Graph()

# Charger la liste noire des extensions à partir du fichier
with open("src/blacklist.txt", "r") as file:
    blacklist = {line.strip() for line in file}

options = webdriver.ChromeOptions()
options.page_load_strategy = "none"
#options.add_argument("--headless=new")
driver = Chrome(options=options)


# ------------------------ Fonctions utilitaires ------------------------


# Fonction pour récupérer le titre d'une page
def get_page_title(parser):
    title_tag = parser.find("title")
    return title_tag.text if title_tag else "Titre non trouvé"

def get_extension():
    driver.current_url
    driver.implicitly_wait(2)
    extension = os.path.splitext(driver.current_url)[1]
    return extension


# ------------------------ Fonctions de scrapping ------------------------


# Fonction pour récupérer les liens d'une page avec filtrage
def get_links(parser, page_url):
    # Traitement de la page cible
    links = parser.find_all("a")
    result = []

    # on recupere le lien absolu
    for link in links:
        href = link.get("href")
        if href and (href[0] != "#") and ("null" not in href):
            # si le lien est relatif
            if ("http" or "https") not in href:
                full_link = urljoin(page_url, href)
                result.append(full_link)
            # sinon
            else:
                result.append(href)
    return result


# Fonction pour scraper les pages en profondeur
def scrape_page(url, depth=0, source=None):
    # Vérifier si la page a déjà été visitée
    if url in visited_pages:
        return
    
    if depth > 2 :
        return

    # On ne traite que les pages de l'ENT
    if "https://webapplis.utc.fr" not in url:
        return
    
    extension = get_extension()
    if extension in blacklist:
        return

    # Ajouter la page à la liste des pages visitées
    visited_pages.add(url)

    driver.get(url)
    time.sleep(3)
    parser = BeautifulSoup(driver.page_source, "html.parser")

    # Appel des différentes fonctions de traitement
    title = get_page_title(parser)
    links = get_links(parser, url)
    words = word_count(parser)
    tags = tag_count(parser)

    # Ajout des données dans le graph
    G.add_node(url, title=title, extension=extension, word_count=words[0], tag_count=tags, depth=depth)
    if source:
        G.add_edge(source, url)


    print(f"{'  ' * depth} - {title} ({len(links)} liens, {words[0]} mots, {tags} balises)")

    # Appel récursif pour les pages en dessous
    for link in links:
        scrape_page(link, depth + 1, url)


# ------------------------ Connexion + Scrapping ------------------------


# Initialiser l'ensemble des pages visitées
visited_pages = set()

# Soumettre le formulaire de connexion
# URL de la page de connexion
LOGIN_URL = "https://cas.utc.fr/cas/login.jsf"
# URL de la page à scraper après la connexion
TARGET_URL = "https://webapplis.utc.fr/ent/index.jsf"

driver.implicitly_wait(2)
driver.get(TARGET_URL)
time.sleep(3)

# Find login elements
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

# Input login credentials
username_field.send_keys(credentials["username"])
password_field.send_keys(credentials["password"])
login_button.click()
time.sleep(3)

# Vérifier si la connexion a réussi
if "Authentication failed" in driver.page_source:
    print("Échec de la connexion. Vérifiez vos identifiants.")
else:
    # Scraper la page cible et ses liens en profondeur
    scrape_page(TARGET_URL, 0)

# Exporter le graphe au format GraphML
nx.write_graphml(G, "graph.graphml")

# Fermer la session
driver.quit()
