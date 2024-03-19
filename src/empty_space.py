import cv2
import numpy as np

# def create_mask(image_path, width):
#     image = Image.open(image_path)
#     image_array = np.array(image)
#     mask = np.zeros(image_array.shape[:2], dtype=bool)
#     total_pixels = image.width * image.height
#     current_pixel = 0
#     for y in range(image.height):
#         for x in range(image.width):
#             start_x = max(0, x - width // 2)
#             end_x = min(image.width, x + width // 2 + 1)
#             start_y = max(0, y - width // 2)
#             end_y = min(image.height, y + width // 2 + 1)
#             window = image_array[start_y:end_y, start_x:end_x]
#             if np.all(window == window[0, 0]):
#                 mask[y, x] = True
#             current_pixel += 1
#             print(f"{current_pixel / total_pixels * 100:.2f}% complete")
#     return mask
#
# def mask_to_image(mask):
#     # Convert the boolean mask to uint8 where True becomes 0 (black) and False becomes 255 (white)
#     mask_image = np.where(mask, 0, 255).astype(np.uint8)
#     # Create a PIL image from the numpy array
#     return Image.fromarray(mask_image)
#
# # Path to your PNG image
# image_path = "screenshot (2).png"
# # Width of the pixel window to consider
# width = 30
#
# # Create the mask
# mask = create_mask(image_path, width)
#
# # Convert the mask to an image
# mask_image = mask_to_image(mask)
#
# # Save or display the image (optional)
# mask_image.show()

def create_mask(image_path, width):
    # Charger l'image avec OpenCV
    image = cv2.imread(image_path)

    # Convertir l'image en niveaux de gris
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Initialiser le masque
    mask = np.zeros_like(gray_image, dtype=bool)

    # Calculer la moitié de la largeur de la fenêtre
    half_width = width // 2

    total_pixels = image.shape[0] * image.shape[1]

    # Compteur de pixels traités
    processed_pixels = 0
    # Parcourir chaque pixel de l'image
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            # Extraire la région de l'image autour du pixel
            start_x = max(0, x - half_width)
            end_x = min(image.shape[1], x + half_width + 1)
            start_y = max(0, y - half_width)
            end_y = min(image.shape[0], y + half_width + 1)
            window = gray_image[start_y:end_y, start_x:end_x]

            # Vérifier si tous les pixels de la fenêtre ont la même intensité
            if np.all(window == window[0, 0]):
                mask[y, x] = True

            processed_pixels += 1
            progress = (processed_pixels / total_pixels) * 100
            print(f"Progress: {progress:.2f}% complete", end="\r")

    return mask


def mask_to_image(mask):
    # Convertir le masque en une image binaire (0 pour True, 255 pour False)
    mask_image = np.where(mask, 0, 255).astype(np.uint8)
    return mask_image


# Chemin vers votre image PNG
image_path = "screenshot (2).png"
# Largeur de la fenêtre de pixels à considérer
width = 30

# Créer le masque
mask = create_mask(image_path, width)

# Convertir le masque en une image
mask_image = mask_to_image(mask)

# Afficher l'image
cv2.imshow("Mask Image", mask_image)
cv2.waitKey(0)
cv2.destroyAllWindows()