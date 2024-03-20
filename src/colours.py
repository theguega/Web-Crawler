import re
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image
from skimage.color import rgb2lab, deltaE_ciede2000
import numpy as np


def normalize_hex_color(hex_color):
    # Supprimer le caractère '#' du début si présent
    hex_color = hex_color.lstrip("#")
    # Si la longueur de la chaîne est de 3, doubler chaque caractère
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    return "#" + hex_color


def distance(color, color_set):
    """
    Calcule la distance entre une couleur et toutes les couleurs dans un ensemble.
    """
    # Convertir la couleur en RGB normalisé
    rgb_color = np.array([[int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]])
    lab_color = rgb2lab(rgb_color)

    # Calculer la distance entre la couleur et chaque couleur dans l'ensemble
    distances = [
        deltaE_ciede2000(
            lab_color,
            rgb2lab(np.array([[int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)]])),
        )
        for c in color_set
    ]
    return min(distances) if distances else float("inf")


def extract_colors(url):
    print("hi")
    # Récupération du contenu HTML de la page web
    response = requests.get(url, timeout=5)
    html_content = response.text

    # Analyse du contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Récupération de l'URL de base
    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc

    # Récupération de tous les éléments <style> et <link rel="stylesheet">
    style_tags = soup.find_all("style")
    link_tags = soup.find_all("link", rel="stylesheet")

    # Extraction des couleurs à partir des éléments CSS
    colors = set()
    for tag in style_tags + link_tags:
        # Si le style est inline (dans la balise elle-même)
        if tag.name == "style":
            style_content = tag.string
        # Si le style est défini dans un fichier externe
        elif tag.name == "link":
            css_url = urljoin(base_url, tag.get("href"))
            css_response = requests.get(css_url, timeout=5)
            style_content = css_response.text

        # Extraction des couleurs avec une expression régulière
        color_matches = re.findall(r"#[0-9a-fA-F]{3,6}", style_content)
        for color in color_matches:
            print(normalize_hex_color(color))
            if distance(normalize_hex_color(color), colors) > 20:
                colors.add(normalize_hex_color(color))
    print("hi")
    return colors


def create_color_image(colors, image_size):
    """
    Crée une image avec des carrés de couleur.
    """
    num_colors = len(colors)
    image_array = np.zeros((image_size, image_size * num_colors, 3), dtype=np.uint8)
    for i, color in enumerate(colors):
        rgb_color = np.array(
            [[int(color[i : i + 2], 16) for i in range(1, 7, 2)]], dtype=np.uint8
        )
        image_array[:, i * image_size : (i + 1) * image_size, :] = rgb_color
    return Image.fromarray(image_array, "RGB")


# URL du site web à analyser
URL = "https://www.utc.fr/"

# Extraction des couleurs utilisées sur le site web
colors = extract_colors(URL)

# Affichage des couleurs
print("Couleurs utilisées sur le site web :")
for color in colors:
    print(color)


image = create_color_image(colors, 50)
image.show()
