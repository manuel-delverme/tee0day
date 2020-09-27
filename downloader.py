import itertools
import json
import multiprocessing
import pathlib
import sys
import tempfile
import time
import urllib.parse
import requests
import bs4
import snippets

DEBUG = sys.gettrace() is not None

MAIN_URL = "https://yandex.com/images/search"
MAXIMUM_FILENAME_LENGTH = 50
MAXIMUM_PAGES_PER_SEARCH = 50
MAXIMUM_IMAGES_PER_PAGE = 30
IMAGES_TO_DOWNLOAD = 2
NUM_WORKERS = max(IMAGES_TO_DOWNLOAD, 10)


def filepath_fix_existing(directory_path: pathlib.Path, name: str, filepath: pathlib.Path) -> pathlib.Path:
    new_filepath = filepath
    if filepath.exists():
        for i in itertools.count(start=1):
            new_name = f'{name} ({i}){filepath.suffix}'
            new_filepath = directory_path / new_name
            if not new_filepath.exists():
                break

    return new_filepath


@snippets.snippets.disk_cache
def cached_wget(img_url):
    print("downloading", img_url)
    return requests.get(img_url, timeout=10)


def download_single_image(img_url: str, output_directory: pathlib.Path):
    response = cached_wget(img_url)
    output_directory.mkdir(parents=True, exist_ok=True)
    if not response.ok:
        return

    with tempfile.TemporaryFile("wb", dir=output_directory, delete=False) as f:
        f.write(response.content)
        return f.name


def yandex_get(driver, output_directory, keyword):
    output_directory = pathlib.Path(output_directory)
    check_captcha_and_get(driver, MAIN_URL, params={'text': keyword, "nomisspell": 1})

    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    tag_sepr_item = soup.find_all("div", class_="serp-item")[:IMAGES_TO_DOWNLOAD]

    with multiprocessing.Pool(NUM_WORKERS) as pool:
        img_url_results = []

        for item in tag_sepr_item:
            img_url = json.loads(item.attrs["data-bem"])["serp-item"]["img_href"]
            img_url_results.append(pool.apply_async(download_single_image, args=(img_url, output_directory)))

        img_url_results = [res.get() for res in img_url_results]

    return img_url_results


def check_captcha_and_get(driver, url, params):
    del driver.requests
    driver.get(f"{url}?{urllib.parse.urlencode(params)}")

    if "captcha" in driver.current_url:
        print(f"Please, type the captcha in the browser")
        while "captcha" in driver.current_url:
            time.sleep(0.5)

    for request in driver.requests:
        if request.url == driver.current_url:
            return request.response
