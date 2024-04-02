from urllib.parse import urljoin
import networkx as nx
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from login import credentials

from word_count import word_count
from tag_count import tag_count


# ------------------------ Fonctions utilitaires ------------------------


def get_extension(url: str) -> str:
    # Trouver la dernière occurrence du caractère '.' dans l'URL
    dot_index = url.rfind(".")

    # Si aucun '.' n'est trouvé dans l'URL, c'est une page html
    if dot_index == -1:
        return "html"

    # Extraire l'extension du fichier en utilisant le reste de l'URL après le dernier '.'
    extension = url[dot_index + 1 :]

    # Si l'extension contient un '/', c'est une page html
    if "/" in extension:
        extension = "html"

    # Si l'extension contient des paramètres de requête, les supprimer
    if "?" in extension:
        extension = extension[: extension.index("?")]
        return "jsf"

    return extension


def format_url(url: str) -> str:
    if url[-1] == "/":
        return url[:-1]
    return url


# ------------------------ Fonctions de scrapping ------------------------


# Fonction pour récupérer les liens d'une page avec filtrage
def get_links(parser: BeautifulSoup, page_url: str) -> list[tuple[str, int]]:
    # retourne une liste de tuple (url, internal) avec internal = 1 si le lien est interne à l'ent
    # Traitement de la page cible
    links = parser.find_all("a")
    result = []

    # on recupere le lien absolu
    for link in links:
        href = link.get("href")
        if (
            href
            and (href[0] != "#")
            and not href.startswith("mailto:")
            and not href.startswith("tel:")
        ):
            # si le lien est relatif
            if ("http" or "https") not in href:
                full_link = urljoin(page_url, href)
                # distinction site interne / externe à l'ent
                if BASE_LINK not in full_link:
                    result.append((format_url(full_link), 0))
                else:
                    result.append((format_url(full_link), 1))
            # sinon
            else:
                # distinction site interne / externe à l'ent
                if BASE_LINK not in href:
                    result.append((format_url(href), 0))
                else:
                    result.append((format_url(href), 1))
    return result


# Fonction pour scraper les pages en profondeur
def scrape_page(url: str) -> None:
    url = format_url(url)
    # Si la page à déjà été visitée, on ne la traite pas
    if url in visited_pages:
        return

    # Ajouter la page à la liste des pages visitées
    visited_pages.add(url)

    print(G.number_of_nodes(), "pages scrappés, page actuelle : ", url)

    # On ne traite que les pages de l'ENT
    if BASE_LINK not in url:
        return

    extension = get_extension(url)

    # On ne scrap pas les pdf, docx etc..
    if extension in blacklist:
        return

    # Scrapping
    driver.get(url)
    parser = BeautifulSoup(driver.page_source, "html.parser")
    links = get_links(parser, url)

    if len(links) == 0:
        return

    # Si la page est scrappable, on ajoute d'autres infos dans le graphe
    words = word_count(parser)[0]
    tags = tag_count(parser)
    G.add_node(
        url,
        title=driver.title,
        nb_words=words,
        nb_tags=tags,
        nb_links=len(links),
        internal=1,
        extension=extension,
    )  # add_note ne créer pas de doublon mais va actualiser les valeurs si le noeud existe déjà

    # Appel récursif pour les pages en dessous
    for link in links:
        extension = get_extension(link[0])
        G.add_node(format_url(link[0]), extension=extension, internal=link[1])
        G.add_edge(url, format_url(link[0]))
        scrape_page(link[0])


# ---------------------- Préparations préliminaires ----------------------


# Créer un graphe NetworkX
G = nx.DiGraph()

# Charger la liste noire des extensions à partir du fichier
with open("src/blacklist.txt", "r", encoding="utf-8") as file:
    blacklist = {line.strip() for line in file}

visited_pages = set()

# ------------------------ Connexion ------------------------

options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")
driver = Chrome(options=options)

# BASE_LINK = "https://www.ecoindex.fr"
BASE_LINK = "https://webapplis.utc.fr"
LOGIN_URL = "https://cas.utc.fr/cas/login.jsf"
TARGET_URL = "https://webapplis.utc.fr/ent/index.jsf"

# """

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

# """

# ------------------------ Scrapping ------------------------

# Vérifier si la connexion a réussi
if "Authentication failed" in driver.page_source:
    print("Échec de la connexion. Vérifiez vos identifiants.")
else:
    # Scraper la page cible et ses liens en profondeur
    scrape_page(url=TARGET_URL)

# Exporter le graphe au format GraphML
print("Export du graphe")
nx.write_graphml(G, "ent.graphml")
print("Graph exporté avec succès.")

# Fermer la session
driver.quit()
