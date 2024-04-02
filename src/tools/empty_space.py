import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from Screenshot import Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Screenshot import Screenshot
from selenium import webdriver
import time
from playwright.sync_api import sync_playwright
from selenium.webdriver.common.by import By
from selenium import webdriver

# Initialize Selenium WebDriver (you may need to install a WebDriver executable)
driver = webdriver.Chrome()  # Change this to your preferred WebDriver

# Navigate to the web page
driver.get("https://example.com")  # Replace this with the URL of the web page you want to analyze

# Get the total area of the web page
total_area = driver.execute_script("return document.body.scrollHeight * document.body.scrollWidth")
print(total_area)
# Get the total area covered by elements
for element in driver.find_elements(By.XPATH, "//*"):
    print(element.tag_name)
element_areas = sum(element.size['width'] * element.size['height'] for element in driver.find_elements(By.XPATH, "//div"))
# You may need to refine the XPath expression to only include visible elements

# Calculate the percentage of empty space
empty_space_percentage = ((total_area - element_areas) / total_area) * 100

print("Percentage of empty space:", empty_space_percentage)

# Close the WebDriver
driver.quit()

# def reduce_image(image, taille):
#     # Retrancher le reste de la division par 4 du nombre de lignes et de colonnes
#     new_height = image.shape[0] - (image.shape[0] % taille)
#     new_width = image.shape[1] - (image.shape[1] % taille)
#
#     # Diviser l'image en carrés de 4x4 pixels et calculer la moyenne pour chaque carré
#     reduced_image = np.mean(
#         image[:new_height, :new_width].reshape(
#             new_height // taille, taille, new_width // taille, taille
#         ),
#         axis=(1, 3),
#     )
#
#     return reduced_image
#
#
# def create_mask(image, width):
#     # Initialiser le masque
#     mask = np.zeros_like(image, dtype=bool)
#
#     # Calculer la moitié de la largeur de la fenêtre
#     half_width = width // 2
#
#     total_pixels = image.shape[0] * image.shape[1]
#
#     # Compteur de pixels traités
#     processed_pixels = 0
#     # Parcourir chaque pixel de l'image
#     for y in range(image.shape[0]):
#         for x in range(image.shape[1]):
#             # Extraire la région de l'image autour du pixel
#             start_x = max(0, x - half_width)
#             end_x = min(image.shape[1], x + half_width + 1)
#             start_y = max(0, y - half_width)
#             end_y = min(image.shape[0], y + half_width + 1)
#             window = image[start_y:end_y, start_x:end_x]
#
#             # Vérifier si tous les pixels de la fenêtre ont la même intensité
#             if np.all(window == window[0, 0]):
#                 mask[y, x] = True
#
#             processed_pixels += 1
#             progress = (processed_pixels / total_pixels) * 100
#             print(f"Progress: {progress:.2f}% complete", end="\r")
#
#     return mask
#
#
# def mask_to_image(mask):
#     # Convertir le masque en une image binaire (0 pour True, 255 pour False)
#     mask_image = np.where(mask, 0.0, 1.0)
#     return mask_image
#
#
# def proportion_true_false(mask):
#     # Compter le nombre de True et de False dans le masque
#     true_count = np.count_nonzero(mask)
#     false_count = np.count_nonzero(~mask)  # Compter le complément du masque (False)
#
#     # Calculer les proportions
#     total_pixels = mask.size
#     proportion_true = true_count / total_pixels
#     proportion_false = false_count / total_pixels
#
#     return proportion_true, proportion_false
#
#
# image = cv2.imread("screenshot (6).png")
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# reduced_gray_image = reduce_image(gray_image, 10)
# # Afficher l'image réduite en niveaux de gris
# plt.imshow(reduced_gray_image, cmap="gray")
# plt.axis("off")
# plt.show()
#
#
# # Créer le masque
# mask = create_mask(reduced_gray_image, 5)
# print(proportion_true_false(mask))
# print(mask.shape)
#
# # Convertir le masque en une image
# mask_image = mask_to_image(mask)
#
# plt.imshow(mask_image, cmap="gray", vmin=0, vmax=1, interpolation="none")
# plt.axis("off")
# plt.show()
# plt.imsave("mask.png", mask_image, cmap="gray")
