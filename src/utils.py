import sqlite3
import json
import os
from logs import logging_msg



##################################################
##################################################
##################################################

############
### INIT ###
############
def init()->bool:
    log_prefix = '[utils | init]'
    try:
        FOLDER_PATH = os.getenv("FOLDER_PATH")
        os.makedirs(f'./{FOLDER_PATH}/', exist_ok=True)

        conn = sqlite3.connect('thesis.db')

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thesis (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            podcast_name TEXT NOT NULL,
            rss_feed TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            published TEXT NOT NULL,
            description TEXT NOT NULL,
            downloaded BOOLEAN DEFAULT FALSE,
            processed BOOLEAN DEFAULT FALSE
        )""")

        conn.commit()
        conn.close()

        return True
    
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False

##################################################
##################################################
##################################################

import requests
import json

def extract_hal():
    # URL de l'API HAL (à vérifier si elle existe)
    BASE_URL = "https://api.archives-ouvertes.fr/search/?q=intelligence+artificielle&rows=2&fq=submittedDate_tdate:[NOW-3MONTHS/DAY%20TO%20NOW/HOUR]"
    # query = {
    #     "q": "intelligence artificielle",  # Mots-clés
    #     "rows": 10,                        # Nombre de résultats
    #     "fl": "docid,title,authFullName,fileSize,doi"  # Champs à extraire
    # }

    response = requests.get(BASE_URL)
    # response = requests.get(BASE_URL, params=query)

    if response.status_code == 200:
        data = response.json()
        for doc in data.get("response", {}).get("docs", []):
            # print(doc)
            print()
            print(f"docid: {doc.get('docid')}")
            print()
            print(f"label_s: {doc.get('label_s')}")
            print()
            print(f"uri_s: {doc.get('uri_s')}")
    else:
        print("Erreur >>> ", response.status_code)


##################################################
##################################################
##################################################

### PARSE JSON ###
def parse_json(json_file: str) -> list:
    log_prefix = '[utils | parse_json]'
    try:
        logging_msg(f"{log_prefix} json_file: {json_file}", 'DEBUG')

        with open(json_file, 'r', encoding='utf-8') as file:
            feeds = json.load(file)
        return feeds
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return []