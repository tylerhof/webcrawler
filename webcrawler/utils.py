from io import StringIO
import requests
import lxml.etree as etree
from exceptionhandling.exception_handler import ExceptionHandler, Safe
from exceptionhandling.functor import Functor
from urllib.parse import urlparse

class ImFeelingLucky(Functor):

    def __init__(self, policy: ExceptionHandler = Safe()):
        super().__init__(policy)
        self.parser = etree.HTMLParser()
        self.google_template = r'http://www.google.com/search?q={input}&btnI'

    def apply(self, input):
        var = requests.get(self.google_template.format(input = input.replace(' ', '+')))
        tree = etree.parse(StringIO(var.text), self.parser)
        return tree.xpath('//a')[0].text

class GetDomain(Functor):

    def apply(self, input):
        return urlparse(input).netloc

