import time
from urllib.parse import urljoin
import networkx as nx
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from page_stats import PageStats


class Scraper:
    with open("src/blacklist.txt", "r", encoding="utf-8") as file:
        blacklist = {line.strip() for line in file}
    driver = webdriver.Chrome()

    def __init__(
        self,
        target_url: str = "https://webapplis.utc.fr/ent/index.jsf",
        base_link: str = "https://webapplis.utc.fr",
        login_required: bool = True,
        username_id: str = "username",
        password_id: str = "password",
        login_button_xpath: str = "//button[@type='submit']",
        username: str = "",
        password: str = ""
    ):
        self._target_url = target_url
        self._base_link = base_link
        self._login_required = login_required
        self._username_id = username_id
        self._password_id = password_id
        self._login_button_xpath = login_button_xpath
        self._username = username
        self._password = password
        self._visited_pages = set()
        self._graph = nx.DiGraph()
        self._page_stats = PageStats()

    @staticmethod
    def get_extension(url: str) -> str:
        dot_index = url.rfind(".")  # Trouve la dernière occurrence du caractère '.' dans l'URL
        if dot_index == -1:         # Si aucun '.' n'est trouvé dans l'URL, c'est une page html
            return "html"

        extension = url[dot_index + 1:]     # Extrait l'extension en utilisant le reste de l'URL après le dernier '.'
        if "/" in extension:        # Si l'extension contient un '/', c'est une page html
            extension = "html"

        if "?" in extension:        # Si l'extension contient des paramètres de requête, les supprimer
            extension = extension[: extension.index("?")]
            return "jsf"

        return extension

    @staticmethod
    def format_url(url: str) -> str:
        if url[-1] == "/":
            return url[:-1]
        return url

    @staticmethod
    def calculate_shortest_paths(source_node, graph):
        shortest_paths_length = nx.single_source_shortest_path_length(
            graph, source_node
        )
        nx.set_node_attributes(graph, shortest_paths_length, "depth")

    def get_links(
        self, parser: BeautifulSoup, page_url: str
    ) -> list[tuple[str, int]]:
        # Retourne une liste de tuple (url, internal) avec internal=1 si le lien renvoie vers l'ENT

        links = parser.find_all("a")
        result = []

        # On récupère le lien absolu
        for link in links:
            href = link.get("href")
            if (
                href
                and (href[0] != "#")
                and not href.startswith("mailto:")
                and not href.startswith("tel:")
            ):
                # Si le lien est relatif
                if ("http" or "https") not in href:
                    full_link = urljoin(page_url, href)
                    # distinction site interne / externe à l'ENT
                    if self._base_link not in full_link:
                        result.append((self.format_url(full_link), 0))
                    else:
                        result.append((self.format_url(full_link), 1))
                else:
                    # distinction site interne / externe à l'ENT
                    if self._base_link not in href:
                        result.append((self.format_url(href), 0))
                    else:
                        result.append((self.format_url(href), 1))
        return result

    def scrape_page(self, url: str) -> None:    # Parcours des pages récursivement
        url = self.format_url(url)
        if url in self._visited_pages:        # Si la page a déjà été visitée, on ne la traite pas
            return

        self._visited_pages.add(url)        # Ajout de la page à la liste des pages visitées

        print(self._graph.number_of_nodes(), "Pages scrapées, page actuelle : ", url)

        if self._base_link not in url:        # On ne traite que les pages de l'ENT
            return

        extension = self.get_extension(url)
        if extension in Scraper.blacklist:    # On ne scrape pas les pdf, docx, etc.
            return

        # Récupération d'informations
        start_time = time.time()
        Scraper.driver.get(url)
        end_time = time.time()
        loading_time = end_time - start_time    # Temps de chargement de la page

        parser = BeautifulSoup(Scraper.driver.page_source, "html.parser")
        links = self.get_links(parser, url)

        if len(links) == 0:  # Une page qui n'a aucun lien devrait être scrappée non ??
            return

        words = self._page_stats.word_count(parser)[0]  # Nombre de mots
        tags = self._page_stats.tag_count(parser)       # Nombre d'éléments du DOM
        self._graph.add_node(
            url,
            title=Scraper.driver.title,
            nb_words=words,
            nb_tags=tags,
            nb_links=len(links),
            internal=1,
            extension=extension,
            loading_time=loading_time,
        )  # add_node ne crée pas de doublons, mais actualise les valeurs si le nœud existe déjà

        for link in links:        # Appel récursif pour les pages en dessous
            extension = self.get_extension(link[0])
            self._graph.add_node(
                self.format_url(link[0]), extension=extension, internal=link[1]
            )
            self._graph.add_edge(url, self.format_url(link[0]))
            self.scrape_page(link[0])

    def get_data(self) -> nx.DiGraph:
        Scraper.driver.implicitly_wait(5)
        Scraper.driver.get(self._target_url)
        Scraper.driver.maximize_window()
        if self._login_required:
            if self._username == "" or self._password == "":
                raise ValueError("Username and password must be provided if login is set to True")
            username_field = Scraper.driver.find_element(By.ID, self._username_id)
            password_field = Scraper.driver.find_element(By.ID, self._password_id)
            login_button = Scraper.driver.find_element(
                By.XPATH, self._login_button_xpath
            )
            username_field.send_keys(self._username)
            password_field.send_keys(self._password)
            login_button.click()

        self.scrape_page(self._target_url)
        print("Traitement du graphe")
        self.calculate_shortest_paths(self._target_url, self._graph)
        print("Export du graphe")
        nx.write_graphml(self._graph, "graph/ent.graphml")
        print("Graph exporté avec succès : graph/ent.graphml")
        Scraper.driver.quit()
        return self._graph
