import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from tidylib import tidy_document
from urllib3 import Retry


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def parse_invalid_xml(xml_text):
    content, _ = tidy_document(xml_text, {"input_xml": True})

    return BeautifulSoup(content, 'xml')
