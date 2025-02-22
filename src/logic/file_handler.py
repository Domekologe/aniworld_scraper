import os
import shutil

from logic.logging_handler import logger

from logic.global_handler import GlobalHandler

def check_write_perms():
    """
    Check if we have write permissions in the OUTPUT dir.

    Returns:
        bool: True if we have write permissions, False otherwise.
    """
    output_dir = GlobalHandler().output_dir
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(f"{output_dir}/write_test.txt", "w") as f:
            f.write("test")
        return True
    except PermissionError:
        return False
    finally:
        try:
            os.remove(f"{output_dir}/write_test.txt")
        except FileNotFoundError:
            pass

def check_if_already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.log("INFO", "Episode {} already downloaded.".format(file_name))
        return True
    logger.log("DEBUG", "File not downloaded. Downloading: {}".format(file_name))
    return False

def check_for_ffmpeg():
    """
    Check if ffmpeg is installed on the system.

    Returns:
        bool: True if ffmpeg is installed, False otherwise.
    """
    program_path = shutil.which("ffmpeg")
    if program_path:
        return True
    if os.name == "nt":
        exe_path = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.isfile(exe_path):
            return True
    return False

def create_output_folder(output_dir):
    """
    Create the output folder if it does not exist.

    Parameters:
        output_dir (String): Path to the output folder.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)