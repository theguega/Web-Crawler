import bs4
from PIL import Image
from skimage.color import rgb2lab, deltaE_ciede2000
import numpy as np
import re
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
import io
import requests
import matplotlib.pyplot as plt
import cv2


class PageStats:
    def __init__(self):
        self.visited_css = {}

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

    @staticmethod
    def _full_hex_color(hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        return "#" + hex_color

    @staticmethod
    def _color_distance(color: str, color_set: set[str]) -> float:
        rgb_color = np.array([[int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]])
        lab_color = rgb2lab(rgb_color)

        distances = [
            deltaE_ciede2000(
                lab_color,
                rgb2lab(np.array([[int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)]])),
            )
            for c in color_set
        ]
        return min(distances) if distances else float("inf")

    def color_count(self, content: bs4.BeautifulSoup, current_url: str, session) -> int:
        style_tags = content.find_all("style")
        link_tags = content.find_all("link", rel="stylesheet")

        color_pattern = re.compile(r"#[0-9a-fA-F]{3,6}")
        colors: set[str] = set()

        for tag in style_tags + link_tags:
            try:
                if tag.name == "style":
                    style_content = tag.string
                    color_matches = color_pattern.findall(style_content)

                    for color in color_matches:
                        if len(color) == 4 or len(color) == 7:
                            hex_color = self._full_hex_color(color)
                            if self._color_distance(hex_color, colors) > 0:
                                colors.add(hex_color)

                elif tag.name == "link":
                    css_url = urljoin(current_url, tag.get("href"))
                    if css_url in self.visited_css:
                        colors.update(self.visited_css[css_url])
                        continue
                    style_content = session.get(css_url).text
                    color_matches = color_pattern.findall(style_content)
                    colors_tmp = set()

                    for color in color_matches:
                        if len(color) == 4 or len(color) == 7:
                            hex_color = self._full_hex_color(color)
                            if self._color_distance(hex_color, colors) > 0:
                                colors_tmp.add(hex_color)
                    self.visited_css[css_url] = colors_tmp
                    colors.update(colors_tmp)
            except Exception as e:
                print("Failed to get the color:", e)

        return len(colors)

    @staticmethod
    def full_page_screenshot(driver):
        width = driver.execute_script(
            "return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );"
        )
        height = driver.execute_script(
            "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );"
        )
        driver.set_window_size(width, height)
        full_page = driver.find_element(By.TAG_NAME, "html")

        screen = full_page.screenshot_as_png
        image = Image.open(io.BytesIO(screen))

        return np.array(image)

    @staticmethod
    def _reduce_image(image, taille):
        # Retrancher le reste de la division par 4 du nombre de lignes et de colonnes
        new_height = image.shape[0] - (image.shape[0] % taille)
        new_width = image.shape[1] - (image.shape[1] % taille)

        # Diviser l'image en carrés de taille x taille pixels et calculer la moyenne pour chaque carré
        reduced_image = np.mean(
            image[:new_height, :new_width].reshape(
                new_height // taille, taille, new_width // taille, taille
            ),
            axis=(1, 3),
        )

        return reduced_image

    @staticmethod
    def _create_mask(image, width):
        mask = np.zeros_like(image, dtype=bool)
        half_width = width // 2

        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                # Extraire la région de l'image autour du pixel
                start_x = max(0, x - half_width)
                end_x = min(image.shape[1], x + half_width + 1)
                start_y = max(0, y - half_width)
                end_y = min(image.shape[0], y + half_width + 1)
                window = image[start_y:end_y, start_x:end_x]

                # Vérifier si tous les pixels de la fenêtre ont la même intensité
                if np.all(window == window[0, 0]):
                    mask[y, x] = True

        return mask

    @staticmethod
    def _mask_to_image(mask):
        # Convertir le masque en une image binaire (0 pour True, 255 pour False)
        mask_image = np.where(mask, 0.0, 1.0)
        return mask_image

    @staticmethod
    def _proportion_true_false(mask):
        true_count = np.count_nonzero(mask)
        false_count = np.count_nonzero(~mask)  # Compter le complément du masque (False)

        total_pixels = mask.size
        proportion_true = true_count / total_pixels
        proportion_false = false_count / total_pixels

        return proportion_true, proportion_false

    def empty_space(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reduced_gray_image = self._reduce_image(gray_image, 10)

        # # Afficher l'image réduite en niveaux de gris
        # plt.imshow(reduced_gray_image, cmap="gray")
        # plt.axis("off")
        # plt.show()

        mask = self._create_mask(reduced_gray_image, 5)
        empty_proportion = self._proportion_true_false(mask)[0]

        # # Convertir le masque en une image
        # mask_image = self._mask_to_image(mask)
        # plt.imshow(mask_image, cmap="gray", vmin=0, vmax=1, interpolation="none")
        # plt.axis("off")
        # plt.show()
        return empty_proportion


