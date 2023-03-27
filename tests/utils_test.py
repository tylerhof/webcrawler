import unittest

from expression import Ok

from webcrawler.utils import GoogleSearch
from webcrawler_tests.test_utils import FunctorTest


class UtilsTest(unittest.TestCase):

    def test_google_search(self):
        FunctorTest.test(self, GoogleSearch(),
                         "Bing", Ok(['https://www.bing.com/']), num_results=1)


if __name__ == '__main__':
    unittest.main()
