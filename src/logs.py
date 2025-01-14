import datetime
import logging
import os



def init_log()->bool:
    try:
        DEBUG = os.getenv("DEBUG")

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        os.makedirs('./logs/', exist_ok=True)
        log_filename = f"./logs/{date_str}.log"

        if DEBUG != '0':
            print("§§§§§§§§§§§§§§§§§§§§§§")
            print("§§§§§ DEBUG MODE §§§§§")
            print("§§§§§§§§§§§§§§§§§§§§§§")
            print("Debug mode: ", DEBUG)
            if DEBUG == '1':
                logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            elif DEBUG == '2':
                logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
            elif DEBUG == '3':
                logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        else:
            logging.basicConfig(filename=log_filename, level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
        
        return True
    
    except Exception as e:
        print(f"Error in logging.py init_log(): {e}")
        return False


def logging_msg(msg, type='INFO')->bool:
    try:
        DEBUG = os.getenv("DEBUG")

        logger = logging.getLogger(__name__)
        # print(logging.getLevelName(logger.getEffectiveLevel()))

        type = type.upper()

        if type == 'INFO':
            logger.info(msg)
        elif type == 'DEBUG':
            logger.debug(msg)
        elif type == 'ERROR':
            logger.error(msg)
        elif type == 'WARNING':
            logger.warning(msg)
        elif type == 'CRITICAL':
            logger.critical(msg)
        elif type == 'SQL':
            if DEBUG == '3':
                logger.info(msg)
            else:
                logger.debug(msg)

        if type != 'DEBUG' and type != 'SQL' or DEBUG == '3' and type == 'SQL':
            print(f"[{type}] {msg}")

        return True

    except Exception as e:
        print(f"Error in logging.py logging_msg(): {e}")
        return False