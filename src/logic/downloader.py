import os
import platform
import subprocess
import time
from os import path, remove
from threading import Thread

import requests

from src.custom_logging import setup_logger
from src.failures import append_failure, remove_file
from src.successes import append_success

logger = setup_logger(__name__)

MAX_RETRIES = 3

def already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.info("Episode {} already downloaded.".format(file_name))
        return True
    logger.debug("File not downloaded. Downloading: {}".format(file_name))
    return False


def download(link, file_name):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        logger.debug(f"Attempt {retry_count + 1}: Link: {link}, File_Name: {file_name}")
        try:
            r = requests.get(link, stream=True, timeout=10)
            r.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            if path.getsize(file_name) > 0:
                logger.success(f"Finished download of {file_name}.")
                append_success(file_name)
                return
            else:
                logger.warning(f"Downloaded file {file_name} is empty.")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {file_name}: {e}")
        
        retry_count += 1
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying download of {file_name} in 10 seconds...")
            time.sleep(10)
    
    logger.error(f"Server error. Could not download {file_name}. Please manually download it later.")
    append_failure(file_name)
    if path.exists(file_name):
        remove(file_name)


def download_and_convert_hls_stream(hls_url, file_name):
    if path.exists("ffmpeg.exe"):
        ffmpeg_path = "ffmpeg.exe"
    elif path.exists("src/ffmpeg.exe"):
        ffmpeg_path = "src/ffmpeg.exe"
    else:
        ffmpeg_path = "ffmpeg"

    try:
        tmp_file_name = file_name.replace(".mp4", "_tmp.mp4")
        if path.exists(tmp_file_name):
            os.remove(tmp_file_name)
            logger.info("Found broken download. Removed {}.".format(tmp_file_name))
        ffmpeg_cmd = [ffmpeg_path, '-i', hls_url, '-c', 'copy', tmp_file_name]
        if platform.system() == "Windows":
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.rename(tmp_file_name, file_name)
        logger.success("Finished download of {}.".format(file_name))
        append_success(file_name)
    except subprocess.CalledProcessError as e:
        logger.error("Server error. Could not download {}. Please manually download it later.".format(file_name))
        append_failure(file_name)
        remove_file(file_name)


def create_new_download_thread(url, file_name, provider) -> Thread:
    logger.debug("Entered Downloader.")
    t = None
    if provider in ["Vidoza", "Streamtape"]:
        t = Thread(target=download, args=(url, file_name))
        t.start()
    elif provider == "VOE":
        t = Thread(target=download_and_convert_hls_stream, args=(url, file_name))
        t.start()
    logger.loading("Provider {} - File {} added to queue.".format(provider, file_name))
    return t
