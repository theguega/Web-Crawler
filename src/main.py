from urllib.parse import urljoin
import time
import networkx as nx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from src.login import credentials
from src.word_count import word_count
from src.tag_count import tag_count


# ---------------------- Préparations préliminaires ----------------------


# Créer un graphe NetworkX
G = nx.Graph()

# Charger la liste noire des extensions à partir du fichier
with open("blacklist.txt", "r") as file:
    blacklist = {line.strip() for line in file}

options = webdriver.ChromeOptions()
options.page_load_strategy = "none"
# options.add_argument("--headless=new")
driver = Chrome(options=options)


# ------------------------ Fonctions utilitaires ------------------------


# Fonction pour récupérer le titre d'une page
def get_page_title(url):
    driver.get(url)
    time.sleep(3)
    page_soup = BeautifulSoup(driver.page_source, "html.parser")
    title_tag = page_soup.find("title")
    return title_tag.text if title_tag else "Titre non trouvé"


# ------------------------ Fonctions de scrapping ------------------------


# Fonction pour récupérer les liens d'une page avec filtrage
def get_links(page_url):
    driver.get(page_url)
    time.sleep(3)
    # Traitement de la page cible
    index_page = BeautifulSoup(driver.page_source, "html.parser")
    links = index_page.find_all("a")
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

    # On ne traite que les pages de l'ENT
    if "https://webapplis.utc.fr" not in url:
        return

    # On ne traite pas les pages de fichiers (pdf, docx, zip, etc.)
    extension = url.split(".")[-1]
    if extension in blacklist:
        return

    # Ajouter la page à la liste des pages visitées
    visited_pages.add(url)
    print(url)
    driver.get(url)
    time.sleep(3)
    content = BeautifulSoup(driver.page_source, "html.parser")
    print(f"Nombre de mots : {word_count(content)[0]}")
    # print(f"Nombre de couleurs différentes : {len(color_set(url, session))}")
    print(f"Nombre d'éléments sur la page : {tag_count(content)}")
    # Scrapping de la page
    links = get_links(url)

    # Affichage de la page
    """
    title = get_page_title(url)
    print("Informations sur la page : ")
    print(f"Profondeur : from [{source}] -> [{depth}]")
    print(f"Url : [{url}]")
    print(f"Titre : [{title}]")
    print(f"Nombre de liens : [{len(links)}]")
    print(f"Extension : {extension}\n")
    print("\n\n\n------------------------\n\n\n")
    """
    # Ajout de tous les liens présents sur la page dans notre graph
    for link in links:
        G.add_edge(url, link)
        # print(f"    - {link}")

    # Scraper les pages liées en profondeur si elles n'ont pas déjà été visitées
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
time.sleep(5)
# Vérifier si la connexion a réussi
if "Authentication failed" in driver.page_source:
    print("Échec de la connexion. Vérifiez vos identifiants.")
else:
    # Scraper la page cible et ses liens en profondeur
    scrape_page(TARGET_URL, 0, "Main page")

# Exporter le graphe au format GraphML
nx.write_graphml(G, "graph.graphml")

# Fermer la session
driver.quit()
