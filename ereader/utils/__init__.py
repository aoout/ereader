from bs4 import BeautifulSoup

from .epubparser import EpubParser
from .persistentdict import data


def addCssToHtml(css, html) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    style_tag = soup.new_tag('style')
    style_tag.string = css
    soup.head.append(style_tag)
    return str(soup)
