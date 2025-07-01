import argparse
from src.custom_logging import setup_logger
from src.start_app import main

logger = setup_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--type', '-t', type=str, default='anime', choices=['serie', 'anime'])
parser.add_argument('--name', '-n', type=str, default='Name-Goes-Here')
parser.add_argument('--lang', '-l', type=str, default='Deutsch', choices=['Deutsch', 'Ger-Sub', 'English'])
parser.add_argument('--dl-mode', '-m', type=str, default='Series', choices=['Series', 'Movies', 'All'])
parser.add_argument('--season-override', '-s', type=int, default=0)
parser.add_argument('--provider', '-p', type=str, default='VOE', choices=['VOE', 'Streamtape', 'Vidoza'])
parser.add_argument('--path-override', type=str)

args = parser.parse_args()

if __name__ == "__main__":
    try:
        main(args)
    except KeyboardInterrupt:
        logger.info("-----------------------------------------------------------")
        logger.info("            AnimeSerienScraper Stopped")
        logger.info("-----------------------------------------------------------")
        logger.info("Downloads may still be running. Please don't close this Window until its done.")
        logger.info("You will know it's done once you see your primary prompt string.")
    except Exception as e:
        logger.error("----------")
        logger.error(f"Exception: {e}")
        logger.error("----------")
