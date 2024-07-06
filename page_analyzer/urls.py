from urllib.parse import urlparse
from validators.url import url as valid_url
from bs4 import BeautifulSoup


def validate_url(url):
    return valid_url(url)


def normalize_url(url):
    o = urlparse(url)
    if o.scheme and o.netloc:
        return o.scheme + "://" + o.netloc
    else:
        return False


def extract_seo_data(content):
    soup = BeautifulSoup(content, "html.parser")
    h1 = soup.h1.text if soup.h1 else ""
    title = soup.title.text if soup.title else ""
    meta_desc = soup.find("meta", {"name": "description"})
    description = meta_desc.get("content") if meta_desc else ""
    return {
        "h1": h1,
        "title": title,
        "description": description
    }
