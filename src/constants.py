import sys
import os
import re
import argparse

from src.custom_logging import setup_logger

logger = setup_logger(__name__)

def check_for_old_parse():
    if sys.argv[1] == "serie" or sys.argv[1] == "anime":
        return True
    else:
        return False

use_old_parse = check_for_old_parse()

def parse_cli_arguments(default: str | int, position: int) -> str | int:
    try:
        cli_argument: str = sys.argv[position]
        logger.debug(f"cli argument detected on position:{position} with value:{cli_argument}")
        if type(default) is int:
            cli_argument: int = int(cli_argument)
        return cli_argument
    except IndexError:
        logger.debug(f"no cli argument detected on position:{position}. Using default value:{default}")
        return default

args_pattern = re.compile(
    r"("
    r"(--(?P<HELP>help).*)|"
    r"((?:-t|--type)\s(?P<TYPE>serie|anime))|"
    r"((?:-n|--name)\s(?P<NAME>[\w\-]+))|"
    r"((?:-l|--lang)\s(?P<LANG>Deutsch|Ger-Sub|English))|"
    r"((?:-m|--dl-mode)\s(?P<MODE>Series|Movies|All))|"
    r"((?:-s|--season-override)\s(?P<SEASON>\d+\+?))|"
    r"((?:-p|--provider)\s(?P<PROVIDER>VOE|Streamtape|Vidoza))"
    r")"
)

def args_parse():
    arg_line = " ".join(sys.argv[1:])
    args: dict[str, str] = {}
    if match_objects := args_pattern.finditer(arg_line):
        for match_object in match_objects:
            for item in match_object.groupdict().items():
                if item[1] != None:
                    args[item[0]] = item[1]
    return args

arguments = args_parse() if use_old_parse == False else {}

def get_arg(name: str, default: str | int = None):
    return arguments.get(name, default)

# ------------------------------------------------------- #
#                   definitions
# ------------------------------------------------------- #
APP_VERSION = "v02-19"

# ------------------------------------------------------- #
#                   argparse config
# ------------------------------------------------------- #
parser = argparse.ArgumentParser()

parser.add_argument('--type', '-t', type=str, default='anime', choices=['serie', 'anime'])
parser.add_argument('--name', '-n', type=str, default='Name-Goes-Here')
parser.add_argument('--lang', '-l', type=str, default='Deutsch', choices=['Deutsch', 'Ger-Sub', 'English'])
parser.add_argument('--dl-mode', '-m', type=str, default='Series', choices=['Series', 'Movies', 'All'])
parser.add_argument('--season-override', '-s', type=int, default=0)
parser.add_argument('--provider', '-p', type=str, default='VOE', choices=['VOE', 'Streamtape', 'Vidoza'])
parser.add_argument('--path-override', type=str)  # No default → allows detection if argument was provided

args = parser.parse_args()




type_of_media = args.type
name = args.name
language = args.lang
dlMode = args.dl_mode
season_override = args.season_override
cliProvider = args.provider

# Determine output root based on --path-override argument
if args.path_override:
    logger.info(f"--path-override set: {args.path_override}")
    # Check if absolute path (e.g. D:\ or /something)
    if os.path.isabs(args.path_override) or (len(args.path_override) > 1 and args.path_override[1] == ':'):
        # Absolute path → use as root
        output_root = args.path_override
        logger.info(f"Using absolute path: {output_root}")
    else:
        # Relative path → use under project directory
        output_root = os.path.join(os.getcwd(), args.path_override)
        logger.info(f"Using relative path (project directory): {output_root}")
else:
    # No argument provided → use default "output" under project directory
    output_root = os.path.join(os.getcwd(), "output")
    logger.info(f"--path-override not set, using default path: {output_root}")
    
output_name = name
output_path = os.path.join(output_root, output_name)

# Other global settings
episode_override = 0  # 0 = no override. 1 = episode 1. etc...
ddos_protection_calc = 5
ddos_wait_timer = 60  # in seconds
max_download_threads = 5 # This does NOT limit the threads but won't start more when the DDOS Timer starts.
thread_download_wait_timer = 30  # in seconds
disable_thread_timer = False # If true the script will start downloads as soon as the ddos protection is over.
#output_root = path_override  

if os.path.isabs(args.path_override) or (len(args.path_override) > 1 and args.path_override[1] == ':'):
    output_root = args.path_override
    is_absolute_override = True
else:
    output_root = os.path.join(os.getcwd(), args.path_override or "output")
    is_absolute_override = False

site_url = {
    "serie": "https://s.to",  # maybe you need another dns to be able to use this site
    "anime": "https://aniworld.to"
}
provider_priority = ["VOE", "Vidoza", "Streamtape"]

url = "{}/{}/stream/{}/".format(site_url[type_of_media], type_of_media, name)

