from io import StringIO
import requests
import lxml.etree as etree
from exceptionhandling.access import Access
from exceptionhandling.exception_handler import ExceptionHandler, Safe, IdentityPolicy
from exceptionhandling.functor import Functor
from exceptionhandling.strings import Decode, Json
from urllib.parse import urlparse

from exceptionhandling.utils import Compose
from lxml import html


class ImFeelingLucky(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.parser = etree.HTMLParser()
        self.google_template = r'http://www.google.com/search?q={input}&btnI'

    def apply(self, input, **kwargs):
        var = requests.get(self.google_template.format(input = input.replace(' ', '+')))
        tree = etree.parse(StringIO(var.text), self.parser)
        return tree.xpath('//a')[0].text

class GetDomain(Functor):

    def apply(self, input, **kwargs):
        return urlparse(input).netloc

class Rest(Functor):
    def apply(self, input, **kwargs):
        if 'headers' in kwargs:
            return requests.get(input, headers=kwargs['headers'])
        else:
            return requests.get(input)

class GetRestJson(Functor):
    def __init__(self):
        super().__init__(IdentityPolicy())
        self.inner_functor = Compose(Rest(), Access('_content'), Decode(), Json())

    def apply(self, input, **kwargs):
        return self.inner_functor(input, **kwargs)

class HtmlParser(Functor):

    def apply(self, input, **kwargs):
        return html.fromstring(input)

class XPathParser(Functor):

    def __init__(self, xpath, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.xpath = xpath

    def apply(self, input, **kwargs):
        return input.xpath(self.xpath)