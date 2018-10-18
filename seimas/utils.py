from html import unescape
from logging import getLogger

from bs4 import BeautifulSoup

logger = getLogger(__name__)


def parse_xml(xml_text):
    return BeautifulSoup(xml_text, 'xml')


def try_parse_int(value):
    if value:
        try:
            return int(value)
        except ValueError:
            return None


def sanitize_text(text):
    if text is None:
        return None

    return unescape(text).strip()
