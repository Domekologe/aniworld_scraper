from logic.logging_handler import Logger, get_translation
logger = Logger()

from logic.global_handler import GlobalHandler
from logic.file_handler import check_write_perms, check_for_ffmpeg, create_output_folder, check_if_already_downloaded
from logic.request_handler import request_handler
from logic.download_handler import start_download

global_handler = GlobalHandler()

import sys


def user_interface():
    # why does this already look like the worst code ever?
    logger.log("INFO", get_translation("choose_language"))
    logger.log("INFO", get_translation("language_list"))
    # todo placeholder input
    lang = input("Input: ")
    while lang not in ["1", "2", "q"]:
        logger.log("ERROR", get_translation("invalid_language"))
        lang = input("Input: ")
    if lang == "q":
        exit()
    interface_language = "en" if lang == "1" else "de"
    Logger().lang = interface_language
    # todo fix what ever you did here

    logger.log("INFO", get_translation("language_selected", values=[interface_language]))
    logger.log("INFO",  get_translation("welcome"))
    logger.log("INFO", get_translation("get_media_type"))
    media = input("Input: ")
    while media not in ["1", "2"]:
        logger.log("ERROR", get_translation("invalid_media_type"))
        media = input("Input: ")
    if media == "1":
        media = "anime"
    else:
        media = "serie"
    global_handler["media"] = media
    logger.log("INFO", get_translation("get_name"))
    name = input("Input: ")
    while not name:
        logger.log("ERROR", get_translation("no_name_entered"))
        name = input("Input: ")
    global_handler["name"] = name

    logger.log("INFO", get_translation("get_download_lang"))
    lang = input("Input: ")
    while lang not in ["1", "2", "3"]:
        logger.log("ERROR", get_translation("invalid_language"))
        lang = input("Input: ")
    global_handler.download_lang = lang

    logger.log("INFO", get_translation("get_dl_mode"))
    dl_mode = input("Input: ")
    while dl_mode not in ["1", "2", "3"]:
        logger.log("ERROR", get_translation("invalid_dl_mode"))
        dl_mode = input("Input: ")
    if dl_mode == "1":
        dl_mode = "Series"
    elif dl_mode == "2":
        dl_mode = "Movies"
    else:
        dl_mode = "All"
    global_handler["dl_mode"] = dl_mode

    logger.log("INFO", get_translation("get_optional_parameters"))
    optianl_parameters = input("Input: ")
    if optianl_parameters.lower() == "n":
        return

    # Optional parameters
    logger.log("INFO", get_translation("get_season_override"))
    season_override = input("Input: ")
    if season_override:
        # Season override is INT unless it ends with a '+' or starts with a '+'
        if not "+" in season_override:
            try:
                global_handler["season_override"] = int(season_override)
            except ValueError:
                logger.log("ERROR", get_translation("invalid_season_override"))
    logger.log("INFO", get_translation("get_provider"))
    provider = input("Input: ")
    if provider:
        global_handler["provider"] = provider
    logger.log("INFO", get_translation("get_episode_override"))
    episode_override = input("Input: ")
    if episode_override:
        global_handler["episode_override"] = episode_override
    return


def main():
    logger.log("INFO", "---------------------------------------------------------------------")
    logger.log("INFO", f"Starting Aniworld Scraper Version {global_handler.APP_VERSION}")
    cli = global_handler.parse_cli_arguments()
    if not cli:
        user_interface()
    if not check_write_perms():
        logger.log("ERROR", "No write permissions in the output directory.")
        return
    if not check_for_ffmpeg():
        logger.log("ERROR", "ffmpeg not installed or not in the SRC Folder.")
        return

    logger.log("INFO", "Starting Aniworld Scraper.")
    logger.log("INFO", f"Version: {global_handler.APP_VERSION}")
    logger.log("INFO", f"Media: {global_handler.media}")
    logger.log("INFO", f"Name: {global_handler.name}")
    logger.log("INFO", f"Download mode: {global_handler.dl_mode}")
    logger.log("INFO", f"Download Language: {global_handler.download_lang}")
    logger.log("INFO", f"Season override: {global_handler.season_override}")
    logger.log("INFO", f"Provider: {global_handler.provider}")
    logger.log("INFO", f"Episode override: {global_handler.episode_override}")
    logger.log("INFO", f"Max concurrent downloads: {global_handler.max_concurrent_downloads}")
    logger.log("INFO", f"Max retries: {global_handler.max_retries}")
    logger.log("INFO", f"Wait time: {global_handler.wait_time}")
    logger.log("INFO", f"Disable wait threads: {global_handler.disable_wait_threads}")
    logger.log("INFO", f"Output directory: {global_handler.output_dir}")

    download_movies = False
    download_seasons = False
    if global_handler.dl_mode == "Series":
        seasons = request_handler.get_season(global_handler.url)
        download_seasons = True
    elif global_handler.dl_mode == "Movies":
        movies = request_handler.get_movies(global_handler.url)
        download_movies = True
    elif global_handler.dl_mode == "All":
        seasons = request_handler.get_season(global_handler.url)
        movies = request_handler.get_movies(global_handler.url)
        download_movies = True
        download_seasons = True
    else:
        logger.log("ERROR", "Invalid download mode.")
        return
    create_output_folder(f"{global_handler.output_dir}/{global_handler.name}")
    if download_movies:
        movie_dir = f"{global_handler.output_dir}/{global_handler.name}/Movies/"
        create_output_folder(movie_dir)
        for movie in range(movies):
            movie = movie + 1
            file_name = movie_dir + f"{global_handler.name}-{movie}.mp4"
            movie_url = f"{global_handler.url}/filme/film-{movie}"
            url = request_handler.get_redircet_link(movie_url, global_handler.download_lang, global_handler.provider)
            if not url:
                logger.add_error_item(f"Movie {movie} not found.")
                continue
            check = check_if_already_downloaded(file_name)
            if not check:
                start_download(url["url"], url["provider"], file_name)

    if download_seasons:
        for season in range(seasons):
            season = season + 1
            season_folder = f"{global_handler.output_dir}/{global_handler.name}/Season-{season}"
            create_output_folder(season_folder)
            episodes = request_handler.get_episodes(global_handler.url, season)
            for episode in range(episodes):
                episode = episode + 1
                episode_url = f"{global_handler.url}/staffel-{season}/episode-{episode}"
                url = request_handler.get_redircet_link(episode_url, global_handler.download_lang, global_handler.provider)
                if not url:
                    logger.add_error_item(f"Episode {episode} not found.")
                    continue
                file_name = season_folder + f"/{global_handler.name}-S{season}E{episode}.mp4"
                check = check_if_already_downloaded(file_name)
                if not check:
                    start_download(url["url"], url["provider"], file_name)
    logger.log("INFO", "Aniworld Scraper finished.")

# ------------------- ENTRY ------------------- #

try:
    main()
    logger.end_logging()
except Exception as e:
    logger.exception(e)
    sys.exit(3)
except KeyboardInterrupt:
    logger.log("INFO", "User aborted the program.")
    logger.end_logging()
    sys.exit(4)