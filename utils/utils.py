import hashlib
from json import dumps
from logging import getLogger
from urllib.parse import urlsplit, unquote, urlparse, parse_qsl, urlencode, ParseResult

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.paginator import Page, Paginator
from django.utils.timezone import now
from ipware import get_client_ip
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from utils.models import RequestInformation

logger = getLogger(__name__)


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
) -> requests.Session:
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


def file_extension(file_name) -> str:
    return file_name.split('.')[-1]


def save_image_from_url(field, url) -> bool:
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


def get_request_information(request):
    client_ip, _ = get_client_ip(request)

    country = request.META.get('HTTP_CF_IPCOUNTRY', None)
    client_country = country if country != 'XX' else None

    client_user_agent = request.META.get('HTTP_USER_AGENT', None)

    return RequestInformation(
        client_ip=client_ip,
        client_country=client_country,
        client_user_agent=client_user_agent
    )


def django_now():
    return now()


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = {k: v for k, v in parsed_get_args.items() if v is not None}

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


def gravatar_url(email, size):
    gravatar_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    gravatar_arguments = urlencode({'s': str(size), 'd': 'mp'})

    return f"https://www.gravatar.com/avatar/{gravatar_hash}?{gravatar_arguments}"


def first_or_none(arr):
    return arr[0] if arr else None


def distinct_by(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)

        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


class PageWithPageLink(Page):
    def __init__(self, page_link_function, query_params, object_list, number, paginator):
        self._page_link_function = page_link_function
        self._query_params = query_params
        super().__init__(object_list, number, paginator)

    def add_query_params(self, link):
        if self._query_params:
            return f"{link}?{self._query_params}"
        return link

    def previous_page_link(self):
        if self.has_previous():
            return self.page_link(self.previous_page_number())

    def next_page_link(self):
        if self.has_next():
            return self.page_link(self.next_page_number())

    def page_link(self, page_number):
        return self.add_query_params(self._page_link_function(page_number))


class PaginatorWithPageLink(Paginator):
    def _get_page(self, *args, **kwargs):
        return PageWithPageLink(self._page_link_function, self._query_params, *args, **kwargs)

    def __init__(self, object_list, page_link_function, per_page=30, orphans=0, allow_empty_first_page=True,
                 query_params=None):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self._page_link_function = page_link_function
        self._query_params = query_params


def try_parse_int(value):
    if value:
        try:
            return int(value)
        except ValueError:
            return None
