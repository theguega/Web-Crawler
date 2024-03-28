from urllib.parse import urljoin
import networkx as nx
from bs4 import BeautifulSoup

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
options.add_argument("--headless=new")
driver = Chrome(options=options)


# ------------------------ Fonctions utilitaires ------------------------


# Fonction pour récupérer le titre d'une page
def get_page_title(parser : BeautifulSoup) -> str:
    title_tag = parser.find("title")
    return title_tag.text if title_tag else "None"

def get_extension(url : str) -> str:
    # Trouver la dernière occurrence du caractère '.' dans l'URL
    dot_index = url.rfind('.')
    
    # Si aucun '.' n'est trouvé dans l'URL, c'est une page html
    if dot_index == -1:
        return "html"
    
    # Extraire l'extension du fichier en utilisant le reste de l'URL après le dernier '.'
    extension = url[dot_index + 1:]

    # Si l'extension contient un '/', c'est une page html
    if '/' in extension:
        extension = "html"
    
    # Si l'extension contient des paramètres de requête, les supprimer
    if '?' in extension:
        extension = extension[:extension.index('?')]
        return "jsf"
    
    return extension



# ------------------------ Fonctions de scrapping ------------------------


# Fonction pour récupérer les liens d'une page avec filtrage
def get_links(parser : BeautifulSoup, page_url : str) -> list[tuple[str, int]]: 
    # retourne une liste de tuple (url, internal) avec internal = 1 si le lien est interne à l'ent
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
def scrape_page(url : str, depth:int=0, source:str=None) -> None:
    # Si la page à déjà été visitée, on ne la traite pas
    if url in visited_pages:
        return
    
    # Ajouter la page à la liste des pages visitées
    visited_pages.add(url)
    global nb
    nb+=1
    print(nb, "pages scrappés")
    
    #on récupère les infos de la page pour ajouter un noeud au graphe
    extension = get_extension(url)
    #print(f"{'  ' * depth} - {url} extension : {extension}")
    G.add_node(url, extension=extension, depth=depth)
    if source:
        G.add_edge(source, url)

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
    links = get_links(parser, url)
    words = word_count(parser)
    tags = tag_count(parser)


    # Ajout des données dans le graph
    G.add_node(url, title=title, extension=extension, word_count=words[0], tag_count=tags, depth=depth)

    # Appel récursif pour les pages en dessous
    for link in links:
        scrape_page(url=link[0], depth=depth + 1, source=url)


# ------------------------ Connexion + Scrapping ------------------------


# Initialiser l'ensemble des pages visitées
global visited_pages
global nb

visited_pages = set()
nb=0

# Soumettre le formulaire de connexion
# URL de la page de connexion
LOGIN_URL = "https://cas.utc.fr/cas/login.jsf"
# URL de la page à scraper après la connexion
TARGET_URL = "https://webapplis.utc.fr/ent/index.jsf"

driver.implicitly_wait(5)
driver.get(TARGET_URL)

# Find login elements
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
driver.maximize_window()

# Input login credentials
username_field.send_keys(credentials["username"])
password_field.send_keys(credentials["password"])
login_button.click()

# Vérifier si la connexion a réussi
if "Authentication failed" in driver.page_source:
    print("Échec de la connexion. Vérifiez vos identifiants.")
else:
    # Scraper la page cible et ses liens en profondeur
    scrape_page(url=TARGET_URL, depth=0)

# Exporter le graphe au format GraphML
nx.write_graphml(G, "graph.graphml")

# Fermer la session
driver.quit()
