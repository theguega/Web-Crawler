# **Complexity and Clarity Evaluation of the ENT UTC**

## **Description**
This project is a web crawler designed to scrape all relevant information from the ENT (Espace Numérique de Travail) platform of **UTC**. The collected data is structured into a graph, providing insights into the complexity and clarity of the website's content and structure.

![graph](graph/export/extensions.png)

## **Table of Contents**
1. [Setup](#setup)
2. [Usage](#usage)
3. [Output](#output)

## **Setup**
To set up the project, follow these steps:

1. Install the required Python libraries:
   ```bash
   pip install -r src/requirements.txt
   ```

2. Create a `login.py` file and add your ENT login credentials:
   ```python
   credentials = {
       'username': 'yourusername',
       'password': 'yourpassword',
   }
   ```

## **Usage**
Once everything is configured, run the script to start the web crawling process:

```bash
python3 src/main.py
```

The scraping process will take approximately **15 minutes** to retrieve all pages.

## **Output**
The data is exported as a **graph** file in the `graph/` directory. You can find the generated graph file here:
```
graph/ent.graphml
```

---

Crédits : Samuel Beziat & Theo Guegan
