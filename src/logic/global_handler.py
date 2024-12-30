from logic.logging_handler import Logger
logger = Logger()
from sys import argv

help_options = """
Aniworld Scraper.
Usage:
-------------------------------------------------
If no parameters are given you will get a User Interface to make these options.

Parameters:
--media=anime|serie
--name=NameOfTheShow/Anime/Movie
--download_lang=Deutsch|Ger-Sub|English
--dl-mode=Series|Movies|All

Optional Parameters:
--season_override=SeasonNumber
--provider=VOE|Streamtape|Vidoza|SpeedFiles
--help
--episode_override=EpisodeNumber
--max_concurrent_downloads=Number
--max_retries=Number
--wait_time=Number
--disable_wait_threads=True/False
--output_dir=Path
--debug_logging=True/False
-------------------------------------------------
"""
def __get_lang__():
    lang = GlobalHandler()["lang"]
    return lang

class GlobalHandler:
    def __init__(self):
        self.media = None
        self.name = None
        self.download_lang = None
        self.dl_mode = None
        self.season_override = None
        self.provider = None
        self.episode_override = None
        self.max_concurrent_downloads = 5
        self.max_retries = 4
        self.wait_time = 30
        self.disable_wait_threads = False
        self.output_dir = "output"
        self.site_url = {"serie": "https://s.to/serie","anime": "https://aniworld.to/anime"}
        self.provider_priority = ["VOE", "Streamtape", "Vidoza", "SpeedFiles"]
        self.url = None
        self.APP_VERSION = "v03-00"

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)


    def parse_cli_arguments(self):
        if len(argv) == 1:
            return False
        for arg in argv[1:]:
            if "--media" in arg:
                self.media = arg.split("=")[1]
            elif "--name" in arg:
                self.name = arg.split("=")[1]
            elif "--download_lang" in arg:
                lang = arg.split("=")[1]
                if lang == "Deutsch":
                    lang = 1
                elif lang == "Eng-Sub":
                    lang = 2
                elif lang == "Ger-Sub":
                    lang = 3
                else:
                    print("Invalid Language. Supported Languages: Deutsch, Eng-Sub, Ger-Sub")
                    exit()
                self.download_lang = lang
            elif "--dl-mode" in arg:
                self.dl_mode = arg.split("=")[1]
            elif "--season_override" in arg:
                self.season_override = arg.split("=")[1]
            elif "--provider" in arg:
                self.provider = arg.split("=")[1]
            elif "--episode_override" in arg:
                self.episode_override = arg.split("=")[1]
            elif "--max_concurrent_downloads" in arg:
                self.max_concurrent_downloads = arg.split("=")[1]
            elif "--max_retries" in arg:
                self.max_retries = arg.split("=")[1]
            elif "--wait_time" in arg:
                self.wait_time = arg.split("=")[1]
            elif "--disable_wait_threads" in arg:
                self.disable_wait_threads = arg.split("=")[1]
            elif "--output_dir" in arg:
                self.output_dir = arg.split("=")[1]
            elif "--help" in arg:
                print(help_options)
                exit()
            elif "--debug_logging" in arg:
                debug_logging = arg.split("=")[1]
                print("Debug Logging: ", debug_logging)
                if debug_logging == "True":
                    global debug_log
                    debug_log = True
        self.url = "{}/stream/{}/".format(self.site_url[self.media], self.name)
        return True