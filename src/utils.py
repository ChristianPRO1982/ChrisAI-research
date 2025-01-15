from bs4 import BeautifulSoup
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
            thesis_id TEXT,
            thesis_name TEXT,
            thesis_url TEXT NOT NULL UNIQUE,
            thesis_abstract_en TEXT,
            thesis_abstract_fr TEXT,
            thesis_info TEXT,
            thesis_summary_by_ai TEXT,
            downloaded INTEGER DEFAULT -1,
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
                docid = doc.get('docid')
                label_s = doc.get('label_s')
                uri_s = doc.get('uri_s')
                uri_s = uri_s.replace('"', '″')
                
                logging_msg(f"{log_prefix} docid: {docid}", 'DEBUG')
                logging_msg(f"{log_prefix} label_s: {label_s}", 'DEBUG')
                logging_msg(f"{log_prefix} uri_s: {uri_s}", 'DEBUG')
                
                request = '''
INSERT INTO thesis (category, thesis_id, thesis_url, thesis_info)
     VALUES (?, ?, ?, ?)
'''
                params = ('HAL', docid, uri_s, label_s)
                logging_msg(f"{log_prefix} request: {request}", 'SQL')
                try:
                    cursor.execute(request, params)
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
SELECT id, thesis_url
  FROM thesis
 WHERE downloaded = -1
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            logging_msg(f"{log_prefix} row: {row}", 'DEBUG')
            id = row[0]

            try:
                response = requests.get(row[1])
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    thesis_name = soup.find('h2', class_='title-lang')
                    if thesis_name:
                        thesis_name_text = thesis_name.get_text(strip=True)
                    else:
                        thesis_name_text = "No title"

                    summary_en = soup.find('div', class_='abstract-content', lang='en')
                    if summary_en:
                        thesis_abstract_en = summary_en.get_text(strip=True)
                    else:
                        thesis_abstract_en = "No abstract in English"
                    
                    summary_fr = soup.find('div', class_='abstract-content', lang='fr')
                    if summary_fr:
                        thesis_abstract_fr = summary_fr.get_text(strip=True)
                    else:
                        thesis_abstract_fr = "No abstract in French"

                else:
                    logging_msg(f"{log_prefix} Error: {response.status_code}", 'ERROR')
                
                download_status = extract_hal_download(row[1], id)

                request = f'''
UPDATE thesis
   SET downloaded = ?,
       thesis_name = ?,
       thesis_abstract_en = ?,
       thesis_abstract_fr = ?
 WHERE id = ?
'''
                params = (download_status, thesis_name_text, thesis_abstract_en, thesis_abstract_fr, id)
                logging_msg(f"{log_prefix} request: {request}", 'SQL')
                cursor.execute(request, params)
                conn.commit()
                logging_msg(f"{log_prefix} Podcast updated: {id}", 'DEBUG')

            except Exception as e:
                logging_msg(f"{log_prefix} Error downloading podcast [id:{id}]: {e}", 'ERROR')
        
        conn.close()

        return True
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False
    

def extract_hal_download(url: str, id: int)->int:
    log_prefix = '[utils | extract_hal_download]'

    FOLDER_PATH = os.getenv("FOLDER_PATH")
    PREFIX = os.getenv("PREFIX")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pdf_link = soup.find('iframe')
            if not pdf_link:
                logging_msg(f"{log_prefix} No pdf link found [id:{id}]", 'DEBUG')
                return 1 # no pdf link found
            
            pdf_url = pdf_link['src'] if pdf_link.name == 'iframe' else pdf_link['href']
            if ".pdf" not in pdf_url:
                logging_msg(f"{log_prefix} PDF link is not a pdf file [id:{id}]", 'DEBUG')
                return 3 # pdf link is not a pdf file

            pdf_response = requests.get(pdf_url)
            
            if pdf_response.status_code == 200:
                file_path = os.path.join(FOLDER_PATH, f"{PREFIX}{id}.pdf")
                with open(file_path, 'wb') as file:
                    file.write(pdf_response.content)
                logging_msg(f"{log_prefix} PDF downloaded successfully: {file_path} [id:{id}]", 'DEBUG')
                return 2 # pdf downloaded successfully
            
            else:
                raise Exception(f"Download: {pdf_response.status_code}")
            
        else:
            raise Exception(f"Load HTML page: {response.status_code}")
    

    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return 0 # error during download
    

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