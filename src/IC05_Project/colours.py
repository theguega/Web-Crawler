import re
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image
from skimage.color import rgb2lab, deltaE_ciede2000
import numpy as np


def color_set(url: str, session: requests.Session) -> set[str]:
    def full_hex_color(hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        return "#" + hex_color

    def distance(col: str, col_set: set[str]) -> float:
        rgb_color = np.array([[int(col[i : i + 2], 16) / 255 for i in (1, 3, 5)]])
        lab_color = rgb2lab(rgb_color)

        distances = [
            deltaE_ciede2000(
                lab_color,
                rgb2lab(np.array([[int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)]])),
            )
            for c in col_set
        ]
        return min(distances) if distances else float("inf")

    soup = BeautifulSoup(session.get(url).content, "html.parser")
    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
    style_tags = soup.find_all("style")
    link_tags = soup.find_all("link", rel="stylesheet")

    # Extraction des couleurs à partir des éléments CSS
    colors: set[str] = set()
    for tag in style_tags + link_tags:
        try:
            # Si le style est inline (dans la balise elle-même)
            if tag.name == "style":
                style_content = tag.string
            # Si le style est défini dans un fichier externe
            elif tag.name == "link":
                css_url = urljoin(base_url, tag.get("href"))
                style_content = session.get(css_url).text

            # Extraction des couleurs avec une expression régulière
            color_matches = re.findall(r"#[0-9a-fA-F]{3,6}", style_content)
            for color in color_matches:
                if len(color) == 4 or len(color) == 7:
                    if distance(full_hex_color(color), colors) > 20:
                        colors.add(full_hex_color(color))
        except Exception as e:
            print("Failed to get the color:", e)
    return colors


def create_color_image(colors, image_size):
    """
    Crée une image avec toutes les images de colors
    """
    num_colors = len(colors)
    image_array = np.zeros((image_size, image_size * num_colors, 3), dtype=np.uint8)
    for i, color in enumerate(colors):
        rgb_color = np.array(
            [[int(color[i : i + 2], 16) for i in range(1, 7, 2)]], dtype=np.uint8
        )
        image_array[:, i * image_size : (i + 1) * image_size, :] = rgb_color
    return Image.fromarray(image_array, "RGB")


# # URL du site web à analyser
# URL = "https://www.utc.fr/"
#
# # Extraction des couleurs utilisées sur le site web
# colors = color_set(URL)
# colors = {'#234386', '#ffffff', '#4f4f4f', '#00FFFF', '#5f83b9', '#000000', '#c09853', '#cd0a0a', '#a8a8a8'}
# # Affichage des couleurs
# print("Couleurs utilisées sur le site web :")
# for color in colors:
#     print(color)
#
#
# image = create_color_image(colors, 50)
# image.show()
