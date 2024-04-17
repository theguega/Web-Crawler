import time
from urllib.parse import urljoin
import networkx as nx
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from login import credentials
from tools.word_count import word_count
from tools.tag_count import tag_count


class Scraper:
    with open("blacklist.txt", "r", encoding="utf-8") as file:
        blacklist = {line.strip() for line in file}

    driver = webdriver.Chrome()

    def __init__(
        self,
        target_url="https://webapplis.utc.fr/ent/index.jsf",
        base_link="https://webapplis.utc.fr",
        login_required=True,
    ):
        self._target_url = target_url
        self._base_link = base_link
        self._login_required = login_required
        self._visited_pages = set()
        self._graph = nx.DiGraph()

    @staticmethod
    def __get_extension(url: str) -> str:
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

    @staticmethod
    def __format_url(url: str) -> str:
        if url[-1] == "/":
            return url[:-1]
        return url

    @staticmethod
    def __calculate_shortest_paths(source_node, graph):
        shortest_paths_length = nx.single_source_shortest_path_length(
            graph, source_node
        )
        # Ajouter l'attribut contenant la longueur du plus court chemin à chaque nœud
        nx.set_node_attributes(graph, shortest_paths_length, "depth")


    @staticmethod
    def word_count(
        content: bs4.BeautifulSoup,
    ) -> tuple[int, list[str]] | tuple[int, None]:
        def tag_visible(element: bs4.element.NavigableString) -> bool:
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
                or isinstance(element, bs4.Comment)
                or not element.strip()
            ):
                return False
            return True

        try:
            texts = content.find_all(string=True)
            visible_texts = filter(tag_visible, texts)
            words = [word.strip() for text in visible_texts for word in text.split()]
            count = len(words)
            return count, words
        except Exception as e:
            print("Failed to retrieve the webpage:", e)
            return 0, None

    @staticmethod
    def tag_count(content: bs4.BeautifulSoup) -> int:
        try:
            body = content.body
            if body:
                return sum(1 for _ in body.descendants)
            return 0
        except AttributeError as e:
            print("Failed to retrieve the webpage:", e)
            return 0

    def __get_links(
        self, parser: BeautifulSoup, page_url: str
    ) -> list[tuple[str, int]]:
        # retourne une liste de tuple (url, internal) avec internal=1 si le lien renvoie à l'ent
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
                    if self._base_link not in full_link:
                        result.append((self.__format_url(full_link), 0))
                    else:
                        result.append((self.__format_url(full_link), 1))
                # sinon
                else:
                    # distinction site interne / externe à l'ent
                    if self._base_link not in href:
                        result.append((self.__format_url(href), 0))
                    else:
                        result.append((self.__format_url(href), 1))
        return result

    # Fonction pour scraper les pages en profondeur
    def __scrape_page(self, url: str) -> None:
        url = self.__format_url(url)
        # Si la page à déjà été visitée, on ne la traite pas
        if url in self._visited_pages:
            return

        # Ajouter la page à la liste des pages visitées
        self._visited_pages.add(url)

        print(self._graph.number_of_nodes(), "pages scrappés, page actuelle : ", url)

        # On ne traite que les pages de l'ENT
        if self._base_link not in url:
            return

        extension = self.__get_extension(url)

        # On ne scrap pas les pdf, docx etc..
        if extension in Scraper.blacklist:
            return

        # Scrapping
        start_time = time.time()
        Scraper.driver.get(url)
        end_time = time.time()
        loading_time = end_time - start_time

        parser = BeautifulSoup(Scraper.driver.page_source, "html.parser")
        links = self.__get_links(parser, url)

        if len(links) == 0:
            return

        # Si la page est scrappable, on ajoute d'autres infos dans le graphe
        words = word_count(parser)[0]
        tags = tag_count(parser)
        self._graph.add_node(
            url,
            title=Scraper.driver.title,
            nb_words=words,
            nb_tags=tags,
            nb_links=len(links),
            internal=1,
            extension=extension,
            loading_time=loading_time,
        )  # add_node ne crée pas de doublons mais va actualiser les valeurs si le noeud existe déjà

        # Appel récursif pour les pages en dessous
        for link in links:
            extension = self.__get_extension(link[0])
            self._graph.add_node(
                self.__format_url(link[0]), extension=extension, internal=link[1]
            )
            self._graph.add_edge(url, self.__format_url(link[0]))
            self.__scrape_page(link[0])

    def get_data(self) -> nx.DiGraph:
        Scraper.driver.implicitly_wait(5)
        Scraper.driver.get(self._target_url)

        if self._login_required:
            username_field = Scraper.driver.find_element(By.ID, "username")
            password_field = Scraper.driver.find_element(By.ID, "password")
            login_button = Scraper.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )
            Scraper.driver.maximize_window()

            # Input login credentials
            username_field.send_keys(credentials["username"])
            password_field.send_keys(credentials["password"])
            login_button.click()

        self.__scrape_page(self._target_url)
        print("Traitement du graphe")
        self.__calculate_shortest_paths(self._target_url, self._graph)
        # Exporter le graphe au format GraphML
        print("Export du graphe")
        nx.write_graphml(self._graph, "graph/ent.graphml")
        print("Graph exporté avec succès.")
        # Fermer la session
        Scraper.driver.quit()
        return self._graph
