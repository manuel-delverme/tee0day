import tempfile

# from .parse import parse_args
from seleniumwire import webdriver

from downloader import yandex_get


def main(keyword):
    keyword = str(keyword).strip()
    with webdriver.Chrome(executable_path="./chromedriver") as driver:
        with tempfile.TemporaryDirectory() as tmpdir:
            images = yandex_get(driver, tmpdir, keyword)
    print(images)


if __name__ == "__main__":
    main(keyword='"Dragon\'s Dogma" logo')
