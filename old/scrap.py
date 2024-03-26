import requests
from bs4 import BeautifulSoup
from src.login import credentials

# URL de la page de connexion
login_url = "https://cas.utc.fr/cas/login.jsf"

# URL de la page à scraper après la connexion
target_url = "https://webapplis.utc.fr/ent/index.jsf"

# Création d'une session pour maintenir la connexion
session = requests.Session()

# Effectuer la connexion
login_response = session.get(login_url)
login_soup = BeautifulSoup(login_response.content, 'html.parser')

# Extraire les paramètres nécessaires pour la soumission du formulaire
execution_value = login_soup.find('input', {'name': 'execution'})['value']

# Préparer les données pour la soumission du formulaire
login_payload = {
    'username': credentials['username'],
    'password': credentials['password'],
    'execution': execution_value,
    '_eventId': 'submit',
    'geolocation': '',
}

# Soumettre le formulaire de connexion
response = session.post(login_url, data=login_payload)

# Vérifier si la connexion a réussi (vous pouvez personnaliser cette vérification en fonction du site)
if "Authentication failed" in response.text:
    print("Échec de la connexion. Vérifiez vos identifiants.")
else:
    # Accéder à la page cible après la connexion
    target_response = session.get(target_url)

    # Traitement de la page cible
    index_page = BeautifulSoup(target_response.content, 'html.parser')
    links = index_page.find_all("a")
    for link in links:
        if (link.get("href")[0]!="#") and("null" not in link.get("href")) :
            #si le lien est relatif
            if ("http" or "https") not in link.get("href"):
                print(target_url+link.get("href"))
            #sinon
            else:
                print(link.get("href"))

    # Fermer la session
    session.close()