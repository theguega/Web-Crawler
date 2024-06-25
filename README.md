# Méthode d’évaluation de la complexité et de la clarté de l’ENT UTC

Ce projet est un web-crawler permettant de récupérer toutes les informations du site ENT - UTC.

## Configuration du projet :

1. Installation des bibliothèques  

```bash
pip install -r src/requirements.txt  
```

2. Créer un fichier `login.py` et y ajouter les informations suivantes :  

```python
credentials = {
    'username': 'yourusername',
    'password': 'youpassword',
}
```

3. Lancer le script  

```bash
python3 src/main.py
```

4. Attendre que toutes les pages soient récupérées ~15 minutes.  

5. Récupérer le graph exportés : `graph/ent.graphml`  

---

Crédits : Samuel Beziat & Theo Guegan
