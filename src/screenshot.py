from selenium import webdriver
import time

# Créer une instance du navigateur Chrome
driver = webdriver.Chrome()

# Ouvrir une page web
driver.get("https://www.utc.fr/")

# Attendre que la page se charge complètement
time.sleep(2)

# Récupérer la taille de la fenêtre du navigateur
window_size = driver.get_window_size()
screen_width = window_size['width']
screen_height = window_size['height']

# Définir la taille de la capture d'écran
screenshot_width = screen_width
screenshot_height = screen_height

# Calculer le nombre de scrolls nécessaires pour atteindre le bas de la page
scrolls = 5  # ajustez ce nombre selon votre besoin

# Boucle pour faire défiler la page et prendre des captures d'écran
for i in range(scrolls):
    # Prendre une capture d'écran
    driver.save_screenshot(f"screenshot_{i}.png")

    # Faire défiler la page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Attendre un court instant pour que la page se scroll
    time.sleep(2)

# Fermer le navigateur
driver.quit()