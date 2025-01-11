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
        self.max_concurrent_downloads = 2
        self.max_retries = 4
        self.wait_time = 30
        self.disable_wait_threads = False
        self.output_dir = "output"
        self.site_url = {"serie": "https://s.to/serie","anime": "https://aniworld.to/anime"}
        self.provider_priority = ["VOE", "Streamtape", "Vidoza", "SpeedFiles", "Doodstream"] # This var is not in use yet.
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
            if arg == "--help":
                print(help_options)
                exit()
            match arg.split("=")[0]:
                case "--media":
                    self.media = arg.split("=")[1]
                case "--name":
                    self.name = arg.split("=")[1]
                case "--download_lang":
                    lang = arg.split("=")[1]
                    match lang:
                        case "Deutsch":
                            lang = 1
                        case "Eng-Sub":
                            lang = 2
                        case "Ger-Sub":
                            lang = 3
                        case _:
                            print("Invalid Language. Supported Languages: Deutsch, Eng-Sub, Ger-Sub")
                            exit()
                    self.download_lang = lang
                case "--dl-mode":
                    self.dl_mode = arg.split("=")[1]
                case "--season_override":
                    self.season_override = arg.split("=")[1]
                case "--provider":
                    self.provider = arg.split("=")[1]
                case "--episode_override":
                    self.episode_override = arg.split("=")[1]
                case "--max_concurrent_downloads":
                    self.max_concurrent_downloads = arg.split("=")[1]
                case "--max_retries":
                    self.max_retries = arg.split("=")[1]
                case "--wait_time":
                    self.wait_time = arg.split("=")[1]
                case "--disable_wait_threads":
                    self.disable_wait_threads = arg.split("=")[1]
                case "--output_dir":
                    self.output_dir = arg.split("=")[1]
                case "--debug_logging":
                    debug_logging = arg.split("=")[1]
                    print("Debug Logging: ", debug_logging)
                    if debug_logging == "True":
                        global debug_log
                        debug_log = True
                case _:
                    print("Invalid Argument: ", arg)
                    exit()
        self.url = "{}/stream/{}/".format(self.site_url[self.media], self.name)
        return True