import datetime
import os
import sys
import traceback

debug_log = False
translation_table = {
    'en': {
        'language_list': 'Available languages: 1: English, 2: German, q: Quit',
        'choose_language': 'Choose a language:',
        'language_selected': 'Language selected: {0}',
        'invalid_language': 'Invalid language',
        'welcome': 'Welcome to Aniworld Scraper.',
        'get_media_type': 'Enter the media type: 1: Anime, 2: Series',
        'get_name': 'Enter the name of the show:',
        'invalid_media_type': 'Invalid media type',
        'get_dl_mode': 'Specify what you want to download: 1: Series, 2: Movies, 3: All',
        'invalid_dl_mode': 'Invalid download mode',
        'get_season_override': 'Enter the season number:',
        'get_provider': 'Enter the provider:',
        'get_episode_override': 'Enter the episode number:',
        'invalid_season_override': 'Invalid season number',
        'invalid_episode_override': 'Invalid episode number',
        'invalid_provider': 'Invalid provider',
        'get_optional_parameters': 'Do you want to set optional parameters? (y/n)',
        'type': 'type',
        'series': 'series',
        'anime': 'anime',
        'name': 'name',
        'language': 'language',
        'lang_german': 'German',
        'lang_english': 'English',
        'get_download_lang': 'Enter the language you want to download in: 1: German, 2: English Sub, 3: German Sub',
        'log_type_error': 'ERROR',
        'log_type_info': 'INFO',
        'log_type_warning': 'WARNING',
        'log_type_loading': 'LOADING',
        'log_type_exception': 'EXCEPTION',
        'log_invalid_level': 'Invalid log level',
        'log_exception_occurred': 'An exception occurred',
        'log_year_not_found': 'Could not find year of the show.',
        'log_no_cli_arg': 'no cli argument detected',
},
    'de': {
        'language_list': 'Verfügbare Sprachen: 1: Englisch, 2: Deutsch, q: Beenden',
        'choose_language': 'Wähle eine Sprache:',
        'language_selected': 'Sprache ausgewählt: {0}',
        'invalid_language': 'Ungültige Sprache',
        'welcome': 'Willkommen beim Aniworld Scraper.',
        'get_media_type': 'Gib den Medientyp ein: 1: Anime, 2: Serie',
        'get_name': 'Gib den Namen der Show ein:',
        'invalid_media_type': 'Ungültiger Medientyp',
        'get_dl_mode': 'Gib an was du herunterladen möchtest: 1: Serien, 2: Filme, 3: Alles',
        'invalid_dl_mode': 'Ungültiger Download-Modus',
        'get_season_override': 'Gib die Staffelnummer ein:',
        'get_provider': 'Gib den Anbieter ein:',
        'get_episode_override': 'Gib die Episodennummer ein:',
        'invalid_season_override': 'Ungültige Staffelnummer',
        'invalid_episode_override': 'Ungültige Episodennummer',
        'invalid_provider': 'Ungültiger Anbieter',
        'get_optional_parameters': 'Möchtest du Optionale Parameter setzen? (y/n)',
        'type': 'Typ',
        'series': 'Serie',
        'anime': 'Anime',
        'name': 'Name',
        'language': 'Sprache',
        'lang_german': 'Deutsch',
        'lang_english': 'Englisch',
        'get_download_lang': 'Gib die Sprache ein, in der du herunterladen möchtest: 1: Deutsch, 2: Englisch Sub, 3: Deutsch Sub',
        'log_type_error': 'FEHLER',
        'log_type_info': 'INFO',
        'log_type_warning': 'WARNUNG',
        'log_type_loading': 'LADE',
        'log_type_exception': 'AUSNAHME',
        'log_invalid_level': 'Ungültiger Log-Level',
        'log_exception_occurred': 'Eine Ausnahme ist aufgetreten',
        'log_year_not_found': 'Jahr der Show konnte nicht gefunden werden.',
        'log_no_cli_arg': 'Kein CLI-Argument gefunden',
    }
}


def get_translation(message, language=None, values=None):
    if not language:
        language = Logger().lang
    if language not in translation_table:
        raise ValueError(f"Invalid language: {language}")

    if message not in translation_table[language]:
        raise ValueError(f"Invalid message: {message}")

    translation = translation_table[language][message]
    if values:
        translation = translation.format(*values)

    return translation




class Logger:
    LEVELS = {
        'DEBUG': '\033[94m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'LOADING': '\033[96m',
        'EXCEPTION': '\033[95m'
    }
    RESET = '\033[0m'

    def __init__(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        self.log_dir = 'logs'
        self.log_file = os.path.join(self.log_dir, f'log_{date_str}.log')
        self.debug_logging = debug_log
        #  todo: Translate for OS.Lang?
        self.lang = "en"
        self.success_items = None
        self.error_items = None
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def add_error_item(self, item):
        if not self.error_items:
            self.error_items = []
        self.error_items.append(item)

    def add_success_item(self, item):
        if not self.success_items:
            self.success_items = []
        self.success_items.append(item)

    def log(self, level, message):
        if level not in self.LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        if not self.debug_logging and level == 'DEBUG':
            return

        frame = sys._getframe(1)
        file_name = os.path.basename(frame.f_code.co_filename)
        func_name = frame.f_code.co_name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {level} - {file_name} - {func_name} - {message}"
        print(f"{self.LEVELS[level]}{log_message}{self.RESET}")
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')

    def exception(self, message):
        exc_info = traceback.format_exc()
        self.log('EXCEPTION', f"{message}\n{exc_info}")

    def end_logging(self):
        self.log('INFO', 'Logging finished.')
        if self.success_items:
            self.log('INFO', 'Success items:')
            for item in self.success_items:
                self.log('INFO', str(item))
        if self.error_items:
            self.log('ERROR', 'Error items:')
            for item in self.error_items:
                self.log('ERROR', str(item))
        self.log('INFO', 'Downloads may still be running in the background.')

# Example usage:
# logger = Logger()
# logger.log('INFO', 'This is an info message.')
# logger.log('ERROR', 'This is an error message.')
# try:
#     1 / 0
# except ZeroDivisionError:
#     logger.exception('An exception occurred')
