import unittest

import os
from kraken.crawler import JJDecoder


def get_real_path(rel_path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), rel_path)


class JJDecoderTest(unittest.TestCase):
    def test(self):
        with open(get_real_path('jjdecoder_tests.txt'), 'r') as tests:
            while True:
                req = tests.readline()
                if not req:
                    break
                exp = tests.readline().strip()
                result = JJDecoder.decode(req)
                self.assertEqual(exp, result)


if __name__ == '__main__':
    unittest.main()
