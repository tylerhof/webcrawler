import random
from io import StringIO
from urllib.parse import urlparse
from googlesearch import search

import lxml.etree as etree
import requests
from exceptionhandling.access import Access
from exceptionhandling.exception_handler import ExceptionHandler, Safe, IdentityPolicy
from exceptionhandling.functor import Functor
from exceptionhandling.strings import Decode, Json
from exceptionhandling.utils import Compose
from lxml import html


class ImFeelingLucky(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.parser = etree.HTMLParser()
        self.google_template = r'http://www.google.com/search?q={input}&btnI'

    def apply(self, input, **kwargs):
        var = requests.get(self.google_template.format(input=input.replace(' ', '+')))
        tree = etree.parse(StringIO(var.text), self.parser)
        return tree.xpath('//a')[0].text


class GoogleSearch(Functor):

    def apply(self, input, **kwargs):
        return list(search(input, **kwargs))[1:]


class GetDomain(Functor):

    def apply(self, input, **kwargs):
        return urlparse(input).netloc


class GetProxy(Functor):
    def __init__(self, rotating_ip_addresses=None):
        super().__init__(IdentityPolicy())
        if rotating_ip_addresses is None:
            rotating_ip_addresses = []
        self.rotating_ip_addresses = rotating_ip_addresses

    def apply(self, input, **kwargs):
        if len(self.rotating_ip_addresses) > 0:
            proxy = random.randint(0, len(self.rotating_ip_addresses) - 1)
            return {"http": self.rotating_ip_addresses[proxy], "https": self.rotating_ip_addresses[proxy]}
        else:
            return {}


class GetRest(Functor):
    def apply(self, input, **kwargs):
        return requests.get(input, **kwargs)


class GetRestJson(Functor):
    def __init__(self, rotating_ip_addresses=None):
        super().__init__(IdentityPolicy())
        self.inner_functor = Compose(GetRest(), Access('_content'), Decode(), Json())
        self.get_proxy = GetProxy(rotating_ip_addresses)

    def apply(self, input, **kwargs):
        return self.inner_functor(input, proxies=self.get_proxy(input, **kwargs), **kwargs)


class PostRest(Functor):
    def apply(self, input, **kwargs):
        return requests.post(input, **kwargs)


class PostRestJson(Functor):
    def __init__(self, rotating_ip_addresses=None):
        super().__init__(IdentityPolicy())
        self.inner_functor = Compose(PostRest(), Access('_content'), Decode(), Json())
        self.get_proxy = GetProxy(rotating_ip_addresses)

    def apply(self, input, **kwargs):
        return self.inner_functor(input, proxies=self.get_proxy(input, **kwargs), **kwargs)


class HtmlParser(Functor):

    def apply(self, input, **kwargs):
        return html.fromstring(input)


class XPathParser(Functor):

    def __init__(self, xpath, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.xpath = xpath

    def apply(self, input, **kwargs):
        return input.xpath(self.xpath)
