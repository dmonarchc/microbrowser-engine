import sys

from microbrowser.browser import load
from microbrowser.url import URL


DEFAULT_URL = "file:///C:/Users/ciste/OneDrive/Escritorio/Code/microbrowser-engine/examples/test.html"


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    load(URL(url))


if __name__ == "__main__":
    main()
