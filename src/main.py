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

# RSS_FEEDS = utils.parse_json(os.getenv("RSS_FEEDS"))
FOLDER_PATH = os.getenv("FOLDER_PATH")
PREFIX = os.getenv("PREFIX")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")

if utils.init():
    utils.extract_hal()

logging_msg("END PROGRAM", "WARNING")
