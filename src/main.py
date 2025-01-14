import dotenv
import os
from logs import init_log, logging_msg
import utils



##################################################
##################################################
##################################################

############
### MAIN ###
############
dotenv.load_dotenv(override=True)
init_log()
logging_msg("START PROGRAM", "WARNING")

RSS_FEEDS = utils.parse_json(os.getenv("RSS_FEEDS"))
FOLDER_PATH = os.getenv("FOLDER_PATH")
PREFIX = os.getenv("PREFIX")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")

if utils.init():
    for podcast in RSS_FEEDS:
        category = podcast["category"]
        name = podcast["name"]
        rss_feed = podcast["rss_feed"]
        logging_msg(f"Processing {name}...")
        logging_msg("utils.parse_rss_feed START")
        stop_and_go = utils.parse_rss_feed(category, name, rss_feed)
        if not stop_and_go:
            continue
        logging_msg("utils.download_podcast START")
        stop_and_go = utils.download_podcast(FOLDER_PATH, PREFIX)
        if not stop_and_go:
            continue
        logging_msg("utils.transcribe_all_podcasts START")
        stop_and_go = utils.transcribe_all_podcasts(FOLDER_PATH, PREFIX, FFMPEG_PATH)
        if not stop_and_go:
            continue

logging_msg("END PROGRAM", "WARNING")
