import requests
from bs4 import BeautifulSoup


def tag_count(url: str, session: requests.Session) -> int | None:
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.body
        if body:
            balises = body.find_all()
            return len(balises)
        return None
    print("La requête a échoué avec le code :", response.status_code)
    return None


# # URL de la page à analyser
# url = "https://www.crummy.com/software/BeautifulSoup/bs4/doc/"
# # Appeler la fonction pour compter les balises sur la page
# nombre_balises = tag_count(url)
# # Afficher le résultat
# if nombre_balises is not None:
#     print("Le nombre total de balises dans la balise <body> est :", nombre_balises)
