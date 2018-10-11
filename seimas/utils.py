from logging import getLogger

from bs4 import BeautifulSoup
from tidylib import tidy_document

logger = getLogger(__name__)


def parse_invalid_xml(xml_text):
    content, _ = tidy_document(xml_text, {"input_xml": True})

    return BeautifulSoup(content, 'xml')


def try_parse_int(value):
    if value:
        try:
            return int(value)
        except ValueError:
            return None
