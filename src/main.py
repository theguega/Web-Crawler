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
#options.add_argument("--headless=new")
driver = Chrome(options=options)


# ------------------------ Fonctions utilitaires ------------------------


# Fonction pour récupérer le titre d'une page
def get_page_title(parser):
    title_tag = parser.find("title")
    return title_tag.text if title_tag else "Titre non trouvé"

def get_extension(url):
    if url[-1] == '/':
        return "htlm"
    
    # Trouver la dernière occurrence du caractère '.' dans l'URL
    dot_index = url.rfind('.')
    
    # Si aucun '.' n'est trouvé dans l'URL, renvoyer une chaîne vide
    if dot_index == -1:
        return ""
    
    # Extraire l'extension du fichier en utilisant le reste de l'URL après le dernier '.'
    extension = url[dot_index + 1:]
    
    # Si l'extension contient des paramètres de requête, les supprimer
    if '?' in extension:
        extension = extension[:extension.index('?')]

    if "jsf" in extension:
        return "jsf"
    
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
        if href and (href[0] != "#") and not href.startswith("mailto:") and not href.startswith("tel:"):
            # si le lien est relatif
            if ("http" or "https") not in href:
                full_link = urljoin(page_url, href)
                #distinction site interne / externe à l'ent
                if "https://webapplis.utc.fr" not in full_link:
                    result.append((full_link,0))
                else:
                    result.append((full_link,1))
            # sinon
            else:
                #distinction site interne / externe à l'ent
                if "https://webapplis.utc.fr" not in href:
                    result.append((href,0))
                else:
                    result.append((href,1))
    return result


# Fonction pour scraper les pages en profondeur
def scrape_page(url, depth=0, source=None):
    # Si la page à déjà été visitée, on ne la traite pas
    if url in visited_pages:
        return
    
    # provisoir pur les tests
    if depth > 2 :
        print("depth > 2")
        return
    
    # Ajouter la page à la liste des pages visitées
    visited_pages.add(url)
    
    #on récupère les infos de la page pour ajouter un noeud au graphe
    extension = get_extension(url)
    print(extension)
    G.add_node(url, extension=extension, depth=depth)

    # Scrapping de la page ----------------------------------------------
    # On ne traite que les pages de l'ENT
    if "https://webapplis.utc.fr" not in url:
        return
    #On ne scrap pas les pdf, docx etc..
    if extension in blacklist:
        return

    # Si la page n'a pas de titre, on ne la traite pas
    if not driver.title or driver.title == "404 Not Found":
        return
    
    driver.get(url)
    parser = BeautifulSoup(driver.page_source, "html.parser")
    
    title = get_page_title(parser)
    links = get_links(parser, url) # retourne une liste de tuple (url, internal) ave internal = 1 si le lien est interne à l'ent
    words = word_count(parser)
    tags = tag_count(parser)

    # Ajout des données dans le graph
    G.add_node(url, title=title, extension=extension, word_count=words[0], tag_count=tags, depth=depth)
    if source:
        G.add_edge(source, url)

    #print(f"{'  ' * depth} - {title} ({len(links)} liens, {words[0]} mots, {tags} balises)")

    # Appel récursif pour les pages en dessous
    for link in links:
        scrape_page(link[0], depth + 1, url)


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

# Find login elements
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

# Input login credentials
username_field.send_keys(credentials["username"])
password_field.send_keys(credentials["password"])
login_button.click()

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
