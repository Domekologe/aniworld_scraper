from logic.logging_handler import logger
import urllib.request
from urllib.error import URLError

from bs4 import BeautifulSoup


class Request_Handler:
    def __init__(self):
        self.cache_url_attempts = 0

    def get_year(self, url):
        """
        Get the year of the show.

        Parameters:
            url (String): url of the show.

        Returns:
            year (String): year of the show.
        """
        try:
            html_page = urllib.request.urlopen(url)
            soup = BeautifulSoup(html_page, features="html.parser")
            year = soup.find("span", {"itemprop": "startDate"}).text
            return year
        except AttributeError:
            logger.log("ERROR", "Could not find year of the show.")
            return 0


    def get_redircet_link(self, site_url, language, requested_provider=None):
        """
        Get the redirect link to the video file.

        Parameters:
            site_url (String): serie or anime site. [https://aniworld.to/anime/stream/angels-of-death]
            language (String): desired language to download the video file in.
            requested_provider (String): define the provider to use if NONE use provider_priority.

        Returns:
            get_redirect_link(): returns link_to_redirect and provider.
        """
        if not site_url.startswith("https://"):
            logger.log("ERROR", "Invalid Site URL")
            return None
        html_response = urllib.request.urlopen(site_url)
        soup = BeautifulSoup(html_response, features="html.parser")
        languages = soup.find("div", {"class": "changeLanguageBox"}).find_all("img")
        supported_langs = []
        for lang in languages:
            supported_langs.append(int(lang.get("data-lang-key")))
        if not language in supported_langs:
            # todo 1. Translate 2. IDs to names.
            logger.log("ERROR", "Language not supported.")
            logger.log("INFO", "Supported Languages: " + str(supported_langs))
            return None
        # Lang 1 = German, Lang 2 = ENG-Sub, Lang 3 = DE-SUB
        all_providers = soup.find("ul", {"class": "row"})
        provider_list = []
        for provider in all_providers.find_all("li"):
            redirect_link = provider.find("a").get("href")
            provider_name = provider.find("h4").text
            data_lang_key = int(provider["data-lang-key"])
            provider_list.append((provider_name, redirect_link, data_lang_key))
        url = None
        base_url = f"https://{site_url.split('/')[2]}"
        if requested_provider:
            for provider in provider_list:
                if provider[0] == requested_provider and provider[2] == language:
                    url = base_url + provider[1]
                    break
        if not url:
            if requested_provider:
                logger.log("ERROR", "Requested Provider not found.")
                logger.log("INFO", "Using next best provider.")
            for provider in provider_list:
                if provider[2] == language:
                    url = base_url + provider[1]
                    requested_provider = provider[0]
                    break
        # todo speed check list
        return {"url": url, "provider": requested_provider}


    def get_season(self, url_path):
        logger.log("DEBUG", "Entered get_season")
        logger.log("DEBUG", "URL Path: " + url_path)
        counter_seasons = 1
        html_page = urllib.request.urlopen(url_path, timeout=50)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll('a'):
            seasons = str(link.get("href"))
            if "/staffel-{}".format(counter_seasons) in seasons:
                counter_seasons = counter_seasons + 1
        logger.log("DEBUG", "Now leaving Function get_season")
        return counter_seasons - 1


    def get_episodes(self, url_path, season_count):
        logger.log("DEBUG", "Entered get_episodes")
        url = "{}staffel-{}/".format(url_path, season_count)
        episode_count = 1
        html_page = urllib.request.urlopen(url, timeout=50)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll('a'):
            episode = str(link.get("href"))
            if "/staffel-{}/episode-{}".format(season_count, episode_count) in episode:
                episode_count = episode_count + 1
        logger.log("DEBUG", "Now leaving Function get_episodes")
        return episode_count - 1


    def get_movies(self, url_path):
        logger.log("DEBUG", "Entered get_movies")
        url = "{}filme/".format(url_path)
        movie_count = 1
        html_page = urllib.request.urlopen(url, timeout=50)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll('a'):
            movie = str(link.get("href"))
            if "/filme/film-{}".format(movie_count) in movie:
                movie_count = movie_count + 1
        logger.log("DEBUG", "Now leaving Function get_movies")
        return movie_count - 1


request_handler = Request_Handler()