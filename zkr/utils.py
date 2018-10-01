from urllib.parse import urlsplit

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from seimas.utils import logger


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


def file_extension(file_name):
    return file_name.split('.')[-1]


def save_image_from_url(field, url):
    r = requests_retry_session().get(url)

    if r.ok:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()

        img_filename = urlsplit(url).path[1:]
        try:
            field.save(img_filename, File(img_temp), save=True)
        except OSError:
            return False
        except ValueError as ex:
            logger.warning(ex, exc_info=True)
            return False

        return True
    elif r.status_code == 404:
        return False
    else:
        logger.warning("Unable to save image from url", exc_info=True)

    return False


def request_country(request):
    country = request.META.get('CF-IPCountry', None)

    return country if country != 'XX' else None
