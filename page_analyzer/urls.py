from urllib.parse import urlparse
from validators.url import url as valid_url
from datetime import datetime
from bs4 import BeautifulSoup


def validate_and_normalize(url):
    if valid_url(url):
        o = urlparse(url)
        if o.scheme and o.netloc:
            return o.scheme + "://" + o.netloc
        else:
            return False
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
        "description": description,
        "created_at": datetime.today()
    }
