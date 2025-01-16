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

if utils.init():
    logging_msg("utils.extract_hal_gen START", 'WARNING')
    stop_and_go = utils.extract_hal_gen()
    if stop_and_go:
        logging_msg("utils.extract_hal START", 'WARNING')
        stop_and_go = utils.extract_hal()
    if stop_and_go:
        logging_msg("utils.extract_stat START", 'WARNING')
        stop_and_go = utils.extract_stat()

logging_msg("END PROGRAM", "WARNING")
