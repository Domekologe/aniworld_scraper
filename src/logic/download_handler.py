import base64
import random
import string
import subprocess
import time
import urllib.request
import re
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from threading import Thread, active_count
import sys
from jsbeautifier.unpackers import UnpackingError
from bs4 import BeautifulSoup

from logic.logging_handler import Logger
logger = Logger()

from logic.global_handler import GlobalHandler

VOE_PATTERNS = [
    re.compile(r"'hls': '(?P<url>.+)'"),
    re.compile(r'prompt\("Node",\s*"(?P<url>[^"]+)"'),
    re.compile(r"window\.location\.href = '(?P<url>[^']+)'")
]
STREAMTAPE_PATTERN = re.compile(r'get_video\?id=[^&\'\s]+&expires=[^&\'\s]+&ip=[^&\'\s]+&token=[^&\'\s]+\'')
DOODSTREAM_PATTERN_URL = re.compile(r"'(?P<url>/pass_md5/[^'.*]*)'")
DOODSTREAM_PATTERN_TOKEN = re.compile(r"token=(?P<token>[^&.*]*)&")

# ------------------------------------------------------- #
# Code from https://github.com/beautifier/js-beautify/blob/main/python/jsbeautifier/unpackers/packer.py
beginstr = ""
endstr = ""
def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    juicers = [
        (r"}\('(.*)', *(\d+|\[\]), *(\d+), *'(.*)'\.split\('\|'\), *(\d+), *(.*)\)\)"),
        (r"}\('(.*)', *(\d+|\[\]), *(\d+), *'(.*)'\.split\('\|'\)"),
    ]
    for juicer in juicers:
        args = re.search(juicer, source, re.DOTALL)
        if args:
            a = args.groups()
            if a[1] == "[]":
                a = list(a)
                a[1] = 62
                a = tuple(a)
            try:
                return a[0], a[3].split("|"), int(a[1]), int(a[2])
            except ValueError:
                raise UnpackingError("Corrupted p.a.c.k.e.r. data.")

    # could not find a satisfying regex
    raise UnpackingError(
        "Could not make sense of p.a.c.k.e.r data (unexpected code structure)"
    )

def _replacestrings(source):
    global beginstr
    global endstr
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = "%s[%%d]" % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return beginstr + source + endstr


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""

    ALPHABET = {
        62: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        95: (
            " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        ),
    }

    def __init__(self, base):
        self.base = base

        # fill elements 37...61, if necessary
        if 36 < base < 62:
            if not hasattr(self.ALPHABET, self.ALPHABET[62][:base]):
                self.ALPHABET[base] = self.ALPHABET[62][:base]
        # attrs = self.ALPHABET
        # print ', '.join("%s: %s" % item for item in attrs.items())
        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            # Build conversion dictionary cache
            try:
                self.dictionary = dict(
                    (cipher, index) for index, cipher in enumerate(self.ALPHABET[base])
                )
            except KeyError:
                raise TypeError("Unsupported base encoding.")

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base**index) * self.dictionary[cipher]
        return ret


def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError("Malformed p.a.c.k.e.r. symtab.")

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError("Unknown p.a.c.k.e.r. encoding.")

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    payload = payload.replace("\\\\", "\\").replace("\\'", "'")
    if sys.version_info.major == 2:
        source = re.sub(r"\b\w+\b", lookup, payload)
    else:
        source = re.sub(r"\b\w+\b", lookup, payload, flags=re.ASCII)
    return _replacestrings(source)

# ------------------------------------------------------- #

def http_save_file(url, file_path):
    """
    Directly download a file from a url.
    Comparable to CTRL + S in a browser.

    Parameters:
        url (String): url of the file.
        file_path (String): path to save the file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    file_name = file_path.split("/")[-1]
    try:
        logger.log("LOADING", "Downloading: {}".format(file_name))
        print(url)
        urllib.request.urlretrieve(url, file_path)
        logger.add_success_item({"file_name": file_name})
        return True
    except URLError as e:
        logger.add_error_item({"file_name": file_name, "error": e})
        logger.log("ERROR", "Could not download file: {}".format(file_name))
        logger.exception(e)
        return False
    except Exception as e:
        logger.add_error_item({"file_name": file_name, "error": e})
        logger.log("ERROR", "Could not download file: {}".format(file_name))
        logger.exception(e)
        return False

def download_hls_stream(hls_url, file_path):
    """
    Download an HLS stream and save it as a file.

    Parameters:
        hls_url (String): url of the HLS stream.
        file_name (String): name of the file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    file_name = file_path.split("/")[-1]
    try:
        logger.log("LOADING", "Downloading: {}".format(file_name))
        # DEBUG LOG: "-report",
        ffmpeg_cmd = ["ffmpeg", "-i", hls_url, "-c", "copy", file_path , "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.log("INFO", "Finished download of {}.".format(file_name))
        logger.add_success_item({"file_name": file_name})
        return True
    except subprocess.CalledProcessError as e:
        logger.exception(e)
        logger.add_error_item({"file_name": file_name, "error": e})
        logger.log("ERROR", "Could not download {}. Please manually download it later.".format(file_name))
        return False
    except Exception as e:
        logger.add_error_item({"file_name": file_name, "error": e})
        logger.log("ERROR", "Could not download {}. Please manually download it later.".format(file_name))
        logger.exception(e)
        return False

# todo think about this again...
def choose_download_mode(url, name, provider):
    """
    Choose the download mode based on the provider.

    Parameters:
        url (String): url of the file.
        name (String): name of the file.
        provider (String): provider of the file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    t = None
    if provider == "hls":
        t = Thread(target=download_hls_stream, args=(url, name))
    elif provider == "http":
        t = Thread(target=http_save_file, args=(url, name))
    else:
        logger.log("ERROR", "Provider not supported.")
        return False
    t.start()


def start_download(url, provider, output_dir):
    """
    Start the download process.

    Parameters:
        url (String): url of the file.
        output_dir (String): Output Folder.
        provider (String): provider of the file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    max_concurrent_downloads = GlobalHandler().max_concurrent_downloads
    wait_time = GlobalHandler().wait_time
    disable_wait_threads = GlobalHandler().disable_wait_threads
    if not disable_wait_threads:
        active_threads = active_count()
        if active_threads >= max_concurrent_downloads:
            logger.log("INFO", "Max concurrent downloads reached. Waiting for a free thread.")
            while active_count() >= max_concurrent_downloads:
                logger.log("DEBUG", "Active Threads: {}".format(active_count()))
                time.sleep(wait_time)
    hls_providers = ["VOE", "Filemoon"]
    http_providers = ["Vidoza", "Streamtape", "SpeedFiles", "Doodstream"]
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'Referer' :'https://aniworld.to/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        html_page = urllib.request.urlopen(req)
    except URLError as e:
        logger.log("ERROR", f"{e}")
        logger.log("INFO", "An Error has occured.")
        # todo repeat handler
        return False
    if provider == "Vidoza":
        html_page = html_page.read().decode('utf-8')
        soup = BeautifulSoup(html_page, features="html.parser")
        cache_link = soup.find("source").get("src")
    elif provider == "SpeedFiles":
        html_page = html_page.read().decode('utf-8')
        link = re.search(r'src="([^"]+)"', html_page.read().decode('utf-8')).group(1)
        if "store_access" in link:
            cache_link = link
    elif provider == "Streamtape":
        # Obsolete???
        html_page = html_page.read().decode('utf-8')
        cache_link = STREAMTAPE_PATTERN.search(html_page.read().decode('utf-8'))
        cache_link = "https://" + provider + ".com/" + cache_link.group()[:-1]

    elif provider == "Filemoon":
        html_page = html_page.read().decode('utf-8')
        soup = BeautifulSoup(html_page, features="html.parser")
        stream_link = soup.find("iframe").get("src")
        for script in soup.find_all("script"):
            if "$.cookie" in script.text:
                cookie = script.text.replace("\n", "").replace("\t", "").replace(" ", "").replace("{expires:10}" , "").replace(";", "").replace("$.cookie(", "").replace(")", "")
                file_id = cookie.split(",")[1].split("'")[1]
                aff = cookie.split(",")[3].split("'")[1]
                ref_url = cookie.split(",")[5].split("'")[1]
                break
        base_url = f"{stream_link.split('/')[2]}"
        try:
            req = urllib.request.Request(
                stream_link,
                data=None,
                headers={
                    'Host': base_url,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
                    'Accept-Language': 'en-GB,en;q=0.5',
                    'Alt-Used': base_url,
                    'Connection': 'keep-alive',
                    'Cookie': f'file_id={file_id}; aff={aff}; ref_url={ref_url}; lang=1',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'iframe',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site',
                    'Priority': 'u=4',
                    'TE': 'trailers',
                }
            )
            html_page = urllib.request.urlopen(req)
            soup = BeautifulSoup(html_page, features="html.parser")
            packed_script = soup.find_all("script")[-1].text
            unpacked = unpack(packed_script)
            cache_link = re.search(r'file:"([^"]+)"', unpacked).group(1)
            print(cache_link)
        except HTTPError as e:
            logger.log("ERROR", f"{e}")
            logger.log("INFO", "An Error has occured.")
    elif provider == "Doodstream":
        logger.log("ERROR", "Doodstream is not supported yet.")
        return False
        referer = html_page.geturl()
        html_page = html_page.read().decode('utf-8')
        match_url = DOODSTREAM_PATTERN_URL.search(html_page)
        match_token = DOODSTREAM_PATTERN_TOKEN.search(html_page)
        if match_url and match_token:
            logger.log("DEBUG", "Found Doodstream URL.")
            parsed_url = urlparse(referer)
            req = urllib.request.Request(
                f"{parsed_url.scheme}://{parsed_url.netloc}" + match_url.group('url'),
                data=None,
                headers={
                    'Referer': referer,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'
                }
            )
            req_body = urllib.request.urlopen(req).read().decode('utf-8')
            dood_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            expiry = int(round(time.time() * 1000)) + 50
            cache_link = f"{req_body}{dood_hash}?token={match_token.group('token')}&expiry={expiry}"
            logger.log("DEBUG",f"Video URL: {cache_link}")
        else:
            logger.log("ERROR", "Could not find Doodstream URL.")
            return False
    elif provider == "VOE":
        html_page = html_page.read().decode('utf-8')
        for pattern in VOE_PATTERNS:
            match = pattern.search(html_page)
            if match:
                cache_link = match.group('url')
                break
        if not "node" in cache_link:
            new_page = urllib.request.urlopen(cache_link).read().decode('utf-8')
            for pattern in VOE_PATTERNS:
                match = pattern.search(new_page)
                if match:
                    cache_link_b64 = match.group('url')
                    cache_link = base64.b64decode(cache_link_b64).decode('utf-8')
                    break
    else:
        logger.log("ERROR", "Provider not supported.")
        return False
    try:
        if provider in http_providers:
            choose_download_mode(cache_link, output_dir, "http")
        elif provider in hls_providers:
            choose_download_mode(cache_link, output_dir, "hls")
    except NameError:
        logger.log("ERROR", "Something went really wrong... Cache link is None.")
        return False

    return True