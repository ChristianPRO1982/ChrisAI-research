import feedparser
import requests
import whisper
import openai
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
    log_prefix = '[utils | parse_rss_feed]'
    try:
        FOLDER_PATH = os.getenv("FOLDER_PATH")
        os.makedirs(f'./{FOLDER_PATH}/', exist_ok=True)

        conn = sqlite3.connect('podcast.db')

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
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

######################
### PARSE PODCASTS ###
######################
def parse_rss_feed(category: str, name: str, rss_feed: str) -> bool:
    log_prefix = '[utils | parse_rss_feed]'
    try:
        logging_msg(f"{log_prefix} feed_rss_url: {rss_feed}", 'DEBUG')

        feed = feedparser.parse(rss_feed)

        if feed.bozo:
            raise Exception(f"Failed to parse RSS feed: {feed.bozo_exception}")

        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()
        
        for entry in feed.entries:
            title = entry.get('title', 'No title')
            link = entry.get('link', 'No link')
            published = entry.get('published', 'No publish date')
            description = entry.get('description', 'No description')
            logging_msg(f"----------------------------------------------------------------------------------------------------", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Title: {title}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Link: {link}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Published Date: {published}", 'DEBUG')
            logging_msg(f"{log_prefix} Podcast Description: {description}", 'DEBUG')
            title = title.replace('"', "''")
            link = link.replace('"', "''")
            published = published.replace('"', "''")
            description = description.replace('"', "''")

            request = f'''
INSERT INTO podcasts (category, podcast_name, rss_feed, title, link, published, description)
     VALUES ("{category}", "{name}", "{rss_feed}", "{title}", "{link}", "{published}", "{description}")
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
        logging_msg(f"{log_prefix} >> OK <<", 'DEBUG')
        return True


    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False
    

########################
### DOWNLOAD PODCAST ###
########################
def download_podcast(FOLDER_PATH, PREFIX) -> bool:
    log_prefix = '[utils | download_podcast]'
    try:
        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()

        request = f'''
SELECT id, link
  FROM podcasts
 WHERE downloaded IS FALSE
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            logging_msg(f"{log_prefix} row: {row}", 'DEBUG')
            id = row[0]
            link = row[1]

            file_name = os.path.join(FOLDER_PATH, f'{PREFIX}{id}.mp3')

            try:
                response = requests.get(link)
                response.raise_for_status()
                with open(file_name, 'wb') as file:
                    file.write(response.content)
                logging_msg(f"{log_prefix} Podcast downloaded: {file_name}", 'DEBUG')

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

##################
### TRANSCRIBE ###
##################
def transcribe_all_podcasts(FOLDER_PATH, PREFIX, FFMPEG_PATH):
    log_prefix = '[utils | transcribe_all_podcasts]'

    try:
        conn = sqlite3.connect('podcast.db')
        cursor = conn.cursor()

        request = f'''
SELECT id
  FROM podcasts
 WHERE downloaded IS TRUE
   AND processed IS FALSE
LIMIT 1
'''
        logging_msg(f"{log_prefix} request: {request}", 'SQL')
        cursor.execute(request)

        for row in cursor.fetchall():
            logging_msg(f"{log_prefix} row: {row}", 'DEBUG')
            id = row[0]

            file_name = os.path.join(FOLDER_PATH, f'{PREFIX}{id}.mp3')

            try:
                if not os.path.exists(file_name):
                    raise Exception(f"File not found: {file_name}")
                
                transcribe(file_name, FFMPEG_PATH)
                logging_msg(f"{log_prefix} Podcast processed: {file_name}", 'DEBUG')

                request = f'''
UPDATE podcasts
   SET processed = TRUE
 WHERE id = {id}
'''
                # cursor.execute(request)
                # conn.commit()
                # logging_msg(f"{log_prefix} Podcast updated: {id}", 'DEBUG')
                
                break

            except Exception as e:
                logging_msg(f"{log_prefix} Error downloading podcast [id:{id}]: {e}", 'ERROR')
        
        conn.close()

        return True
    
    
    except Exception as e:
        logging_msg(f"{log_prefix} Error: {e}", 'ERROR')
        return False


def transcribe(file_path, FFMPEG_PATH)->bool:
    log_prefix = '[utils | transcribe]'

    try:
        print(file_path)
        print(FFMPEG_PATH)
        os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
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