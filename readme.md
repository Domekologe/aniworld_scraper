# Anime/Serien Scraper

Scraper for the Anime Hoster Aniworld.to and the Series Hoster S.to

How to use:

- Clone the Repo
- `pip install -r requirements.txt`
- download or install [ffmpeg](https://ffmpeg.org) (If you download it put it in the src folder)

There are two main way to run this script.

## Manual with a UI:

- Go into the `src` folder.
- Run `python start_app.py`


## Automatic with CLI arguments:

- Go into the `src` folder.
- Run `python start_app.py` with your arguments.

### Arguments:

- `--help` : Shows the help message

#### Required Arguments:

- `--media=anime|serie` : Choose between Anime and Series
- `--name=NameOfTheShow/Anime/Movie` : Name of the Show/Anime/Movie
- `--download_lang=Deutsch|Ger-Sub|English` : Choose the language of the show
- `--dl-mode=Series|Movies|All` : Choose weather to download Series Episodes, Movies or both

EXAMPLE: `python start_app.py --media=anime --name=angels-of-death --download_lang=Deutsch --dl-mode=All`

#### Optional Arguments:

- `--season_override=SeasonNumber` : Choose which season to download. 
(You can use Num+ to download all seasons starting from Num)
- `--provider=VOE|Streamtape|Vidoza|SpeedFiles` : Choose the provider to download from
- `--episode_override=EpisodeNumber` : Choose which episode to download.
- `--max_concurrent_downloads=Number` : Choose the maximum number of concurrent downloads
- `--max_retries=Number` : Choose the maximum number of retries for each download.
- `--wait_time=Number` : Choose the time to wait when max concurrent downloads are reached. 
(will not work if disable_wait_threads is set to True)
- `--disable_wait_threads=True/False` : Choose weather to wait for downloads to finish before starting new ones or not.
- `--output_dir=Path` : Choose the output directory for the downloads.
- `--debug_logging` : Toggle Debug logging messages.

EXAMPLE: `python start_app.py --media=anime --name=angels-of-death --download_lang=Deutsch --dl-mode=All --season_override=1 --provider=VOE --episode_override=1 --max_concurrent_downloads=5 --max_retries=3 --wait_time=30 --disable_wait_threads=False --output_dir=output --debug_logging=True`

## Support

Please create an Issue.

## Special Thanks:

Thank you to [Michtdu](https://github.com/Michtdu) for the workaround and code for the Captcha!

Thank you [speedyconzales](https://github.com/speedyconzales) for adding S.to support