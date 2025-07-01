# constants.py
import os
import sys
import re
from src.custom_logging import setup_logger

logger = setup_logger(__name__)

APP_VERSION = "v02-20"
episode_override = 0
ddos_protection_calc = 5
ddos_wait_timer = 60
max_download_threads = 5
thread_download_wait_timer = 30
disable_thread_timer = False

provider_priority = ["VOE", "Vidoza", "Streamtape"]
site_url = {
    "serie": "https://s.to",
    "anime": "https://aniworld.to"
}

def resolve_output_root(path_override: str | None) -> tuple[str, bool]:
    if path_override and (
        os.path.isabs(path_override) or (len(path_override) > 1 and path_override[1] == ':')
    ):
        logger.info(f"--path-override set: {path_override}")
        logger.info(f"Using absolute path: {path_override}")
        return path_override, True
    elif path_override:
        rel = os.path.join(os.getcwd(), path_override)
        logger.info(f"--path-override set: {path_override}")
        logger.info(f"Using relative path (project directory): {rel}")
        return rel, False
    else:
        default_path = os.path.join(os.getcwd(), "output")
        logger.info("--path-override not set, using default path: " + default_path)
        return default_path, False

def build_url(media_type: str, name: str) -> str:
    return f"{site_url[media_type]}/{media_type}/stream/{name}/"
