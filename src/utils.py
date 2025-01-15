import requests
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
            thesis_name TEXT,
            thesis_url TEXT NOT NULL UNIQUE,
            thesis_abstract TEXT,
            thesis_abstract_fr TEXT,
            thesis_info TEXT,
            thesis_file BOOLEAN DEFAULT FALSE,
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

###########
### HAL ###
###########

def extract_hal_gen()->bool:
    log_prefix = '[utils | extract_hal_gen]'
    try:
        DEBUG = os.getenv("DEBUG")
        QUERY = os.getenv("QUERY")
        if DEBUG != "0":
            ROWS = "2"
        else:
            ROWS = os.getenv("ROWS")
        FQ = os.getenv("FQ")

        BASE_URL = f"https://api.archives-ouvertes.fr/search/?q={QUERY}&rows={ROWS}&fq={FQ}"
        logging_msg(f"{log_prefix} BASE_URL: {BASE_URL}")

        conn = sqlite3.connect('thesis.db')
        cursor = conn.cursor()

        response = requests.get(BASE_URL)
        if response.status_code == 200:
            data = response.json()
            for doc in data.get("response", {}).get("docs", []):
                logging_msg(f"{log_prefix} docid: {doc.get('docid')}", 'DEBUG')
                logging_msg(f"{log_prefix} label_s: {doc.get('label_s')}", 'DEBUG')
                logging_msg(f"{log_prefix} uri_s: {doc.get('uri_s')}", 'DEBUG')
                
                request = f'''
INSERT INTO thesis (category, thesis_url)
     VALUES ("HAL", "{doc.get('uri_s')}")
'''
                logging_msg(f"{log_prefix} request: {request}", 'SQL')
                try:
                    cursor.execute(request)
                except Exception as e:
                    if 'UNIQUE constraint' in str(e):
                        logging_msg(f"{log_prefix} Podcast already exists", 'DEBUG')
                    else:
                        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')

                conn.commit()

            conn.close()

        else:
            raise Exception(f"Error: {response.status_code}")
        
        return True
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False
    

def extract_hal()->bool:
    log_prefix = '[utils | extract_hal]'
    try:
        conn = sqlite3.connect('thesis.db')
        cursor = conn.cursor()

        request = f'''
SELECT id, url
  FROM thesis
 WHERE downloaded IS FALSE
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            logging_msg(f"{log_prefix} row: {row}", 'DEBUG')
            id = row[0]

            try:
                tt = 0/0

                request = f'''
UPDATE podcasts
   SET downloaded = TRUE
 WHERE id = {id}
'''
                cursor.execute(request)
                conn.commit()
                logging_msg(f"{log_prefix} Podcast updated: {id}", 'DEBUG')

            except Exception as e:
                logging_msg(f"{log_prefix} Error downloading podcast [id:{id}]: {e}", 'ERROR')
        
        conn.close()

        return True
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False


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